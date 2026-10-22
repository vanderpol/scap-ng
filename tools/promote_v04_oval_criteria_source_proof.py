#!/usr/bin/env python3
"""Fail-closed cumulative 17 -> 26/167 original OVAL criteria source promotion.

Requires the certified 17-row baseline, source-pinned nine-Definition native
Assessments, independent XML/XSD and all nine original-root semantic graphs.
This does not certify scanner execution or the entire OVAL vocabulary.
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

from prove_v04_oval_criteria_source import (
    FILE, NEW, NUMBERS, PIN, SHA, def_id, native_to_oval,
    source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, reason):
    if not ok:
        raise ValueError("pinned nine-definition criteria promotion: " + reason)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 17 and
            previous.get("current_040_original_xml_roundtrip_exported") == 17 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 145 and
            previous.get("scanner_result_parity_proven") == 0,
            "exact certified 17-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete original 167 Definition identity ledger")
    keys = [(r.get("source_file"), r.get("definition_id")) for r in rows]
    require(len(set(keys)) == 167, "unique original source/Definition rows")
    updated = deepcopy(previous)
    candidates = [r for r in updated["records"] if r.get("source_file") == FILE]
    require(len(candidates) == 9 and
            {r.get("definition_id") for r in candidates} ==
            {def_id(n) for n in NUMBERS}, "nine original criteria Definition identities")
    for row in candidates:
        require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
                row.get("original_source_file_sha256") == SHA and
                row.get("current_040_native_schema") == "NOT_TESTED" and
                row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
                "unproven original source row " + row["definition_id"])

    folder = Path(evidence_root).resolve()
    names = ("original.xml", "native-040.assessments.json",
             "native-040.assessments.yaml", "roundtrip-oval.xml",
             "roundtrip-xsd.json", "roundtrip-semantics.json",
             "source-and-mapping-proof.json", "mutated-xor-to-one.xml",
             "mutated-one-to-xor.xml")
    files = {name: folder / name for name in names}
    require(all(p.is_file() for p in files.values()),
            "complete original/nine-native/XSD/semantic/adversarial artifacts")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "pinned original OVAL XML digest")
    docs = json.loads(files["native-040.assessments.json"].read_text())
    require(list(yaml.safe_load_all(files["native-040.assessments.yaml"].read_text())) == docs,
            "all nine native YAML/JSON graph identities")
    require(canonical_json(source_to_native(raw)) == canonical_json(docs),
            "fresh original XML -> nine native 0.4 Assessments")
    regenerated = native_to_oval(docs)
    expected = etree.fromstring(ET.tostring(regenerated.getroot(), encoding="utf-8"))
    observed = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(observed, method="c14n"),
            "independent re-export must originate solely from native Assessments")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "independent" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "independent OVAL 5.12.3 XSD proof")
    sems = json.loads(files["roundtrip-semantics.json"].read_text())
    require(set(sems) == {str(n) for n in NUMBERS},
            "original nine Definition graph report completeness")
    for n in NUMBERS:
        actual = compare(files["original.xml"], files["roundtrip-oval.xml"],
                         source_root=def_id(n),
                         regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sems[str(n)].get("equal") is True and actual.get("equal") is True,
                "independently checked source Definition root " + str(n))
    for original, replacement, n in (("xor", "one", 142),
                                     ("one", "xor", 599)):
        actual = compare(files["original.xml"],
                         files[f"mutated-{original}-to-{replacement}.xml"],
                         source_root=def_id(n),
                         regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(actual.get("equal") is False,
                "ONE versus XOR original semantic mutation must be detectable")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_ids") == [def_id(n) for n in NUMBERS] and
            proof.get("definition_count") == 9 and
            proof.get("test_count") == 2 and
            proof.get("scanner_parity") is False and
            proof.get("source_mutation") == "REJECTED" and
            proof.get("native_expression_mutation") == "REJECTED" and
            proof.get("one_xor_semantic_swap") == "DETECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_nine_root_semantic_graphs")),
            "source, native, XSD and adversarial proof claims")
    for row in candidates:
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
            row[field] = "criteria-nine/" + name
        row["current_040_artifact_source"] = (
            "pinned source nine-Definition OVAL criteria/ONE/XOR 0.4 CI proof")
    updated["current_040_schema_and_original_source_validated"] = 26
    updated["current_040_original_xml_roundtrip_exported"] = 26
    updated["remaining_v003_compatible_without_current_040_proof"] = 136
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 26,
            "exactly 26 original Definition roots independently proven")
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
