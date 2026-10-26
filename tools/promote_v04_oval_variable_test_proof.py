#!/usr/bin/env python3
"""Promote source-proven variable.value OVAL XML roundtrip into 167 Definition ledger.

Requires prior complete 3/167 cumulative baseline, current 0.4 native schema
evidence, independently generated OVAL 5.12.3 XSD/semantic comparison, source
identity and negative tests. No scanner parity. Refs #248 #229.
"""
from __future__ import annotations
import argparse
from hashlib import sha256
import json
from pathlib import Path
from copy import deepcopy
import yaml

from v04_a_authoring_graph_index import canonical_json
from convert_v04_oval_independent_variable_test import convert_current as convert
from export_v04_oval_independent_variable_test import emit_current as emit
from scap_ng_roundtrip_v003.compare_oval_semantics import compare

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
ORIGINAL = "agnostic/ind-def_variable_test.xml"
DID = "oval:org.mitre.oval.test:def:538"
FILES = (
    "native-040.assessment.json", "native-040.assessment.yaml",
    "original.xml", "roundtrip-oval.xml",
    "source-and-mapping-proof.json", "roundtrip-xsd.json",
    "roundtrip-semantics.json", "negative-tests.json",
)


def promote(previous, directory):
    if not (previous.get("source_revision") == PIN
            and previous.get("original_definitions") == 167
            and previous.get("declared_oval_tests") == 785
            and previous.get("original_source_invalid_or_deprecated") == 5
            and previous.get("current_040_schema_and_original_source_validated") == 3
            and previous.get("current_040_original_xml_roundtrip_exported") == 3
            and previous.get("scanner_result_parity_proven") == 0
            and previous.get("remaining_v003_compatible_without_current_040_proof") == 159):
        raise ValueError("previous complete 3/167 source-proven ledger missing")
    entries = {(r["source_file"], r["definition_id"]): r
               for r in previous.get("records", [])}
    if len(entries) != 167 or (ORIGINAL, DID) not in entries:
        raise ValueError("pinned independent.variable source Definition absent")
    row = entries[(ORIGINAL, DID)]
    if (row.get("source_status") != "OVAL_003_SOURCE_COMPATIBLE"
            or row.get("current_040_native_schema") != "NOT_TESTED"
            or row.get("current_040_oval_xml_roundtrip") != "NOT_TESTED"):
        raise ValueError("source Definition already promoted or invalid")
    base = Path(directory).resolve()
    paths = {}
    for file in FILES:
        path = (base / file).resolve()
        if not path.is_file() or not path.is_relative_to(base):
            raise ValueError("missing independent current proof file: " + file)
        paths[file] = path
    original = paths["original.xml"].read_bytes()
    native = json.loads(paths["native-040.assessment.json"].read_text())
    if yaml.safe_load(paths["native-040.assessment.yaml"].read_text()) != native:
        raise ValueError("independently rendered YAML/JSON native Assessment differs")
    canonical_doc, canonical_proof = convert(original)
    if canonical_json(native) != canonical_json(canonical_doc):
        raise ValueError("promoted native Assessment differs from pinned original OVAL conversion")
    proof = json.loads(paths["source-and-mapping-proof.json"].read_text())
    xsd = json.loads(paths["roundtrip-xsd.json"].read_text())
    sem = json.loads(paths["roundtrip-semantics.json"].read_text())
    negatives = json.loads(paths["negative-tests.json"].read_text())
    sha_original = sha256(original).hexdigest()
    sha_exported = sha256(paths["roundtrip-oval.xml"].read_bytes()).hexdigest()
    if (row.get("original_source_file_sha256") != sha_original
            or proof["original_xml_sha256"] != sha_original
            or proof["original_definition_id"] != DID
            or proof["original_revision"] != PIN
            or proof["original_path"] != ORIGINAL
            or proof["native_capability"] != "variable.value"
            or proof["native_assessment_sha256"] != canonical_proof["native_assessment_sha256"]
            or proof.get("native_schema_validated") is not True
            or proof.get("roundtrip_oval_5123_validated") is not True
            or len(proof.get("test_pairs", [])) != 4):
        raise ValueError("source identity/native-schema/roundtrip assertions changed")
    if (xsd.get("status") != "PASS"
            or xsd.get("oval_schema_version") != "5.12.3"
            or xsd.get("oval_platform_schema") != "independent"
            or xsd.get("xml_sha256") != sha_exported
            or xsd.get("diagnostics")):
        raise ValueError("independent native-to-OVAL XSD proof failed")
    if sem.get("equal") is not True:
        raise ValueError("independent original-vs-exported OVAL semantic proof failed")
    exported, new_id = emit(native)
    comparison = compare(
        paths["original.xml"], paths["roundtrip-oval.xml"],
        source_root=DID, regenerated_root=new_id, root_only=True)
    if comparison.get("equal") is not True:
        raise ValueError("fresh independent source XML comparison disagrees")
    if (negatives.get("changed_literal_semantic_graph_rejected") is not True
            or negatives.get("not_scanner_parity") is not True
            or set(negatives.get("rejected_structural_mutations", [])) != {
                "var_check", "test_check", "missing_pair",
                "swapped_state_ref", "lost_constant_value"}):
        raise ValueError("required adversarial semantic mutation evidence missing")
    updated = deepcopy(previous)
    current = next(r for r in updated["records"]
                   if (r["source_file"], r["definition_id"]) == (ORIGINAL, DID))
    current["current_040_native_schema"] = "PASS"
    current["current_040_oval_xml_roundtrip"] = (
        "PASS_INDEPENDENT_OVAL_5123_SEMANTIC_AND_XSD")
    current["scanner_six_state_parity"] = "NOT_PROVEN"
    current["current_040_artifact_json"] = "native-040.assessment.json"
    current["current_040_artifact_yaml"] = "native-040.assessment.yaml"
    current["current_040_proof"] = "source-and-mapping-proof.json"
    current["current_040_regenerated_oval"] = "roundtrip-oval.xml"
    current["current_040_oval_xml_proof"] = "roundtrip-semantics.json"
    current["current_040_artifact_source"] = (
        "0.4.0 pinned OVAL independent.variable existing variable.value CI artifact")
    updated["current_040_schema_and_original_source_validated"] = 4
    updated["current_040_original_xml_roundtrip_exported"] = 4
    updated["remaining_v003_compatible_without_current_040_proof"] = 158
    updated["scanner_result_parity_proven"] = 0
    if sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
           for r in updated["records"]) != 4:
        raise ValueError("OVAL XML source-proven total is not exactly four")
    return updated


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--previous-ledger", type=Path, required=True)
    cli.add_argument("--variable-artifacts", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    prior = json.loads(args.previous_ledger.read_text())
    result = promote(prior, args.variable_artifacts)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "records"}, indent=2))


if __name__ == "__main__":
    main()
