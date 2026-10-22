#!/usr/bin/env python3
"""Fail-closed original OVAL datatype proof promotion from 6/167 to 13/167.

Requires all seven pinned original XML files, native YAML/JSON, fresh native
conversion, independent OVAL 5.12.3 XSD, re-export and semantic equivalence.
No scanner parity is asserted. Refs #248 #229 #232.
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

from convert_v04_oval_variable_datatype_suite import CASES, PIN, convert
from export_v04_oval_variable_datatype_suite import emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned datatype suite promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 6 and
            previous.get("current_040_original_xml_roundtrip_exported") == 6 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 156 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete pinned 6-of-167 previous ledger required")
    records = previous.get("records")
    require(type(records) is list and len(records) == 167,
            "complete 167-row original Definition identity ledger")
    keys = {(r["source_file"], r["definition_id"]) for r in records}
    require(len(keys) == 167, "unique source Definition rows")
    updated = deepcopy(previous)
    index = {(r["source_file"], r["definition_id"]): r
             for r in updated["records"]}
    root = Path(evidence_root).resolve()
    for filename, (did, digest, dtype, ntests) in CASES.items():
        rel = "agnostic/" + filename
        row = index.get((rel, did))
        require(row is not None and
                row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == digest and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproven/changed original Definition " + rel)
        folder = (root / filename.removesuffix(".xml")).resolve()
        require(folder.is_relative_to(root) and folder.is_dir(),
                "evidence folder missing " + filename)
        names = ("original.xml", "native-040.assessment.json",
                 "native-040.assessment.yaml", "roundtrip-oval.xml",
                 "roundtrip-xsd.json", "roundtrip-semantics.json",
                 "source-and-mapping-proof.json")
        files = {name: folder / name for name in names}
        require(all(p.is_file() for p in files.values()),
                "required source/native/XSD evidence missing " + filename)
        raw = files["original.xml"].read_bytes()
        require(sha256(raw).hexdigest() == digest, "source XML SHA " + filename)
        native = json.loads(files["native-040.assessment.json"].read_text())
        require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == native,
                "native YAML/JSON graph identity " + filename)
        rebuilt, canonical = convert(raw, filename)
        require(canonical_json(rebuilt) == canonical_json(native) and
                canonical["native_test_count"] == ntests and
                canonical["source_datatype"] == dtype,
                "fresh source-native comparison " + filename)
        proof = json.loads(files["source-and-mapping-proof.json"].read_text())
        require(proof.get("original_definition_id") == did and
                proof.get("original_xml_sha256") == digest and
                proof.get("source_revision") == PIN and
                proof.get("source_file") == rel and
                proof.get("native_test_count") == ntests and
                proof.get("scanner_parity") is False and
                set(k for k in ("native_assessment_schema", "native_capability_schema",
                                "yaml_json_graph_equivalence", "oval_5123_xsd",
                                "original_root_semantic_graph") if proof.get(k) == "PASS") == {
                                    "native_assessment_schema", "native_capability_schema",
                                    "yaml_json_graph_equivalence", "oval_5123_xsd",
                                    "original_root_semantic_graph"} and
                proof.get("source_sha_mutation") == "REJECTED" and
                proof.get("native_test_requirement_mutation") == "REJECTED" and
                proof.get("original_variable_mutation") == "DETECTED" and
                proof.get("original_criterion_mutation") == "DETECTED",
                "adversarial proof or source identity changed " + filename)
        xsd = json.loads(files["roundtrip-xsd.json"].read_text())
        require(xsd.get("status") == "PASS" and
                xsd.get("oval_schema_version") == "5.12.3" and
                xsd.get("oval_platform_schema") == "independent" and
                not xsd.get("diagnostics") and
                xsd.get("xml_sha256") == sha256(
                    files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
                "OVAL 5.12.3 independent XSD evidence " + filename)
        xml, id_new = emit(native)
        expected = etree.fromstring(ET.tostring(xml.getroot(), encoding="utf-8"))
        saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
        require(etree.tostring(expected, method="c14n") ==
                etree.tostring(saved, method="c14n"),
                "fresh independent native-only OVAL exporter " + filename)
        old = json.loads(files["roundtrip-semantics.json"].read_text())
        sem = compare(files["original.xml"], files["roundtrip-oval.xml"],
                      source_root=did, regenerated_root=id_new, root_only=True)
        require(old.get("equal") is True and sem.get("equal") is True,
                "source root graph mismatch " + filename)
        row["current_040_native_schema"] = "PASS"
        row["current_040_oval_xml_roundtrip"] = (
            "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
        row["scanner_six_state_parity"] = "NOT_PROVEN"
        for key, target in {
            "current_040_artifact_json": "native-040.assessment.json",
            "current_040_artifact_yaml": "native-040.assessment.yaml",
            "current_040_proof": "source-and-mapping-proof.json",
            "current_040_regenerated_oval": "roundtrip-oval.xml",
            "current_040_oval_xml_proof": "roundtrip-semantics.json",
        }.items():
            row[key] = filename.removesuffix(".xml") + "/" + target
        row["current_040_artifact_source"] = (
            "pinned native-only 0.4 OVAL datatype suite XSD/semantic CI proof")
    updated["current_040_schema_and_original_source_validated"] = 13
    updated["current_040_original_xml_roundtrip_exported"] = 13
    updated["remaining_v003_compatible_without_current_040_proof"] = 149
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 13,
            "exactly thirteen current original 0.4 native/XML proofs")
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
