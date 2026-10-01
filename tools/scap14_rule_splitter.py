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
        if n in ("component", "extended-component"):
            cid = e.get("id")
            children = [x for x in e if isinstance(x.tag, str)]
            if cid and children:
                if cid in components and etree.tostring(components[cid]) != etree.tostring(children[0]):
                    raise ValueError(f"conflicting embedded component id: {cid}")
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

    @staticmethod
    def reference_kind(node, source: str) -> str:
        name = local(node.tag)
        if source == "definition_ref":
            return "extend_definition"
        if source == "test_ref":
            return "criterion_test"
        if source == "object_ref":
            return "object_component" if name == "object_component" else "test_object"
        if source == "state_ref":
            return "test_state" if name == "state" else "state_reference"
        if source == "var_ref":
            return "variable_reference"
        if name == "object_reference" and source == "text":
            return "set_object_reference"
        if name == "filter" and source == "text":
            return "set_filter_state"
        if name == "var_ref" and source == "text":
            return "variable_reference"
        return f"{name}:{source}"

    def references_from(self, source_id: str, element):
        refs = set()
        unresolved_looking = set()
        edges = []
        for node in element.iter():
            for attr_name, value in node.attrib.items():
                v = value.strip()
                attr = local(attr_name)
                if attr == "id":
                    continue
                if v in self.by_id:
                    refs.add(v)
                    edges.append({
                        "from": source_id,
                        "to": v,
                        "kind": self.reference_kind(node, attr),
                        "element": local(node.tag),
                        "attribute": attr,
                    })
                elif OVAL_ID_RE.match(v):
                    unresolved_looking.add(v)
                    edges.append({
                        "from": source_id,
                        "to": v,
                        "kind": self.reference_kind(node, attr),
                        "element": local(node.tag),
                        "attribute": attr,
                        "resolved": False,
                    })
            if node.text:
                v = node.text.strip()
                if v in self.by_id:
                    refs.add(v)
                    edges.append({
                        "from": source_id,
                        "to": v,
                        "kind": self.reference_kind(node, "text"),
                        "element": local(node.tag),
                        "attribute": None,
                    })
                elif OVAL_ID_RE.match(v):
                    unresolved_looking.add(v)
                    edges.append({
                        "from": source_id,
                        "to": v,
                        "kind": self.reference_kind(node, "text"),
                        "element": local(node.tag),
                        "attribute": None,
                        "resolved": False,
                    })
        # XML sometimes repeats equivalent refs. Preserve one typed edge.
        dedup = {}
        for edge in edges:
            key = (edge["from"], edge["to"], edge["kind"], edge["element"], edge["attribute"])
            dedup[key] = edge
        return refs, unresolved_looking, list(dedup.values())

    def closure(self, seed_ids: list[str]):
        wanted = set()
        unresolved = set()
        dependency_edges = []
        queue = list(seed_ids)
        while queue:
            oid = queue.pop(0)
            if oid in wanted:
                continue
            element = self.by_id.get(oid)
            if element is None:
                unresolved.add(oid)
                continue
            wanted.add(oid)
            refs, unresolved_looking, edges = self.references_from(oid, element)
            dependency_edges.extend(edges)
            unresolved |= unresolved_looking
            for ref in sorted(refs):
                if ref not in wanted:
                    queue.append(ref)

        # Fixed-point integrity: every resolved edge from a reachable node must
        # terminate inside the closure.
        escaped = sorted({
            e["to"] for e in dependency_edges
            if e.get("resolved", True) and e["from"] in wanted and e["to"] not in wanted
        })
        unresolved |= set(escaped)
        dependency_edges.sort(key=lambda e: (
            e["from"], e["to"], e["kind"], e["element"], e.get("attribute") or ""
        ))
        return wanted, unresolved, dependency_edges


def xccdf_node(element):
    out = {
        "name": local(element.tag),
        "namespace": etree.QName(element.tag).namespace or "",
    }
    if element.attrib:
        out["attributes"] = {
            etree.QName(k).localname: v for k, v in sorted(element.attrib.items())
        }
    if element.text and element.text.strip():
        out["text"] = element.text.strip()
    children = [
        xccdf_node(child) for child in element
        if isinstance(child.tag, str)
    ]
    if children:
        out["children"] = children
    return out


