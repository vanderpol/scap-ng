#!/usr/bin/env python3
"""Promote three pinned original cmdlet Variable Definitions, 31 -> 34/167.

No scanner execution claims; preserve the other original source ledger rows.
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

from prove_v04_oval_windows_cmdlet_variable_source import (
    FILE, NEW, PIN, SHA, SOURCES, VARS, native_to_oval, original_def,
    source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned cmdlet Variable promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 31 and
            previous.get("current_040_original_xml_roundtrip_exported") == 31 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 131 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete certified 31-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete 167 source Definition rows")
    keys = [(r.get("source_file"), r.get("definition_id")) for r in rows]
    require(len(set(keys)) == 167, "unique original source/Definition keys")
    updated = deepcopy(previous)
    candidates = [r for r in updated["records"] if r.get("source_file") == FILE]
    require(len(candidates) == 6, "all six source cmdlet Definitions")
    subset = [r for r in candidates if r.get("definition_id") in {
        original_def(n) for n in SOURCES}]
    require(len(subset) == 3 and
            {r["definition_id"] for r in subset} == {
                original_def(n) for n in SOURCES},
            "exactly three source record Variable Definitions")
    for row in subset:
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == SHA and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproven source Variable identity or source SHA " + row["definition_id"])
    for row in candidates:
        if row not in subset:
            require(row.get("current_040_native_schema") == "PASS" and
                    str(row.get("current_040_oval_xml_roundtrip")).startswith("PASS_"),
                    "three previously certified variable-free cmdlet rows retained")

    folder = Path(evidence_root).resolve()
    names = ("original.xml", "native-040.assessments.json",
             "native-040.assessments.yaml", "roundtrip-oval.xml",
             "roundtrip-xsd.json", "roundtrip-semantics.json",
             "mutated-local-variable.xml", "source-and-mapping-proof.json")
    files = {name: folder / name for name in names}
    require(all(p.is_file() for p in files.values()),
            "complete original/native/Windows XSD/semantic/mutation evidence")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "pinned original OVAL source SHA")
    docs = json.loads(files["native-040.assessments.json"].read_text())
    require(list(yaml.safe_load_all(files["native-040.assessments.yaml"].read_text())) == docs,
            "all three native YAML/JSON graphs")
    require(canonical_json(source_to_native(raw)) == canonical_json(docs),
            "fresh pinned original -> canonical native conversions")
    generated = native_to_oval(docs)
    expected = etree.fromstring(ET.tostring(generated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "fresh native-only OVAL exporter re-creates saved proof")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "windows" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "independent Windows OVAL 5.12.3 XSD proof")
    sems = json.loads(files["roundtrip-semantics.json"].read_text())
    require(set(sems) == {str(n) for n in SOURCES},
            "three independent original-root comparisons")
    for n in SOURCES:
        actual = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=original_def(n),
                         regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sems[str(n)].get("equal") is True and actual.get("equal") is True,
                "source root graph and Variable references " + str(n))
    changed = compare(files["original.xml"], files["mutated-local-variable.xml"],
                      source_root=original_def(1222),
                      regenerated_root=NEW + "def:1222", root_only=True)
    require(changed.get("equal") is False,
            "changing local Variable literal changes original graph")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_ids") == [original_def(n) for n in SOURCES] and
            proof.get("definition_count") == 3 and
            proof.get("original_test_count") == 3 and
            proof.get("local_variable_count") == len(VARS) and
            proof.get("scanner_parity") is False and
            proof.get("source_variable_reference_mutation") == "REJECTED" and
            proof.get("native_local_literal_mutation") == "DETECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_three_root_semantic_graphs", "record_variable_links_preserved")),
            "source Variable/capability/XSD/semantic proof claims")
    for row in subset:
        row["current_040_native_schema"] = "PASS"
        row["current_040_oval_xml_roundtrip"] = (
            "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
        row["scanner_six_state_parity"] = "NOT_PROVEN"
        for key, name in {
            "current_040_artifact_json": "native-040.assessments.json",
            "current_040_artifact_yaml": "native-040.assessments.yaml",
            "current_040_proof": "source-and-mapping-proof.json",
            "current_040_regenerated_oval": "roundtrip-oval.xml",
            "current_040_oval_xml_proof": "roundtrip-semantics.json",
        }.items():
            row[key] = "windows-cmdlet-variable-three/" + name
        row["current_040_artifact_source"] = (
            "pinned three original cmdlet Variable record 0.4 Windows XSD/semantic CI")
    updated["current_040_schema_and_original_source_validated"] = 34
    updated["current_040_original_xml_roundtrip_exported"] = 34
    updated["remaining_v003_compatible_without_current_040_proof"] = 128
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 34,
            "exactly 34 original Definition roots independently proven")
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
