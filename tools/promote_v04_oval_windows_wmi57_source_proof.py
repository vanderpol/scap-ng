#!/usr/bin/env python3
"""Certify original Windows wmi57 source graph cases 34 -> 39/167.

Independent OVAL 5.12.3 XML/XSD and root semantics, not scanner parity.
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

from prove_v04_oval_windows_wmi57_source import (
    FILE, NEW, PIN, SHA, SOURCES, native_to_oval, parse_source, source_id,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned Windows WMI57 promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 34 and
            previous.get("current_040_original_xml_roundtrip_exported") == 34 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 128 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete certified 34-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete 167 original Definition identities")
    keys = [(r.get("source_file"), r.get("definition_id")) for r in rows]
    require(len(set(keys)) == 167, "unique source/Definition row keys")
    result = deepcopy(previous)
    subset = [r for r in result["records"] if r.get("source_file") == FILE]
    require(len(subset) == 5 and
            {r["definition_id"] for r in subset} == {
                source_id("def", n) for n in SOURCES},
            "exactly five original Windows wmi57 Definitions")
    for row in subset:
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == SHA and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproved original source graph and SHA " + row["definition_id"])
    folder = Path(evidence_root).resolve()
    names = ("original.xml", "native-040.assessments.json",
             "native-040.assessments.yaml", "roundtrip-oval.xml",
             "roundtrip-xsd.json", "roundtrip-semantics.json",
             "mutated-native-wql.xml", "source-and-mapping-proof.json")
    files = {name: folder / name for name in names}
    require(all(p.is_file() for p in files.values()),
            "complete source/native/WMI record/XSD/semantic evidence")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "pinned original WMI57 XML SHA")
    docs = json.loads(files["native-040.assessments.json"].read_text())
    require(list(yaml.safe_load_all(files["native-040.assessments.yaml"].read_text())) == docs,
            "five native YAML/JSON Assessment graphs")
    require(canonical_json(parse_source(raw)) == canonical_json(docs),
            "fresh independent original WMI57 -> native conversion")
    generated = native_to_oval(docs)
    original = etree.fromstring(ET.tostring(generated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(original, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "fresh native-only 5.12.3 Windows XML export")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "windows" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "independent Windows 5.12.3 XSD proof")
    sems = json.loads(files["roundtrip-semantics.json"].read_text())
    require(set(sems) == {str(n) for n in SOURCES},
            "five original WMI source root comparisons")
    for n in SOURCES:
        actual = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=source_id("def", n),
                         regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sems[str(n)].get("equal") is True and actual.get("equal") is True,
                "original WMI source root semantics " + str(n))
    mutated = compare(files["original.xml"], files["mutated-native-wql.xml"],
                      source_root=source_id("def", 20),
                      regenerated_root=NEW + "def:20", root_only=True)
    require(mutated.get("equal") is False,
            "independently detect altered native WQL acquisition")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_ids") == [
                source_id("def", n) for n in SOURCES] and
            proof.get("definition_count") == 5 and
            proof.get("original_test_count") == 5 and
            proof.get("scanner_parity") is False and
            proof.get("source_wql_mutation") == "REJECTED" and
            proof.get("native_wql_mutation") == "DETECTED" and
            proof.get("native_none_exist_mutation") == "REJECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_five_root_semantic_graphs", "none_exist_without_state",
                "typed_record_result")),
            "complete WMI record, none_exist, XSD, semantic and negative claims")
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
            row[key] = "windows-wmi57-five/" + name
        row["current_040_artifact_source"] = (
            "pinned five original WMI57 native 0.4 record/none_exist Windows XSD/semantic CI")
    result["current_040_schema_and_original_source_validated"] = 39
    result["current_040_original_xml_roundtrip_exported"] = 39
    result["remaining_v003_compatible_without_current_040_proof"] = 123
    result["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in result["records"]) == 39,
            "exactly 39 original OVAL Definition graphs proven")
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous-ledger", required=True, type=Path)
    p.add_argument("--proof-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    result = promote(json.loads(a.previous_ledger.read_text()), a.proof_root)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, sort_keys=True))