def effective_rule_check_nodes(rule):
    """Return XCCDF checks that participate in rule processing.

    If a Rule contains complex-check, XCCDF 1.2 processes its nested checks.
    Otherwise direct check children are candidates. This helper is used only
    for dependency seeding; the benchmark IR preserves the Boolean tree.
    """
    complex_checks=[
        child for child in rule
        if isinstance(child.tag,str) and local(child.tag)=="complex-check"
    ]
    if complex_checks:
        return [
            node
            for complex_check in complex_checks
            for node in complex_check.iter()
            if isinstance(node.tag,str) and local(node.tag)=="check"
        ]
    return [
        child for child in rule
        if isinstance(child.tag,str) and local(child.tag)=="check"
    ]


def applicability_oval_refs(benchmark):
    """Return OVAL definitions referenced by CPE applicability check-fact-ref nodes."""
    rows=[]
    for platform in benchmark.iter():
        if not isinstance(platform.tag,str) or local(platform.tag)!="platform":
            continue
        platform_id=platform.get("id")
        # XCCDF Rule/Group platform elements also use the local name "platform";
        # only CPE platform definitions contain check-fact-ref descendants.
        for ref in platform.iter():
            if not isinstance(ref.tag,str) or local(ref.tag)!="check-fact-ref":
                continue
            system=ref.get("system")
            definition_id=ref.get("id-ref")
            href=ref.get("href") or ref.get(f"{{{XLINK_NS}}}href")
            rows.append({
                "platform_id":platform_id,
                "system":system,
                "definition_id":definition_id,
                "href":href,
            })
    return rows


def cpe_dictionary_oval_refs(components):
    """Return OVAL inventory checks bound to CPE names in embedded CPE dictionaries."""
    rows=[]
    for component_id, root in components.items():
        if local(root.tag)!="cpe-list":
            continue
        for item in root.iter():
            if not isinstance(item.tag,str) or local(item.tag)!="cpe-item":
                continue
            cpe_name=item.get("name")
            if not cpe_name:
                continue
            for check in item:
                if not isinstance(check.tag,str) or local(check.tag)!="check":
                    continue
                system=check.get("system")
                href=check.get("href") or check.get(f"{{{XLINK_NS}}}href")
                definition_id=" ".join("".join(check.itertext()).split()) or check.get("name")
                rows.append({
                    "source_kind":"cpe_dictionary",
                    "cpe_name":cpe_name,
                    "cpe_component":component_id,
                    "system":system,
                    "definition_id":definition_id,
                    "href":href,
                })
    return rows


