#!/usr/bin/env python3
"""Fail-closed 16 -> 17/167 promotion for original OVAL fixed-result unknown.

The source/native/XML proof is independently repeated, not trusted from the
artifact's success labels. Scanner parity is deliberately not asserted.
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

from prove_v04_oval_unknown_source import (
    FILE, NEW_DEF, PIN, SHA, SOURCE_DEF, NAME, native_to_oval,
    source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(condition, reason):
    if not condition:
        raise ValueError("pinned OVAL fixed-unknown promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 16 and
            previous.get("current_040_original_xml_roundtrip_exported") == 16 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 146 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete pinned 16-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete original 167-Definition row ledger required")
    keys = [(r.get("source_file"), r.get("definition_id")) for r in rows]
    require(len(set(keys)) == 167, "unique source/Definition identities")
    updated = deepcopy(previous)
    matching = [r for r in updated["records"]
                if r.get("source_file") == FILE and r.get("definition_id") == SOURCE_DEF]
    require(len(matching) == 1, "exact original fixed-unknown Definition row")
    row = matching[0]
    require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
            row.get("original_source_file_sha256") == SHA and
            row.get("current_040_native_schema") == "NOT_TESTED" and
            row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
            "original fixed-result source not eligible for proof")

    folder = Path(evidence_root).resolve()
    required = ("original.xml", "native-040.assessment.json",
                "native-040.assessment.yaml", "roundtrip-oval.xml",
                "roundtrip-xsd.json", "roundtrip-semantics.json",
                "source-and-mapping-proof.json")
    files = {name: folder / name for name in required}
    require(all(path.is_file() for path in files.values()),
            "complete original/native/XSD/semantic evidence required")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "original XML SHA-256")
    native = json.loads(files["native-040.assessment.json"].read_text())
    require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == native,
            "native YAML/JSON graph equality")
    require(canonical_json(source_to_native(raw)) == canonical_json(native),
            "fresh original-XML-to-minimal-native conversion")
    require(set(native["assessment"]["tests"][NAME]) == {
                "test_title", "capability", "require"} and
            native["assessment"]["tests"][NAME]["require"] == {"items_found": "one_or_more"},
            "uniform structured requirement; no invented collection or State controls")
    regenerated, new_def = native_to_oval(native)
    require(new_def == NEW_DEF, "canonical regenerated Definition identity")
    expected = etree.fromstring(ET.tostring(regenerated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "fresh native-only regenerated XML matches proof")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "independent" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "original OVAL 5.12.3 independent XSD evidence")
    saved_sem = json.loads(files["roundtrip-semantics.json"].read_text())
    actual_sem = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=SOURCE_DEF, regenerated_root=NEW_DEF,
                         root_only=True)
    require(saved_sem.get("equal") is True and actual_sem.get("equal") is True,
            "independently recomputed original-root semantic graph")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_definition_id") == SOURCE_DEF and
            proof.get("original_xml_sha256") == SHA and
            proof.get("scanner_parity") is False and
            proof.get("fixed_result") == "unknown" and
            proof.get("native_control_fields") == ["test_title", "capability", "require"] and
            proof.get("source_mutation") == "REJECTED" and
            proof.get("extraneous_native_controls") == "REJECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_root_semantic_graph")),
            "pinned source, schema and adversarial checks")

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
        row[field] = "fixed-unknown/" + name
    row["current_040_artifact_source"] = (
        "pinned original fixed-result OVAL unknown native-only 0.4 XSD/semantic CI")
    updated["current_040_schema_and_original_source_validated"] = 17
    updated["current_040_original_xml_roundtrip_exported"] = 17
    updated["remaining_v003_compatible_without_current_040_proof"] = 145
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 17,
            "exactly seventeen independently proven original source Definitions")
    return updated


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--previous-ledger", required=True, type=Path)
    p.add_argument("--proof-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    args = p.parse_args()
    result = promote(json.loads(args.previous_ledger.read_text()), args.proof_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, sort_keys=True))
