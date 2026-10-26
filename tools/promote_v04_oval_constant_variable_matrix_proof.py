#!/usr/bin/env python3
"""Promote two source-pinned 0.4 constant Variable proofs from 4/167 to 6/167.

The complete 167-row input ledger, exact prior count, original source hashes,
native documents and independent OVAL graph/XSD evidence must all agree.
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

from convert_v04_oval_constant_variable_matrix import CASES, PIN
from check_v04_oval_constant_variable_matrix import convert
from check_v04_oval_constant_variable_matrix import emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, message):
    if not ok:
        raise ValueError("constant Variable ledger promotion: " + message)


def promote(previous, proof_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 4 and
            previous.get("current_040_original_xml_roundtrip_exported") == 4 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 158 and
            previous.get("scanner_result_parity_proven") == 0,
            "certified complete 4/167 source ledger required")
    rows = previous.get("records")
    require(type(rows) is list and len(rows) == 167,
            "complete 167 original Definition rows")
    indexed = {(r["source_file"], r["definition_id"]): r for r in rows}
    require(len(indexed) == 167, "unique source Definition identities")
    updated = deepcopy(previous)
    changed = {(r["source_file"], r["definition_id"]): r
               for r in updated["records"]}
    base = Path(proof_root).resolve()
    for filename, (original_did, source_sha) in CASES.items():
        source_file = "agnostic/" + filename
        key = source_file, original_did
        require(key in indexed, "missing original Definition " + str(key))
        row = indexed[key]
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == source_sha and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproven/changed source row " + str(key))
        directory = (base / filename.removesuffix(".xml")).resolve()
        require(directory.is_relative_to(base) and directory.is_dir(),
                "proof directory missing")
        required = ("original.xml", "native-040.assessment.json",
                    "native-040.assessment.yaml", "roundtrip-oval.xml",
                    "roundtrip-xsd.json", "roundtrip-semantics.json",
                    "source-and-mapping-proof.json")
        files = {name: directory / name for name in required}
        require(all(p.is_file() for p in files.values()),
                "missing proof member " + filename)
        raw = files["original.xml"].read_bytes()
        require(sha256(raw).hexdigest() == source_sha,
                "original OVAL bytes do not match pinned ledger")
        native = json.loads(files["native-040.assessment.json"].read_text())
        require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == native,
                "YAML/JSON graph differs")
        recreated, canonical_proof = convert(raw, filename)
        require(canonical_json(recreated) == canonical_json(native),
                "independent native conversion changed")
        proof = json.loads(files["source-and-mapping-proof.json"].read_text())
        required_passes = ("native_assessment_schema", "native_capability_schema",
                           "yaml_json_graph_equivalence", "oval_5123_xsd",
                           "original_root_semantic_graph")
        require(all(proof.get(label) == "PASS" for label in required_passes) and
                proof.get("source_sha_mutation") == "REJECTED" and
                set(proof.get("native_structural_mutations", [])) == {
                    "Test_check", "missing_Test",
                    ("scalar_var_check" if filename == "oval-def_constant_variable.xml"
                     else "var_check_enum")},
                "missing adversarial native-structure mutation evidence")
        require(
                set(proof.get("independent_semantic_mutations", [])) == {
                    "Variable_value", "Criterion_negation"} and
                proof.get("scanner_parity") is False and
                proof.get("original_xml_sha256") == source_sha and
                proof.get("original_definition_id") == original_did and
                proof.get("source_revision") == PIN and
                proof.get("native_test_count") == canonical_proof["native_test_count"],
                "incomplete or mismatched proof status")
        xsd = json.loads(files["roundtrip-xsd.json"].read_text())
        require(xsd.get("status") == "PASS" and
                xsd.get("oval_schema_version") == "5.12.3" and
                xsd.get("oval_platform_schema") == "independent" and
                not xsd.get("diagnostics") and
                xsd.get("xml_sha256") == sha256(
                    files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
                "OVAL XSD evidence missing or changed")
        saved = json.loads(files["roundtrip-semantics.json"].read_text())
        tree, emitted_did = emit(native)
        # The independently created XML must agree with native-only export.
        independent = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
        fresh = etree.fromstring(ET.tostring(tree.getroot(), encoding="utf-8"))
        require(etree.tostring(independent, method="c14n") ==
                etree.tostring(fresh, method="c14n"),
                "re-exported native OVAL XML differs")
        result = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=original_did,
                         regenerated_root=emitted_did, root_only=True)
        require(saved.get("equal") is True and result.get("equal") is True,
                "original root OVAL semantic graph differs")
        current = changed[key]
        current["current_040_native_schema"] = "PASS"
        current["current_040_oval_xml_roundtrip"] = (
            "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
        current["scanner_six_state_parity"] = "NOT_PROVEN"
        current["current_040_artifact_json"] = (
            filename.removesuffix(".xml") + "/native-040.assessment.json")
        current["current_040_artifact_yaml"] = (
            filename.removesuffix(".xml") + "/native-040.assessment.yaml")
        current["current_040_proof"] = (
            filename.removesuffix(".xml") + "/source-and-mapping-proof.json")
        current["current_040_regenerated_oval"] = (
            filename.removesuffix(".xml") + "/roundtrip-oval.xml")
        current["current_040_oval_xml_proof"] = (
            filename.removesuffix(".xml") + "/roundtrip-semantics.json")
        current["current_040_artifact_source"] = (
            "pinned 0.4.0 constant Variable matrix native/XML CI proof")
    updated["current_040_schema_and_original_source_validated"] = 6
    updated["current_040_original_xml_roundtrip_exported"] = 6
    updated["remaining_v003_compatible_without_current_040_proof"] = 156
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 6,
            "exactly six certified native/XML original Definitions")
    return updated


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--previous-ledger", required=True, type=Path)
    cli.add_argument("--proof-root", required=True, type=Path)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    promoted = promote(json.loads(args.previous_ledger.read_text()),
                       args.proof_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(promoted, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key: value for key, value in promoted.items()
                      if key != "records"}, sort_keys=True))


if __name__ == "__main__":
    main()