def rule_oval_refs(benchmark):
    values = {
        e.get("id"): xccdf_node(e)
        for e in benchmark.iter()
        if local(e.tag) == "Value" and e.get("id")
    }
    rows = []
    for rule in benchmark.iter():
        if local(rule.tag) != "Rule":
            continue
        rule_id = rule.get("id")
        if not rule_id:
            continue
        checks = []
        for check in effective_rule_check_nodes(rule):
            system = check.get("system")
            exports = []
            for child in check.iter():
                if local(child.tag) == "check-export":
                    value_id = child.get("value-id")
                    exports.append({
                        "export_name": child.get("export-name"),
                        "value_id": value_id,
                        "value_definition": values.get(value_id),
                    })
            for ref in check.iter():
                if local(ref.tag) != "check-content-ref":
                    continue
                name = ref.get("name")
                href = ref.get("href") or ref.get(f"{{{XLINK_NS}}}href")
                checks.append({
                    "system": system,
                    "selector": check.get("selector"),
                    "negate": check.get("negate"),
                    "multi_check": check.get("multi-check"),
                    "name": name,
                    "href": href,
                    "exports": exports,
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

    # Some published ZIPs carry applicability/inventory OVAL as standalone XML
    # members referenced by the XCCDF/CPE dictionary rather than as embedded
    # datastream components.  They are still authoritative package members and
    # must participate in source graph resolution.  Avoid double-indexing an
    # identical OVAL document when the ZIP also embeds the same component.
    embedded_oval = [
        (cid, root) for cid, root in components.items()
        if component_kind(root) == "oval"
    ]
    seen_oval_documents = {
        sha256(etree.tostring(root, encoding="UTF-8"))
        for _, root in embedded_oval
    }
    standalone_oval = []
    for member_name, _, root in parse_xml_candidates(args.source_zip):
        if component_kind(root) != "oval":
            continue
        digest = sha256(etree.tostring(root, encoding="UTF-8"))
        if digest in seen_oval_documents:
            continue
        seen_oval_documents.add(digest)
        standalone_oval.append((f"zip-member:{member_name}", root))

    oval_components = [
        OvalComponent(cid, root) for cid, root in embedded_oval + standalone_oval
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
        "applicability_check_fact_refs": 0,
        "applicability_oval_definition_refs": 0,
        "applicability_unique_oval_definitions": 0,
        "applicability_unresolved_references": 0,
        "applicability_schema_invalid": 0,
        "cpe_inventory_refs": 0,
        "cpe_inventory_split_valid": 0,
        "cpe_inventory_unresolved": 0,
        "cpe_inventory_schema_invalid": 0,
    }

    # CPE applicability uses the same OVAL language as Rule checks, but those
    # definitions are not necessarily reachable from any Rule check. Build one
    # standalone fixed-point OVAL closure so applicability is executable in NG.
    applicability_refs=[]
    for benchmark_component_id, benchmark in benchmarks:
        for ref in applicability_oval_refs(benchmark):
            applicability_refs.append({
                **ref,
                "source_kind":"cpe_platform_expression",
                "xccdf_component":benchmark_component_id,
            })
    stats["applicability_check_fact_refs"]=len(applicability_refs)
    oval_app_refs=[
        ref for ref in applicability_refs
        if ref.get("system")==OVAL_DEF_NS
        and ref.get("definition_id")
        and OVAL_ID_RE.match(ref["definition_id"])
    ]
    stats["applicability_oval_definition_refs"]=len(oval_app_refs)
    stats["applicability_unique_oval_definitions"]=len({
        ref["definition_id"] for ref in oval_app_refs
    })
    manifest["applicability"]={
        "references":applicability_refs,
        "status":"not_present" if not oval_app_refs else "pending",
    }

    if oval_app_refs:
        grouped={}
        resolved=[]
        applicability_errors=[]
        for ref in oval_app_refs:
            definition_id=ref["definition_id"]
            matches=[c for c in oval_components if c.has_definition(definition_id)]
            if len(matches)!=1:
                applicability_errors.append({
                    **ref,
                    "match_count":len(matches),
                    "status":"unresolved" if not matches else "ambiguous",
                })
                continue
            component=matches[0]
            grouped.setdefault(component,set()).add(definition_id)
            resolved.append({
                **ref,
                "match_count":1,
                "status":"resolved",
                "oval_component":component.component_id,
            })

        component_closures=[]
        unresolved=set()
        dependency_edges=[]
        closure_ids=[]
        if not applicability_errors:
            for component,definition_ids in grouped.items():
                closure,missing,edges=component.closure(sorted(definition_ids))
                component_closures.append((component,closure))
                unresolved |= missing
                closure_ids.extend(sorted(closure))
                dependency_edges.extend({
                    **edge,
                    "oval_component":component.component_id,
                } for edge in edges)

        stats["applicability_unresolved_references"]=(
            len(applicability_errors)+len(unresolved)
        )
        if applicability_errors or unresolved:
            manifest["applicability"]={
                "references":resolved+applicability_errors,
                "status":"resolution_error",
                "unresolved":sorted(unresolved),
            }
        else:
            applicability_tree,counts=merge_rule_closures(component_closures)
            xml_bytes=etree.tostring(
                applicability_tree,
                encoding="UTF-8",
                xml_declaration=True,
                pretty_print=True,
            )
            exact_tree=etree.ElementTree(etree.fromstring(xml_bytes))
            schema_errors=validate_schema(exact_tree,schema)
            app_dir=out/"applicability"
            app_dir.mkdir(parents=True,exist_ok=True)
            oval_path=app_dir/"oval.xml"
            oval_path.write_bytes(xml_bytes)
            provenance={
                "generated_artifact":True,
                "authoritative_source":"published_signed_niwc_scap14_zip",
                "kind":"xccdf_cpe_applicability",
                "source":manifest["source"],
                "xccdf_rule_id":None,
                "xccdf_title":"CPE applicability definitions",
                "xccdf_component":None,
                "checks":[
                    {
                        "system":ref.get("system"),
                        "href":ref.get("href"),
                        "name":ref.get("definition_id"),
                        "definition_id":ref.get("definition_id"),
                        "platform_id":ref.get("platform_id"),
                        "cpe_name":ref.get("cpe_name"),
                        "source_kind":ref.get("source_kind"),
                        "cpe_component":ref.get("cpe_component"),
                        "status":ref.get("status"),
                        "oval_component":ref.get("oval_component"),
                        "exports":[],
                    }
                    for ref in resolved
                ],
                "check_exports":[],
                "definition_ids":sorted({
                    ref["definition_id"] for ref in resolved
                }),
                "oval_component_ids":sorted(c.component_id for c in grouped),
                "closure":{
                    "counts":counts,
                    "ids":sorted(set(closure_ids)),
                    "unresolved":[],
                    "dependency_edges":dependency_edges,
                    "fixed_point_complete":True,
                },
                "split_oval":{
                    "path":oval_path.relative_to(out).as_posix(),
                    "sha256":sha256(xml_bytes),
                    "bytes":len(xml_bytes),
                    "omni_schema_valid":not schema_errors,
                    "schema_errors":schema_errors,
                },
            }
            (app_dir/"provenance.json").write_text(
                json.dumps(provenance,indent=2,sort_keys=True)+"\n",
                encoding="utf-8",
            )
            if schema_errors:
                stats["applicability_schema_invalid"]=1
            manifest["applicability"]={
                "references":resolved,
                "status":"schema_invalid" if schema_errors else "split_valid",
                "path":oval_path.relative_to(out).as_posix(),
                "sha256":sha256(xml_bytes),
                "definition_ids":provenance["definition_ids"],
                "closure_counts":counts,
                "dependency_edge_count":len(dependency_edges),
                "schema_errors":schema_errors,
            }

    # CPE dictionary inventory checks are deliberately split per product.
    # They are descriptive platform/product inventory Assessments, not part of
    # the CPE/XCCDF applicability Assessment. Keeping them separate avoids
    # cross-component OVAL ID collisions and guarantees inventory reporting
    # cannot alter applicability truth.
    cpe_inventory=[]
    cpe_refs=cpe_dictionary_oval_refs(components)
    stats["cpe_inventory_refs"]=len(cpe_refs)
    for ordinal,ref in enumerate(cpe_refs,1):
        entry={**ref}
        definition_id=ref.get("definition_id")
        if (
            ref.get("system")!=OVAL_DEF_NS
            or not definition_id
            or not OVAL_ID_RE.match(definition_id)
        ):
            entry["status"]="unsupported_reference"
            stats["cpe_inventory_unresolved"]+=1
            cpe_inventory.append(entry)
            continue

        matches=[comp for comp in oval_components if comp.has_definition(definition_id)]
        if len(matches)!=1:
            entry["status"]="unresolved" if not matches else "ambiguous"
            entry["match_count"]=len(matches)
            stats["cpe_inventory_unresolved"]+=1
            cpe_inventory.append(entry)
            continue

        component=matches[0]
        closure,unresolved,edges=component.closure([definition_id])
        if unresolved:
            entry["status"]="resolution_error"
            entry["unresolved"]=sorted(unresolved)
            stats["cpe_inventory_unresolved"]+=1
            cpe_inventory.append(entry)
            continue

        inventory_tree,counts=merge_rule_closures([(component,closure)])
        xml_bytes=etree.tostring(
            inventory_tree,
            encoding="UTF-8",
            xml_declaration=True,
            pretty_print=True,
        )
        exact_tree=etree.ElementTree(etree.fromstring(xml_bytes))
        schema_errors=validate_schema(exact_tree,schema)
        inv_id=f"{ordinal:04d}-{safe_name(ref.get('cpe_name') or definition_id)}"
        inv_dir=out/"platform-inventory"/inv_id
        inv_dir.mkdir(parents=True,exist_ok=True)
        oval_path=inv_dir/"oval.xml"
        oval_path.write_bytes(xml_bytes)

        provenance={
            "generated_artifact":True,
            "authoritative_source":"published_signed_niwc_scap14_zip",
            "kind":"cpe_product_inventory",
            "source":manifest["source"],
            "cpe_name":ref.get("cpe_name"),
            "cpe_component":ref.get("cpe_component"),
            "definition_id":definition_id,
            "oval_component":component.component_id,
            "closure":{
                "counts":counts,
                "ids":sorted(closure),
                "unresolved":[],
                "dependency_edges":edges,
                "fixed_point_complete":True,
            },
            "split_oval":{
                "path":oval_path.relative_to(out).as_posix(),
                "sha256":sha256(xml_bytes),
                "bytes":len(xml_bytes),
                "omni_schema_valid":not schema_errors,
                "schema_errors":schema_errors,
            },
        }
        (inv_dir/"provenance.json").write_text(
            json.dumps(provenance,indent=2,sort_keys=True)+"\n",
            encoding="utf-8",
        )
        entry.update({
            "status":"schema_invalid" if schema_errors else "split_valid",
            "match_count":1,
            "oval_component":component.component_id,
            "path":oval_path.relative_to(out).as_posix(),
            "sha256":sha256(xml_bytes),
            "closure_counts":counts,
            "dependency_edge_count":len(edges),
            "schema_errors":schema_errors,
        })
        if schema_errors:
            stats["cpe_inventory_schema_invalid"]+=1
        else:
            stats["cpe_inventory_split_valid"]+=1
        cpe_inventory.append(entry)

    manifest["cpe_inventory"]=cpe_inventory

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
                entry = grouped.setdefault(component, {
                    "definition_ids": [],
                    "export_variable_ids": [],
                    "unresolved_export_names": [],
                })
                entry["definition_ids"].append(definition_id)
                for export in check.get("exports", []):
                    export_name = export.get("export_name")
                    if not export_name:
                        continue
                    if (
                        export_name in component.by_id
                        and component.kind_by_id.get(export_name) == "variables"
                    ):
                        entry["export_variable_ids"].append(export_name)
                    elif OVAL_ID_RE.match(export_name):
                        entry["unresolved_export_names"].append(export_name)
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
            dependency_edges = []
            xccdf_export_edges = []
            unresolved_exports = set()
            export_variable_ids = set()
            for component, group in grouped.items():
                definition_ids = sorted(set(group["definition_ids"]))
                exported = sorted(set(group["export_variable_ids"]))
                unresolved_exports |= set(group["unresolved_export_names"])
                export_variable_ids |= set(exported)
                seeds = definition_ids + exported
                closure, missing, edges = component.closure(seeds)
                component_closures.append((component, closure))
                unresolved |= missing
                closure_ids.extend(sorted(closure))
                dependency_edges.extend({
                    **edge,
                    "oval_component": component.component_id,
                } for edge in edges)
                for export_id in exported:
                    xccdf_export_edges.append({
                        "from": row["rule_id"],
                        "to": export_id,
                        "kind": "xccdf_check_export",
                        "oval_component": component.component_id,
                    })
            unresolved |= unresolved_exports
            dependency_edges.extend(xccdf_export_edges)

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
                "external_variable_ids_from_check_export": sorted(export_variable_ids),
                "check_exports": [
                    export
                    for check in resolution
                    for export in check.get("exports", [])
                ],
                "closure": {
                    "counts": counts,
                    "ids": sorted(set(closure_ids)),
                    "unresolved": sorted(unresolved),
                    "dependency_edges": dependency_edges,
                    "fixed_point_complete": not unresolved,
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
                "dependency_edge_count": len(dependency_edges),
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
        + stats["applicability_schema_invalid"]
        + (
            stats["unresolved_references"]
            + stats["applicability_unresolved_references"]
            if args.fail_on_unresolved else 0
        )
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
