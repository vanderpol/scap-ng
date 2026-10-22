#!/usr/bin/env python3
"""Certify pinned original macOS Gatekeeper root graph 39 -> 40/167.

Preserves full original Definition ledger; not scanner runtime parity.
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

from prove_v04_oval_macos_gatekeeper_source import (
    FILE, OLD, NEW, PIN, SHA, native_to_oval, source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned macOS Gatekeeper promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 39 and
            previous.get("current_040_original_xml_roundtrip_exported") == 39 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 123 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete certified 39-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167 and
            len({(r.get("source_file"), r.get("definition_id")) for r in rows}) == 167,
            "unique full pinned original Definition rows")
    updated = deepcopy(previous)
    subset = [r for r in updated["records"] if r.get("source_file") == FILE]
    require(len(subset) == 1 and subset[0].get("definition_id") == OLD + "def:1",
            "exactly one original macOS Gatekeeper Definition")
    row = subset[0]
    require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
            row.get("original_source_file_sha256") == SHA and
            row.get("current_040_native_schema") == "NOT_TESTED" and
            row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
            "unproved original macOS source identity, SHA and proof status")
    folder = Path(evidence_root).resolve()
    names = ("original.xml", "native-040.assessment.json",
             "native-040.assessment.yaml", "roundtrip-oval.xml",
             "roundtrip-xsd.json", "roundtrip-semantics.json",
             "source-and-mapping-proof.json")
    files = {name: folder / name for name in names}
    require(all(p.is_file() for p in files.values()),
            "complete macOS Gatekeeper native/OVAL/XSD/semantic evidence")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "pinned macOS source SHA")
    doc = json.loads(files["native-040.assessment.json"].read_text())
    require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == doc and
            canonical_json(source_to_native(raw)) == canonical_json(doc),
            "fresh original source/native conversion with YAML/JSON parity")
    generated = native_to_oval(doc)
    expected = etree.fromstring(ET.tostring(generated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "independent native-only OVAL XML regeneration")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "macos" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "independent macOS 5.12.3 XSD")
    original = compare(files["original.xml"], files["roundtrip-oval.xml"],
                       source_root=OLD + "def:1",
                       regenerated_root=NEW + "def:1", root_only=True)
    sem = json.loads(files["roundtrip-semantics.json"].read_text())
    require(original.get("equal") is True and sem.get("equal") is True,
            "independent original semantic graph and State-field absence")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_id") == OLD + "def:1" and
            proof.get("scanner_parity") is False and
            proof.get("source_existence_mutation") == "REJECTED" and
            proof.get("native_existence_mutation") == "REJECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_root_semantic_graph", "state_field_none_exist",
                "empty_singleton_object_omitted")),
            "complete source-backed macOS absence-only proof claims")
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
        row[field] = "macos-gatekeeper-one/" + name
    row["current_040_artifact_source"] = (
        "pinned original macOS Gatekeeper singleton State none_exist XSD/semantic CI")
    updated["current_040_schema_and_original_source_validated"] = 40
    updated["current_040_original_xml_roundtrip_exported"] = 40
    updated["remaining_v003_compatible_without_current_040_proof"] = 122
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 40,
            "exactly 40 source-backed Definitions independently proven")
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
