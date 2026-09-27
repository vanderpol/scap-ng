#!/usr/bin/env python3
"""Split a published SCAP 1.4 datastream into standalone per-XCCDF-rule OVAL files.

For each XCCDF Rule that references one or more OVAL definitions, this tool:
  * resolves the referenced definition ID against embedded OVAL components;
  * computes the full transitive OVAL dependency closure;
  * emits one standalone OVAL Definitions document for the XCCDF rule;
  * validates the result against the vendored SCAP 1.4 omni-schema.xsd;
  * records provenance and closure metrics.

The source signed ZIP remains authoritative. Generated files are research
artifacts and must retain provenance to the source publication.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import zipfile

from lxml import etree

OVAL_DEF_NS = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
XLINK_NS = "http://www.w3.org/1999/xlink"
OVAL_ID_RE = re.compile(r"^oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+$")
SECTION_ORDER = ("definitions", "tests", "objects", "states", "variables")


def local(tag: str) -> str:
    return etree.QName(tag).localname


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_member(name: str) -> bool:
    p = PurePosixPath(name)
    return not p.is_absolute() and ".." not in p.parts


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("_") or "unnamed"


def first_text(element, child_name: str) -> str | None:
    for child in element.iter():
        if local(child.tag) == child_name:
            text = " ".join("".join(child.itertext()).split())
            return text or None
    return None


def parse_xml_candidates(zip_path: Path):
    records = []
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir() or not safe_member(info.filename):
                continue
            # Published NIWC packages use XML datastream members, but detect by
            # content rather than filename alone.
            if PurePosixPath(info.filename).suffix.lower() not in {".xml", ".xccdf", ".oval"}:
                continue
            data = zf.read(info)
            try:
                root = etree.fromstring(data)
            except etree.XMLSyntaxError:
                continue
            records.append((info.filename, data, root))
    return records


def find_datastream(zip_path: Path):
    candidates = parse_xml_candidates(zip_path)
    ds = []
    for member, data, root in candidates:
        if local(root.tag) in {"data-stream-collection", "data-stream"}:
            ds.append((member, data, root))
    if len(ds) != 1:
        raise ValueError(
            f"{zip_path}: expected exactly one SCAP source datastream XML, found {len(ds)}"
        )
    return ds[0]


def embedded_components(datastream_root):
    components = {}
    refs = {}
    for e in datastream_root.iter():
        n = local(e.tag)
        if n == "component":
            cid = e.get("id")
            children = [x for x in e if isinstance(x.tag, str)]
            if cid and children:
                components[cid] = children[0]
        elif n == "component-ref":
            rid = e.get("id")
            href = e.get(f"{{{XLINK_NS}}}href") or e.get("href")
            if rid and href:
                refs[rid] = href.lstrip("#")
    return components, refs


def component_kind(root) -> str:
    name = local(root.tag)
    if name == "Benchmark":
        return "xccdf"
    if name == "oval_definitions":
        return "oval"
    return name


class OvalComponent:
    def __init__(self, component_id: str, root):
        self.component_id = component_id
        self.root = root
        self.sections = {}
        self.by_id = {}
        self.kind_by_id = {}
        self.source_order = {}

        seq = 0
        for section in root:
            section_name = local(section.tag)
            if section_name not in SECTION_ORDER:
                continue
            self.sections[section_name] = section
            for item in section:
                oid = item.get("id")
                if not oid:
                    continue
                if oid in self.by_id:
                    raise ValueError(f"{component_id}: duplicate OVAL id {oid}")
                self.by_id[oid] = item
                self.kind_by_id[oid] = section_name
                self.source_order[oid] = seq
                seq += 1

    def has_definition(self, definition_id: str) -> bool:
        return (
            definition_id in self.by_id
            and self.kind_by_id.get(definition_id) == "definitions"
        )

    def references_from(self, element):
        refs = set()
        unresolved_looking = set()
        for node in element.iter():
            for value in node.attrib.values():
                v = value.strip()
                if v in self.by_id:
                    refs.add(v)
                elif OVAL_ID_RE.match(v):
                    unresolved_looking.add(v)
            if node.text:
                v = node.text.strip()
                if v in self.by_id:
                    refs.add(v)
                elif OVAL_ID_RE.match(v):
                    unresolved_looking.add(v)
        return refs, unresolved_looking

    def closure(self, definition_ids: list[str]):
        wanted = set()
        unresolved = set()
        queue = list(definition_ids)
        while queue:
            oid = queue.pop(0)
            if oid in wanted:
                continue
            element = self.by_id.get(oid)
            if element is None:
                unresolved.add(oid)
                continue
            wanted.add(oid)
            refs, unresolved_looking = self.references_from(element)
            unresolved |= unresolved_looking
            for ref in sorted(refs):
                if ref not in wanted:
                    queue.append(ref)
        return wanted, unresolved


def rule_oval_refs(benchmark):
    rows = []
    for rule in benchmark.iter():
        if local(rule.tag) != "Rule":
            continue
        rule_id = rule.get("id")
        if not rule_id:
            continue
        checks = []
        for check in rule:
            if local(check.tag) != "check":
                continue
            system = check.get("system")
            for ref in check.iter():
                if local(ref.tag) != "check-content-ref":
                    continue
                name = ref.get("name")
                href = ref.get("href") or ref.get(f"{{{XLINK_NS}}}href")
                checks.append({
                    "system": system,
                    "name": name,
                    "href": href,
                })
        rows.append({
            "rule_id": rule_id,
            "title": first_text(rule, "title"),
            "checks": checks,
        })
    return rows


def merge_rule_closures(component_closures):
    """Create one standalone OVAL document from one or more component closures."""
    if not component_closures:
        raise ValueError("no OVAL closures supplied")

    first_component, _ = component_closures[0]
    source_root = first_component.root
    nsmap = dict(source_root.nsmap or {})
    root = etree.Element(source_root.tag, nsmap=nsmap)
    for k, v in source_root.attrib.items():
        root.set(k, v)

    generator = next((x for x in source_root if local(x.tag) == "generator"), None)
    if generator is None:
        raise ValueError("OVAL component has no generator")
    root.append(copy.deepcopy(generator))

    merged = {name: {} for name in SECTION_ORDER}
    order = {}
    next_order = 0

    for component, closure in component_closures:
        for oid in closure:
            kind = component.kind_by_id[oid]
            item = component.by_id[oid]
            serialized = etree.tostring(item)
            if oid in merged[kind]:
                if etree.tostring(merged[kind][oid]) != serialized:
                    raise ValueError(
                        f"conflicting duplicate OVAL id {oid} across components"
                    )
                continue
            merged[kind][oid] = copy.deepcopy(item)
            order[(kind, oid)] = next_order
            next_order += 1

    for section_name in SECTION_ORDER:
        if not merged[section_name]:
            continue
        source_section = None
        for component, _ in component_closures:
            source_section = component.sections.get(section_name)
            if source_section is not None:
                break
        if source_section is None:
            raise ValueError(f"cannot construct section {section_name}")
        section = etree.Element(source_section.tag, nsmap=source_section.nsmap)
        for k, v in source_section.attrib.items():
            section.set(k, v)
        items = sorted(
            merged[section_name].items(),
            key=lambda kv: order[(section_name, kv[0])],
        )
        for _, item in items:
            section.append(item)
        root.append(section)

    return etree.ElementTree(root), {
        name: len(merged[name]) for name in SECTION_ORDER
    }


def validate_schema(tree, schema):
    if schema.validate(tree):
        return []
    return [
        {
            "line": e.line,
            "column": e.column,
            "domain": e.domain_name,
            "type": e.type_name,
            "message": e.message,
        }
        for e in schema.error_log
    ]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("source_zip", type=Path)
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--schema", type=Path, required=True)
    ap.add_argument("--source-repository", default="niwc-atlantic/scap-content-library")
    ap.add_argument("--source-revision", required=True)
    ap.add_argument("--source-repository-path")
    ap.add_argument("--benchmark-key", required=True)
    ap.add_argument("--fail-on-unresolved", action="store_true")
    args = ap.parse_args()

    source_bytes = args.source_zip.read_bytes()
    zip_digest = sha256(source_bytes)
    member, ds_bytes, ds_root = find_datastream(args.source_zip)
    components, component_refs = embedded_components(ds_root)

    benchmarks = [
        (cid, root) for cid, root in components.items()
        if component_kind(root) == "xccdf"
    ]
    oval_components = [
        OvalComponent(cid, root) for cid, root in components.items()
        if component_kind(root) == "oval"
    ]
    if not benchmarks:
        raise ValueError("no embedded XCCDF Benchmark component found")
    if not oval_components:
        raise ValueError("no embedded OVAL Definitions component found")

    schema_doc = etree.parse(str(args.schema))
    schema = etree.XMLSchema(schema_doc)

    out = args.output_dir
    if out.exists():
        shutil.rmtree(out)
    rules_dir = out / "rules"
    rules_dir.mkdir(parents=True)

    manifest = {
        "format": "scap-ng-iteration001-rule-split-manifest-0.1",
        "benchmark_key": args.benchmark_key,
        "source": {
            "repository": args.source_repository,
            "revision": args.source_revision,
            "repository_path": args.source_repository_path,
            "zip_filename": args.source_zip.name,
            "zip_sha256": zip_digest,
            "datastream_member": member,
            "datastream_sha256": sha256(ds_bytes),
        },
        "xccdf_components": [cid for cid, _ in benchmarks],
        "oval_components": [c.component_id for c in oval_components],
        "rules": [],
        "summary": {},
    }

    stats = {
        "xccdf_rules": 0,
        "rules_with_oval": 0,
        "rules_without_oval": 0,
        "split_files": 0,
        "schema_valid": 0,
        "schema_invalid": 0,
        "unresolved_references": 0,
        "ambiguous_definition_references": 0,
    }

    for benchmark_component_id, benchmark in benchmarks:
        for row in rule_oval_refs(benchmark):
            stats["xccdf_rules"] += 1
            oval_checks = [
                c for c in row["checks"]
                if c.get("name") and OVAL_ID_RE.match(c["name"])
            ]
            if not oval_checks:
                stats["rules_without_oval"] += 1
                manifest["rules"].append({
                    "xccdf_component": benchmark_component_id,
                    "rule_id": row["rule_id"],
                    "title": row["title"],
                    "status": "no_oval_definition_reference",
                    "checks": row["checks"],
                })
                continue

            stats["rules_with_oval"] += 1
            grouped = {}
            resolution = []
            ambiguous = False

            for check in oval_checks:
                definition_id = check["name"]
                matches = [c for c in oval_components if c.has_definition(definition_id)]
                if len(matches) != 1:
                    if len(matches) > 1:
                        stats["ambiguous_definition_references"] += 1
                        ambiguous = True
                    resolution.append({
                        **check,
                        "definition_id": definition_id,
                        "match_count": len(matches),
                        "status": "unresolved" if not matches else "ambiguous",
                    })
                    continue
                component = matches[0]
                grouped.setdefault(component, []).append(definition_id)
                resolution.append({
                    **check,
                    "definition_id": definition_id,
                    "match_count": 1,
                    "status": "resolved",
                    "oval_component": component.component_id,
                })

            if ambiguous or any(r["status"] != "resolved" for r in resolution):
                manifest["rules"].append({
                    "xccdf_component": benchmark_component_id,
                    "rule_id": row["rule_id"],
                    "title": row["title"],
                    "status": "definition_resolution_error",
                    "checks": resolution,
                })
                continue

            component_closures = []
            unresolved = set()
            closure_ids = []
            for component, definition_ids in grouped.items():
                closure, missing = component.closure(sorted(set(definition_ids)))
                component_closures.append((component, closure))
                unresolved |= missing
                closure_ids.extend(sorted(closure))

            stats["unresolved_references"] += len(unresolved)
            if unresolved and args.fail_on_unresolved:
                manifest["rules"].append({
                    "xccdf_component": benchmark_component_id,
                    "rule_id": row["rule_id"],
                    "title": row["title"],
                    "status": "unresolved_oval_dependency",
                    "checks": resolution,
                    "unresolved": sorted(unresolved),
                })
                continue

            split_tree, counts = merge_rule_closures(component_closures)
            xml_bytes = etree.tostring(
                split_tree,
                encoding="UTF-8",
                xml_declaration=True,
                pretty_print=True,
            )
            # Reparse serialized bytes before schema validation so validation
            # covers the exact artifact that is written.
            exact_tree = etree.ElementTree(etree.fromstring(xml_bytes))
            schema_errors = validate_schema(exact_tree, schema)

            rule_slug = safe_name(row["rule_id"])
            rule_dir = rules_dir / rule_slug
            rule_dir.mkdir(parents=True)
            oval_path = rule_dir / "oval.xml"
            oval_path.write_bytes(xml_bytes)
            split_digest = sha256(xml_bytes)

            provenance = {
                "generated_artifact": True,
                "authoritative_source": "published_signed_niwc_scap14_zip",
                "source": manifest["source"],
                "xccdf_component": benchmark_component_id,
                "xccdf_rule_id": row["rule_id"],
                "xccdf_title": row["title"],
                "checks": resolution,
                "definition_ids": sorted({
                    c["definition_id"] for c in resolution
                    if c["status"] == "resolved"
                }),
                "oval_component_ids": sorted(c.component_id for c in grouped),
                "closure": {
                    "counts": counts,
                    "ids": sorted(set(closure_ids)),
                    "unresolved": sorted(unresolved),
                },
                "split_oval": {
                    "path": oval_path.relative_to(out).as_posix(),
                    "sha256": split_digest,
                    "bytes": len(xml_bytes),
                    "omni_schema_valid": not schema_errors,
                    "schema_errors": schema_errors,
                },
            }
            (rule_dir / "provenance.json").write_text(
                json.dumps(provenance, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )

            stats["split_files"] += 1
            if schema_errors:
                stats["schema_invalid"] += 1
                status = "schema_invalid"
            else:
                stats["schema_valid"] += 1
                status = "split_valid"

            manifest["rules"].append({
                "xccdf_component": benchmark_component_id,
                "rule_id": row["rule_id"],
                "title": row["title"],
                "status": status,
                "path": oval_path.relative_to(out).as_posix(),
                "sha256": split_digest,
                "definition_ids": provenance["definition_ids"],
                "closure_counts": counts,
                "unresolved": sorted(unresolved),
                "schema_errors": schema_errors,
            })

    manifest["summary"] = stats
    out.mkdir(parents=True, exist_ok=True)
    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(stats, indent=2, sort_keys=True))
    failures = (
        stats["schema_invalid"]
        + stats["ambiguous_definition_references"]
        + (stats["unresolved_references"] if args.fail_on_unresolved else 0)
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
