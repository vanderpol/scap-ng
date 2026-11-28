#!/usr/bin/env python3
"""Crosswalk pinned OVAL declarations, mappings and Self-Assertion source."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))

from audit_oval_language import BASE, Grammar, PIN, X

SELF_ASSERTION_PIN = "d91e6ba33841e3202dc27d3e0d469a7abd939b16"
SELF_ASSERTION_PATH = "SCAP_1.4/OVAL_Test_Content"
OUTPUT = ROOT / "conformance/oval-source-coverage.json"


def require_pin(repository, expected):
    commit = subprocess.check_output(
        ["git", "-C", str(repository), "rev-parse", "HEAD"], text=True,
    ).strip()
    if commit != expected:
        raise ValueError(f"{repository}: {commit} differs from {expected}")


def archive_xml(name, data):
    # Read members in memory without materializing paths, links or permissions.
    if name.endswith(".zip"):
        with zipfile.ZipFile(BytesIO(data)) as archive:
            for member in sorted(archive.infolist(), key=lambda item: item.filename):
                if not member.is_dir() and member.filename.lower().endswith(".xml"):
                    yield member.filename, archive.read(member)
    else:
        with tarfile.open(fileobj=BytesIO(data), mode="r:*") as archive:
            for member in sorted(archive.getmembers(), key=lambda item: item.name):
                if member.isfile() and member.name.lower().endswith(".xml"):
                    with archive.extractfile(member) as stream:
                        yield member.name, stream.read()


def scan_xml(data):
    document = ET.fromstring(data)
    record = {"sha256": sha256(data).hexdigest(), "root": document.tag}
    witnesses = []
    if document.tag == f"{{{BASE}}}oval_definitions":
        record["ids"] = {}
        for section in ("definitions", "tests", "objects", "states", "variables"):
            record["ids"][section] = sorted(
                element.attrib["id"] for element in document.findall(f"{{{BASE}}}{section}/*")
            )
        for test in document.findall(f"{{{BASE}}}tests/*"):
            witnesses.append((test.tag, test.attrib["id"]))
    return record, witnesses


def self_assertion(repository):
    require_pin(repository, SELF_ASSERTION_PIN)
    paths = subprocess.check_output([
        "git", "-C", str(repository), "ls-tree", "-r", "--name-only",
        SELF_ASSERTION_PIN, "--", SELF_ASSERTION_PATH,
    ], text=True).splitlines()
    documents, archives = {}, {}
    witnesses = defaultdict(list)
    for path in paths:
        name = path.removeprefix(SELF_ASSERTION_PATH + "/")
        if not name.endswith((".xml", ".zip", ".tarz")):
            continue
        data = subprocess.check_output(
            ["git", "-C", str(repository), "show", f"{SELF_ASSERTION_PIN}:{path}"],
        )
        if name.endswith(".xml"):
            sources = [(name, data)]
        else:
            members = list(archive_xml(name, data))
            archives[name] = {
                "sha256": sha256(data).hexdigest(),
                "xml_members": [member for member, _ in members],
            }
            sources = [(f"{name}!/{member}", raw) for member, raw in members]
        for location, raw in sources:
            if location in documents:
                raise ValueError(f"Duplicate XML location: {location}")
            document, tests = scan_xml(raw)
            documents[location] = document
            for tag, test_id in tests:
                witnesses[tag].append({"file": location, "id": test_id})
    return documents, archives, witnesses


def mappings(root):
    by_source = defaultdict(list)
    for path in sorted((root / "schema/capability-mappings").glob("*/*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        source = record["source"]
        by_source[f"{{{source['namespace']}}}{source['test']}"].append({
            "capability": record["capability"],
            "status": path.parent.name,
            "path": path.relative_to(root).as_posix(),
        })
    return by_source


def build(oval, assertion, oval6):
    # Derive the family denominator before touching any assertion content.
    require_pin(oval, PIN)
    grammar = Grammar(oval / "oval-schemas")
    by_source = mappings(ROOT)
    source_tests = {}
    for (namespace, kind, name), (filename, node) in sorted(grammar.globals.items()):
        if kind != "element" or grammar.resolve(filename, node.get("substitutionGroup")) != (BASE, "test"):
            continue
        tag = f"{{{namespace}}}{name}"
        source_tests[tag] = {
            "declaration": filename,
            "deprecations": grammar.describe(filename, node)["deprecations"],
            "mappings": by_source.get(tag, []),
        }

    crosswalk = json.loads((ROOT / "proposed/issue86-esx-oval6/capability-crosswalk.json").read_text())
    v6_pin = crosswalk["source"]["commit"]
    require_pin(oval6, v6_pin)
    for filename, expected in crosswalk["source"]["schema_files_sha256"].items():
        data = (oval6 / "oval-schemas" / filename).read_bytes()
        if sha256(data).hexdigest() != expected:
            raise ValueError(f"Modified OVAL 6.0 source: {filename}")
    esx_defs = ET.parse(oval6 / "oval-schemas/esx-definitions-schema.xsd").getroot()
    v6_ns = crosswalk["source"]["definitions_namespace"]
    v6_names = {node.attrib["name"] for node in esx_defs.findall(f"{X}element")
                if node.get("substitutionGroup", "").endswith(":test")}
    v6_tests = {}
    for family in crosswalk["families"]:
        name = family["source"]["test"]
        if name not in v6_names:
            raise ValueError(f"Missing OVAL 6.0 XS declaration: {name}")
        tag = f"{{{v6_ns}}}{name}"
        matches = by_source.get(tag, [])
        v6_tests[tag] = {
            "capability": family["capability"],
            "status": matches[0]["status"] if matches else "proposed",
            "mappings": matches,
        }
    if {tag.rsplit("}", 1)[-1] for tag in v6_tests} != v6_names:
        raise ValueError("OVAL 6.0 ESXi crosswalk and XSD Test families differ")

    documents, archives, witnesses = self_assertion(assertion)
    counts = Counter()
    for tag, row in source_tests.items():
        row["self_assertion"] = witnesses.get(tag, [])
        row["status"] = "deprecated" if row["deprecations"] else (
            "supported" if row["mappings"] else "unmapped"
        )
        counts[row["status"]] += 1
        counts[f"{row['status']}_with_source_content"] += bool(row["self_assertion"])

    source_capabilities = {
        entry["capability"]
        for row in source_tests.values() for entry in row["mappings"]
    }
    assertion_capabilities = {
        entry["capability"] for row in source_tests.values() if row["self_assertion"]
        for entry in row["mappings"]
    }
    recognized = source_tests.keys() | v6_tests.keys()
    if unmatched := by_source.keys() - recognized:
        raise ValueError(f"Mappings without source XSD declaration: {sorted(unmatched)}")

    return {
        "format": "scap-ng-oval-source-coverage-1",
        "qualification": "Source declaration and XML Test identity only. "
                         "Presence does not qualify behavior, conversion or execution.",
        "pins": {"oval_5_12_3": PIN, "oval_6_0": v6_pin, "self_assertion": SELF_ASSERTION_PIN},
        "schema_files_sha256": {file: entry["sha256"] for file, entry in grammar.files.items()},
        "schematron_assertion_count": len(grammar.schematron()),
        "self_assertion_counts": {
            "ordinary_xml": sum("!/" not in name for name in documents),
            "archived_xml": sum("!/" in name for name in documents),
            **{section: sum(len(record.get("ids", {}).get(section, [])) for record in documents.values())
               for section in ("definitions", "tests", "objects", "states", "variables")},
        },
        "oval_5_12_3_counts": dict(sorted(counts.items())),
        "oval_5_12_3_native_capability_counts": {
            "mapped": len(source_capabilities),
            "with_source_test": len(assertion_capabilities),
            "missing_source_test": sorted(source_capabilities - assertion_capabilities),
        },
        "oval_5_12_3_tests": source_tests,
        "oval_6_0_esxi_tests": v6_tests,
        "self_assertion_documents": documents,
        "self_assertion_archives": archives,
        "self_assertion_unknown_test_qnames": sorted(witnesses.keys() - source_tests.keys()),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--oval", type=Path, required=True)
    parser.add_argument("--self-assertion", type=Path, required=True)
    parser.add_argument("--oval6", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build(args.oval, args.self_assertion, args.oval6)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.check:
        if OUTPUT.read_text(encoding="utf-8") != rendered:
            raise SystemExit(f"stale source audit: {OUTPUT}")
    else:
        OUTPUT.write_text(rendered, encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("self_assertion_counts", "oval_5_12_3_counts")}))


if __name__ == "__main__":
    main()
