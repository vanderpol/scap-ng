#!/usr/bin/env python3
"""Independently promote original Windows cmdlet source graph 28 -> 31/167.

Only three variable-free source Definitions may be promoted. The remaining
three source Definitions use Variables in cmdlet records and remain unproved.
Native records and only-one outcomes must round-trip through source-independent
OVAL 5.12.3 Windows XML/XSD/graph. Scanner parity remains zero.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from lxml import etree
import yaml

from prove_v04_oval_windows_cmdlet_source import (
    FILE, NEW, PIN, SHA, SOURCES, native_to_oval, original_def,
    source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned three-Definition cmdlet promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 28 and
            previous.get("current_040_original_xml_roundtrip_exported") == 28 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 134 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete 28-of-167 certified prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete 167 original Definition identities")
    keys = [(r.get("source_file"), r.get("definition_id")) for r in rows]
    require(len(set(keys)) == 167, "unique original source/Definition keys")
    updated = deepcopy(previous)
    candidates = [r for r in updated["records"]
                  if r.get("source_file") == FILE]
    require(len(candidates) == 6, "source file contains six Definition rows")
    subset = [r for r in candidates if r.get("definition_id") in {
        original_def(n) for n in SOURCES}]
    require(len(subset) == 3 and
            {r["definition_id"] for r in subset} == {
                original_def(n) for n in SOURCES},
            "only the three variable-free Definition identities")
    for row in subset:
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == SHA and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproved original variable-free cmdlet row " + row["definition_id"])
    for row in candidates:
        if row not in subset:
            require(row.get("current_040_native_schema") == "NOT_TESTED" and
                    row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                    "other source Variables remain unproven")

    folder = Path(evidence_root).resolve()
    names = ("original.xml", "native-040.assessments.json",
             "native-040.assessments.yaml", "roundtrip-oval.xml",
             "roundtrip-xsd.json", "roundtrip-semantics.json",
             "mutated-only-one-to-all.xml", "source-and-mapping-proof.json")
    files = {name: folder / name for name in names}
    require(all(path.is_file() for path in files.values()),
            "complete three-native/Windows XSD/semantic/mutation evidence")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "original source XML SHA")
    docs = json.loads(files["native-040.assessments.json"].read_text())
    require(list(yaml.safe_load_all(files["native-040.assessments.yaml"].read_text())) == docs,
            "all three native YAML/JSON graphs")
    require(canonical_json(source_to_native(raw)) == canonical_json(docs),
            "independent pinned original -> three canonical native conversions")
    regenerated = native_to_oval(docs)
    expected = etree.fromstring(ET.tostring(regenerated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "fresh native-only OVAL exporter recreates exact saved proof")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "windows" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "original Windows OVAL 5.12.3 XSD proof")
    sems = json.loads(files["roundtrip-semantics.json"].read_text())
    require(set(sems) == {str(n) for n in SOURCES},
            "three independent source-root semantic comparisons")
    for n in SOURCES:
        actual = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=original_def(n),
                         regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sems[str(n)].get("equal") is True and actual.get("equal") is True,
                "fresh original root semantics " + str(n))
    changed = compare(files["original.xml"], files["mutated-only-one-to-all.xml"],
                      source_root=original_def(222),
                      regenerated_root=NEW + "def:222", root_only=True)
    require(changed.get("equal") is False, "source only-one differs from all")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_ids") == [original_def(n) for n in SOURCES] and
            proof.get("definition_count") == 3 and
            proof.get("original_test_count") == 3 and
            proof.get("scanner_parity") is False and
            proof.get("source_only_one_mutation") == "REJECTED" and
            proof.get("native_only_one_to_all") == "DETECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_three_root_semantic_graphs", "record_structure_preserved")),
            "source/capability/record/mutation proof claims")
    for row in subset:
        row["current_040_native_schema"] = "PASS"
        row["current_040_oval_xml_roundtrip"] = (
            "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
        row["scanner_six_state_parity"] = "NOT_PROVEN"
        for field, name in {
            "current_040_artifact_json": "native-040.assessments.json",
            "current_040_artifact_yaml": "native-040.assessments.yaml",
            "current_040_proof": "source-and-mapping-proof.json",
            "current_040_regenerated_oval": "roundtrip-oval.xml",
            "current_040_oval_xml_proof": "roundtrip-semantics.json",
        }.items():
            row[field] = "windows-cmdlet-three/" + name
        row["current_040_artifact_source"] = (
            "pinned three variable-free original Windows cmdlet record 0.4 XSD/semantic CI")
    updated["current_040_schema_and_original_source_validated"] = 31
    updated["current_040_original_xml_roundtrip_exported"] = 31
    updated["remaining_v003_compatible_without_current_040_proof"] = 131
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 31,
            "exactly 31 original Definition roots independently proven")
    return updated


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous-ledger", required=True, type=Path)
    p.add_argument("--proof-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = promote(json.loads(a.previous_ledger.read_text()), a.proof_root)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, sort_keys=True))
