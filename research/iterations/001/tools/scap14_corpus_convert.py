#!/usr/bin/env python3
"""SCAP 1.4 corpus conversion research harness.

This tool is deliberately conservative. It provides:
  * safe recursive corpus discovery (XML and ZIP-contained XML);
  * immutable SHA-256 source identification;
  * SCAP component classification;
  * lossless XML-to-semantic-tree capture for accounting;
  * XCCDF rule/profile inventory;
  * OVAL definition/test/object/state/variable inventory;
  * construct-level feature accounting;
  * migration-status scaffolding;
  * machine-readable corpus reports.

It is the framework for native translators, not a claim that all discovered
constructs are already natively converted.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile
import xml.etree.ElementTree as ET

try:
    import yaml
except ImportError:
    yaml = None

KNOWN_EXTENSIONS = {".xml", ".xccdf", ".oval"}
MIGRATION_STATUSES = {
    "exact_native",
    "exact_normalized",
    "legacy_compatible",
    "requires_review",
    "unsupported",
}

SCAP_NAMESPACE_HINTS = {
    "data-stream": "datastream",
    "Benchmark": "xccdf",
    "oval_definitions": "oval-definitions",
    "oval_results": "oval-results",
    "oval_system_characteristics": "oval-system-characteristics",
    "oval_variables": "oval-variables",
    "ocil": "ocil",
    "cpe-list": "cpe-dictionary",
    "platform-specification": "cpe-language",
    "asset-report-collection": "arf",
}


def local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def namespace(tag: str) -> str:
    if tag.startswith("{"):
        return tag[1:].split("}", 1)[0]
    return ""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized_text(text: str | None) -> str | None:
    if text is None:
        return None
    value = " ".join(text.split())
    return value or None


def xml_tree(element: ET.Element) -> dict:
    """Lossless-enough semantic accounting tree.

    This is not canonical SCAP-NG. It preserves every element name, namespace,
    attribute, normalized text value, and child in source order so unsupported
    content remains visible to migration accounting.
    """
    node = {
        "name": local(element.tag),
        "namespace": namespace(element.tag),
    }
    if element.attrib:
        node["attributes"] = {
            str(k): v for k, v in sorted(element.attrib.items())
        }
    text = normalized_text(element.text)
    if text is not None:
        node["text"] = text
    children = [xml_tree(child) for child in list(element)]
    if children:
        node["children"] = children
    return node


def classify(root: ET.Element) -> str:
    name = local(root.tag)
    if name in SCAP_NAMESPACE_HINTS:
        return SCAP_NAMESPACE_HINTS[name]
    ns = namespace(root.tag).lower()
    if "xccdf" in ns:
        return "xccdf"
    if "oval" in ns:
        return "oval-other"
    if "ocil" in ns:
        return "ocil"
    if "cpe" in ns:
        return "cpe-other"
    if "scap" in ns or "source/1.2" in ns or "source/1.3" in ns:
        return "datastream-other"
    return "unknown-xml"


def first_text(element: ET.Element, child_name: str) -> str | None:
    for child in element.iter():
        if local(child.tag) == child_name:
            return normalized_text("".join(child.itertext()))
    return None


def inventory_xccdf(root: ET.Element) -> dict:
    rules = []
    profiles = []
    for e in root.iter():
        n = local(e.tag)
        if n == "Rule":
            checks = []
            references = []
            for child in e:
                cn = local(child.tag)
                if cn == "check":
                    hrefs = []
                    for sub in child.iter():
                        if local(sub.tag) in {"check-content-ref", "check-export"}:
                            hrefs.append({
                                "element": local(sub.tag),
                                "attributes": dict(sub.attrib),
                            })
                    checks.append({
                        "system": child.attrib.get("system"),
                        "selector": child.attrib.get("selector"),
                        "references": hrefs,
                    })
                elif cn == "reference":
                    references.append({
                        "href": child.attrib.get("href"),
                        "text": normalized_text("".join(child.itertext())),
                    })
            rules.append({
                "id": e.attrib.get("id"),
                "severity": e.attrib.get("severity"),
                "weight": e.attrib.get("weight"),
                "title": first_text(e, "title"),
                "description": first_text(e, "description"),
                "check": first_text(e, "check-content"),
                "fix": first_text(e, "fixtext"),
                "checks": checks,
                "references": references,
                "migration_status": "requires_review",
            })
        elif n == "Profile":
            selected = []
            values = []
            for child in e:
                cn = local(child.tag)
                if cn == "select":
                    selected.append(dict(child.attrib))
                elif cn in {"set-value", "refine-value", "refine-rule"}:
                    values.append({
                        "element": cn,
                        "attributes": dict(child.attrib),
                        "text": normalized_text("".join(child.itertext())),
                    })
            profiles.append({
                "id": e.attrib.get("id"),
                "title": first_text(e, "title"),
                "selected": selected,
                "tailoring": values,
            })
    return {
        "benchmark": {
            "id": root.attrib.get("id"),
            "title": first_text(root, "title"),
            "version": first_text(root, "version"),
        },
        "rules": rules,
        "profiles": profiles,
    }


def oval_feature_inventory(root: ET.Element) -> dict:
    counts: dict[str, int] = {}
    attrs: dict[str, dict[str, int]] = {}
    interesting_attrs = {
        "operator", "negate", "check", "check_existence", "var_check",
        "entity_check", "operation", "datatype", "mask",
        "recurse_direction", "max_depth",
    }
    for e in root.iter():
        name = local(e.tag)
        counts[name] = counts.get(name, 0) + 1
        for attr, value in e.attrib.items():
            attr_local = local(attr)
            if attr_local in interesting_attrs:
                attrs.setdefault(attr_local, {})
                attrs[attr_local][value] = attrs[attr_local].get(value, 0) + 1
    return {
        "elements": dict(sorted(counts.items())),
        "attributes": attrs,
    }


def inventory_oval(root: ET.Element, deprecated_tests: dict[str, dict] | None = None) -> dict:
    deprecated_tests = deprecated_tests or {}
    definitions = []
    tests = []
    objects = []
    states = []
    variables = []

    test_elements = {}
    for e in root.iter():
        name = local(e.tag)
        if name.endswith("_test") and e.attrib.get("id"):
            test_elements[e.attrib["id"]] = e

    for e in root.iter():
        name = local(e.tag)
        if name == "definition":
            deprecated_refs = []
            for node in e.iter():
                test_ref = node.attrib.get("test_ref")
                if not test_ref:
                    continue
                test_element = test_elements.get(test_ref)
                if test_element is None:
                    continue
                qname = f"{namespace(test_element.tag)}#{local(test_element.tag)}"
                if qname in deprecated_tests:
                    deprecated_refs.append({
                        "test_ref": test_ref,
                        "qualified_type": qname,
                        "replacement_evidence": deprecated_tests[qname].get("deprecation_evidence"),
                    })
            definition = {
                "id": e.attrib.get("id"),
                "class": e.attrib.get("class"),
                "version": e.attrib.get("version"),
                "title": first_text(e, "title"),
                "description": first_text(e, "description"),
                "criteria": [
                    xml_tree(c) for c in list(e) if local(c.tag) == "criteria"
                ],
                "migration_status": "unsupported" if deprecated_refs else "requires_review",
            }
            if deprecated_refs:
                definition["conversion_error"] = {
                    "code": "deprecated_oval_test",
                    "message": (
                        "SCAP-NG does not support deprecated OVAL tests. "
                        "Update the SCAP 1.4 source to a supported OVAL test before conversion."
                    ),
                    "deprecated_tests": deprecated_refs,
                }
            definitions.append(definition)
        elif name.endswith("_test"):
            qname = f"{namespace(e.tag)}#{name}"
            tests.append({
                "type": name,
                "qualified_type": qname,
                "id": e.attrib.get("id"),
                "attributes": dict(e.attrib),
                "deprecated": qname in deprecated_tests,
                "deprecation_evidence": deprecated_tests.get(qname, {}).get("deprecation_evidence"),
            })
        elif name.endswith("_object"):
            objects.append({
                "type": name,
                "id": e.attrib.get("id"),
                "attributes": dict(e.attrib),
            })
        elif name.endswith("_state"):
            states.append({
                "type": name,
                "id": e.attrib.get("id"),
                "attributes": dict(e.attrib),
            })
        elif name.endswith("_variable"):
            variables.append({
                "type": name,
                "id": e.attrib.get("id"),
                "attributes": dict(e.attrib),
            })

    return {
        "definitions": definitions,
        "tests": tests,
        "objects": objects,
        "states": states,
        "variables": variables,
        "features": oval_feature_inventory(root),
    }


def embedded_datastream_components(root: ET.Element) -> list[tuple[str, bytes]]:
    found = []
    for component in root.iter():
        if local(component.tag) != "component":
            continue
        cid = component.attrib.get("id", "component")
        children = list(component)
        if not children:
            continue
        payload = ET.tostring(children[0], encoding="utf-8")
        found.append((cid, payload))
    return found


def parse_xml(
    label: str,
    data: bytes,
    parent: str | None = None,
    deprecated_tests: dict[str, dict] | None = None,
) -> list[dict]:
    digest = sha256(data)
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return [{
            "source": label,
            "parent": parent,
            "sha256": digest,
            "kind": "parse-error",
            "ingest_status": "error",
            "error": str(exc),
        }]

    kind = classify(root)
    record = {
        "source": label,
        "parent": parent,
        "sha256": digest,
        "kind": kind,
        "root": {"name": local(root.tag), "namespace": namespace(root.tag)},
        "ingest_status": "captured",
        "migration_status": "requires_review",
        "semantic_tree": xml_tree(root),
    }

    if kind == "xccdf":
        record["inventory"] = inventory_xccdf(root)
    elif kind == "oval-definitions":
        record["inventory"] = inventory_oval(root, deprecated_tests)

    records = [record]
    if kind.startswith("datastream"):
        for cid, payload in embedded_datastream_components(root):
            records.extend(parse_xml(
                f"{label}#component:{cid}",
                payload,
                parent=label,
                deprecated_tests=deprecated_tests,
            ))
    return records


def safe_zip_member(name: str) -> bool:
    path = PurePosixPath(name)
    if path.is_absolute():
        return False
    return ".." not in path.parts


def discover_file(path: Path, deprecated_tests: dict[str, dict] | None = None) -> list[dict]:
    data = path.read_bytes()
    if zipfile.is_zipfile(io.BytesIO(data)):
        records = [{
            "source": str(path),
            "sha256": sha256(data),
            "kind": "zip",
            "ingest_status": "captured",
            "migration_status": "container",
        }]
        with zipfile.ZipFile(io.BytesIO(data)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                if not safe_zip_member(info.filename):
                    records.append({
                        "source": f"{path}!{info.filename}",
                        "kind": "unsafe-zip-member",
                        "ingest_status": "error",
                    })
                    continue
                if PurePosixPath(info.filename).suffix.lower() not in KNOWN_EXTENSIONS:
                    continue
                try:
                    payload = zf.read(info)
                except Exception as exc:
                    records.append({
                        "source": f"{path}!{info.filename}",
                        "kind": "zip-read-error",
                        "ingest_status": "error",
                        "error": str(exc),
                    })
                    continue
                records.extend(parse_xml(
                    f"{path}!{info.filename}",
                    payload,
                    parent=str(path),
                    deprecated_tests=deprecated_tests,
                ))
        return records

    if path.suffix.lower() in KNOWN_EXTENSIONS:
        return parse_xml(str(path), data, deprecated_tests=deprecated_tests)
    return []


def discover(inputs: list[Path]) -> list[Path]:
    files = []
    for item in inputs:
        if item.is_file():
            files.append(item)
        elif item.is_dir():
            files.extend(
                p for p in item.rglob("*")
                if p.is_file() and (
                    p.suffix.lower() in KNOWN_EXTENSIONS
                    or p.suffix.lower() == ".zip"
                )
            )
        else:
            raise FileNotFoundError(item)
    return sorted(set(files))


def summary(records: list[dict]) -> dict:
    by_kind: dict[str, int] = {}
    by_status: dict[str, int] = {}
    xccdf_rules = 0
    oval_definitions = 0
    errors = []
    deprecated_oval_definition_blockers = 0
    deprecated_oval_test_types: dict[str, int] = {}

    for r in records:
        kind = r.get("kind", "unknown")
        by_kind[kind] = by_kind.get(kind, 0) + 1
        status = r.get("migration_status")
        if status:
            by_status[status] = by_status.get(status, 0) + 1
        if r.get("ingest_status") == "error":
            errors.append({"source": r.get("source"), "error": r.get("error"), "kind": kind})

        inv = r.get("inventory", {})
        if kind == "xccdf":
            xccdf_rules += len(inv.get("rules", []))
        elif kind == "oval-definitions":
            oval_definitions += len(inv.get("definitions", []))
            for definition in inv.get("definitions", []):
                error = definition.get("conversion_error", {})
                if error.get("code") == "deprecated_oval_test":
                    deprecated_oval_definition_blockers += 1
                    for test in error.get("deprecated_tests", []):
                        qname = test.get("qualified_type", "unknown")
                        deprecated_oval_test_types[qname] = deprecated_oval_test_types.get(qname, 0) + 1

    return {
        "documents": len(records),
        "by_kind": dict(sorted(by_kind.items())),
        "migration_status": dict(sorted(by_status.items())),
        "xccdf_rules": xccdf_rules,
        "oval_definitions": oval_definitions,
        "ingest_errors": errors,
        "deprecated_oval_definition_blockers": deprecated_oval_definition_blockers,
        "deprecated_oval_test_types": dict(sorted(deprecated_oval_test_types.items())),
    }


def gate(name: str, records: list[dict]) -> list[str]:
    failures = []
    if name in {"ingest", "native"}:
        for r in records:
            if r.get("ingest_status") == "error":
                failures.append(f"ingest error: {r.get('source')}: {r.get('error', r.get('kind'))}")
            if r.get("kind") == "unknown-xml":
                failures.append(f"unknown XML root: {r.get('source')}")

    if name == "native":
        for r in records:
            if r.get("kind") in {"xccdf", "oval-definitions"}:
                inv = r.get("inventory", {})
                candidates = []
                if r["kind"] == "xccdf":
                    candidates = inv.get("rules", [])
                else:
                    candidates = inv.get("definitions", [])
                for item in candidates:
                    if item.get("migration_status") not in {"exact_native", "exact_normalized"}:
                        failures.append(
                            f"native gate: {r.get('source')} :: "
                            f"{item.get('id')} = {item.get('migration_status')}"
                        )
    return failures


def load_deprecated_tests(path: Path | None) -> dict[str, dict]:
    if path is None:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        f'{row.get("namespace","")}#{row.get("name","")}': row
        for row in data.get("test_elements", [])
        if row.get("deprecated")
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--gate", choices=["none", "ingest", "native"], default="none")
    default_catalog = Path(__file__).resolve().parent.parent / "generated" / "oval-schema-semantic-catalog.json"
    parser.add_argument(
        "--oval-schema-catalog",
        type=Path,
        default=default_catalog if default_catalog.exists() else None,
        help="Schema-derived OVAL catalog used to reject deprecated OVAL tests.",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    deprecated_tests = load_deprecated_tests(args.oval_schema_catalog)
    source_files = discover(args.inputs)
    records = []
    for path in source_files:
        records.extend(discover_file(path, deprecated_tests=deprecated_tests))

    report = {
        "tool": "scap14_corpus_convert.py",
        "prototype": True,
        "source_files": [str(p) for p in source_files],
        "summary": summary(records),
        "documents": records,
        "deprecated_oval_test_policy": {
            "supported_in_scap_ng": False,
            "catalog": str(args.oval_schema_catalog) if args.oval_schema_catalog else None,
            "deprecated_test_types_known": len(deprecated_tests),
            "conversion_behavior": (
                "Definitions referencing deprecated OVAL tests are marked unsupported "
                "with error code deprecated_oval_test. Source content must be updated "
                "before SCAP-NG conversion."
            ),
        },
    }

    (args.output_dir / "corpus-report.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    failures = gate(args.gate, records)
    gate_report = {
        "gate": args.gate,
        "passed": not failures,
        "failures": failures,
    }
    (args.output_dir / "gate-report.json").write_text(
        json.dumps(gate_report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    if failures:
        for failure in failures[:100]:
            print(f"ERROR: {failure}", file=sys.stderr)
        if len(failures) > 100:
            print(f"ERROR: {len(failures)-100} additional failures omitted", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
