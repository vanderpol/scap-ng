#!/usr/bin/env python3
"""Independently promote three original state-free macOS Definitions 42→45.

Source OVAL Definition version 0 is retained in provenance and re-export;
new native Assessments start at version 1. Scanner result parity remains open.
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

from prove_v04_oval_macos_statefree_source import (
    CASES, NEW, OLD, PIN, native_to_oval, source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned three macOS state-free promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 42 and
            previous.get("current_040_original_xml_roundtrip_exported") == 42 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 120 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete certified 42-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167 and
            len({(r.get("source_file"), r.get("definition_id")) for r in rows}) == 167,
            "unique original 167 Definition identities")
    updated = deepcopy(previous)
    folder = Path(evidence_root).resolve()
    for kind, case in CASES.items():
        file = case["source_file"]
        old_def = OLD + "def:" + str(case["id_number"])
        original_sha = case["source_sha256"]
        subset = [r for r in updated["records"] if r.get("source_file") == file]
        require(len(subset) == 1 and subset[0].get("definition_id") == old_def,
                "single original macOS " + kind + " source")
        row = subset[0]
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == original_sha and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproved pinned macOS " + kind + " original source SHA/status")
        case_folder = folder / ("macos-" + kind + "-one")
        names = ("original.xml", "native-040.assessment.json",
                 "native-040.assessment.yaml", "roundtrip-oval.xml",
                 "roundtrip-xsd.json", "roundtrip-semantics.json",
                 "source-and-mapping-proof.json")
        files = {name: case_folder / name for name in names}
        require(all(p.is_file() for p in files.values()),
                "complete original/native/OVAL evidence for " + kind)
        raw = files["original.xml"].read_bytes()
        require(sha256(raw).hexdigest() == original_sha,
                "original macOS " + kind + " input checksum")
        doc = json.loads(files["native-040.assessment.json"].read_text())
        require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == doc and
                canonical_json(source_to_native(raw, kind)) == canonical_json(doc),
                "independent pinned source and YAML/JSON native " + kind)
        expected = etree.fromstring(ET.tostring(
            native_to_oval(doc, kind).getroot(), encoding="utf-8"))
        saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
        require(etree.tostring(expected, method="c14n") ==
                etree.tostring(saved, method="c14n"),
                "independent native-only regenerated macOS XML " + kind)
        xsd = json.loads(files["roundtrip-xsd.json"].read_text())
        require(xsd.get("status") == "PASS" and
                xsd.get("oval_schema_version") == "5.12.3" and
                xsd.get("oval_platform_schema") == "macos" and
                not xsd.get("diagnostics") and
                xsd.get("xml_sha256") == sha256(
                    files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
                "independent original macOS 5.12.3 schema " + kind)
        source_graph = compare(files["original.xml"], files["roundtrip-oval.xml"],
                               source_root=old_def,
                               regenerated_root=NEW + kind + ":def:1", root_only=True)
        saved_graph = json.loads(files["roundtrip-semantics.json"].read_text())
        require(source_graph.get("equal") is True and
                saved_graph.get("equal") is True,
                "independent state-free source graph " + kind)
        proof = json.loads(files["source-and-mapping-proof.json"].read_text())
        require(proof.get("source_file") == file and
                proof.get("source_revision") == PIN and
                proof.get("original_xml_sha256") == original_sha and
                proof.get("original_definition_id") == old_def and
                proof.get("original_oval_definition_version") == 0 and
                proof.get("native_assessment_version") == 1 and
                proof.get("source_version_remap_documented") is True and
                proof.get("scanner_parity") is False and
                proof.get("source_existence_mutation") == "REJECTED" and
                proof.get("native_existence_mutation") == "REJECTED" and
                all(proof.get(k) == "PASS" for k in (
                    "native_assessment_schema", "native_capability_schema",
                    "yaml_json_graph_equivalence", "oval_5123_xsd",
                    "original_root_semantic_graph", "state_free_test",
                    "empty_singleton_object_omitted")),
                "complete version-aware original macOS state-free evidence " + kind)
        row["current_040_native_schema"] = "PASS"
        row["current_040_oval_xml_roundtrip"] = (
            "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
        row["scanner_six_state_parity"] = "NOT_PROVEN"
        for field, name in {
            "current_040_artifact_json": "native-040.assessment.json",
            "current_040_artifact_yaml": "native-040.assessment.yaml",
            "current_040_proof": "source-and-mapping-proof.json",
            "current_040_regenerated_oval": "roundtrip-oval.xml",
            "current_040_oval_xml_proof": "roundtrip-semantics.json",
        }.items():
            row[field] = "macos-" + kind + "-one/" + name
        row["current_040_artifact_source"] = (
            "pinned original macOS " + kind +
            " state-free singleton, OVAL v0→native v1 mapped source provenance")
    updated["current_040_schema_and_original_source_validated"] = 45
    updated["current_040_original_xml_roundtrip_exported"] = 45
    updated["remaining_v003_compatible_without_current_040_proof"] = 117
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 45,
            "exactly 45 original source Definitions independently certified")
    return updated


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
