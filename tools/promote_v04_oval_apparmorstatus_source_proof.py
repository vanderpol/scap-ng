#!/usr/bin/env python3
"""Promote one original Linux singleton source Definition from 26 to 27/167.

The native Assessment has no fake Object; the independent 5.12.3 exporter
reintroduces its mandatory empty XML singleton object. No runtime parity.
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

from prove_v04_oval_apparmorstatus_source import (
    FILE, NEW, PIN, SHA, SOURCE_DEF, native_to_oval, source_to_native,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from v04_a_authoring_graph_index import canonical_json


def require(ok, message):
    if not ok:
        raise ValueError("pinned Linux AppArmor source promotion: " + message)


def promote(previous, evidence_root):
    require(previous.get("source_revision") == PIN and
            previous.get("original_definitions") == 167 and
            previous.get("declared_oval_tests") == 785 and
            previous.get("original_source_invalid_or_deprecated") == 5 and
            previous.get("current_040_schema_and_original_source_validated") == 26 and
            previous.get("current_040_original_xml_roundtrip_exported") == 26 and
            previous.get("remaining_v003_compatible_without_current_040_proof") == 136 and
            previous.get("scanner_result_parity_proven") == 0,
            "complete certified 26-of-167 prior ledger required")
    rows = previous.get("records")
    require(isinstance(rows, list) and len(rows) == 167,
            "complete 167 original Definition rows")
    keys = {(r.get("source_file"), r.get("definition_id")) for r in rows}
    require(len(keys) == 167, "unique original Definition identities")
    updated = deepcopy(previous)
    matched = [r for r in updated["records"]
               if r.get("source_file") == FILE and r.get("definition_id") == SOURCE_DEF]
    require(len(matched) == 1, "exact original Linux AppArmor Definition")
    row = matched[0]
    require(row.get("source_status") == "OVAL_003_SOURCE_COMPATIBLE" and
            row.get("original_source_file_sha256") == SHA and
            row.get("current_040_native_schema") == "NOT_TESTED" and
            row.get("current_040_oval_xml_roundtrip") == "NOT_TESTED",
            "original Linux AppArmor row not eligible for promotion")
    folder = Path(evidence_root).resolve()
    filenames = ("original.xml", "native-040.assessment.json",
                 "native-040.assessment.yaml", "roundtrip-oval.xml",
                 "roundtrip-xsd.json", "roundtrip-semantics.json",
                 "source-and-mapping-proof.json")
    files = {name: folder / name for name in filenames}
    require(all(f.is_file() for f in files.values()),
            "complete original/native/Linux XSD/semantic evidence")
    raw = files["original.xml"].read_bytes()
    require(sha256(raw).hexdigest() == SHA, "original source digest")
    native = json.loads(files["native-040.assessment.json"].read_text())
    require(yaml.safe_load(files["native-040.assessment.yaml"].read_text()) == native,
            "native YAML and JSON Assessment graph")
    require(canonical_json(source_to_native(raw)) == canonical_json(native),
            "independent fresh original to native conversion")
    require("object" not in next(iter(native["assessment"]["tests"].values())),
            "no invented native singleton Object")
    generated = native_to_oval(native)
    expected = etree.fromstring(ET.tostring(generated.getroot(), encoding="utf-8"))
    saved = etree.fromstring(files["roundtrip-oval.xml"].read_bytes())
    require(etree.tostring(expected, method="c14n") ==
            etree.tostring(saved, method="c14n"),
            "fresh XML exported from native alone")
    xsd = json.loads(files["roundtrip-xsd.json"].read_text())
    require(xsd.get("status") == "PASS" and
            xsd.get("oval_schema_version") == "5.12.3" and
            xsd.get("oval_platform_schema") == "linux" and
            not xsd.get("diagnostics") and
            xsd.get("xml_sha256") == sha256(
                files["roundtrip-oval.xml"].read_bytes()).hexdigest(),
            "independent 5.12.3 Linux XSD validation evidence")
    semantic = json.loads(files["roundtrip-semantics.json"].read_text())
    actual = compare(files["original.xml"], files["roundtrip-oval.xml"],
                     source_root=SOURCE_DEF,
                     regenerated_root=NEW + "def:1", root_only=True)
    require(semantic.get("equal") is True and actual.get("equal") is True,
            "independently compared source-root semantic graph")
    proof = json.loads(files["source-and-mapping-proof.json"].read_text())
    require(proof.get("source_revision") == PIN and
            proof.get("source_file") == FILE and
            proof.get("original_xml_sha256") == SHA and
            proof.get("original_definition_id") == SOURCE_DEF and
            proof.get("scanner_parity") is False and
            proof.get("source_mutation") == "REJECTED" and
            proof.get("extraneous_singleton_object") == "REJECTED" and
            all(proof.get(k) == "PASS" for k in (
                "native_assessment_schema", "native_capability_schema",
                "yaml_json_graph_equivalence", "oval_5123_xsd",
                "original_root_semantic_graph")),
            "complete source, schema, XSD and mutation proof")
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
        row[field] = "linux-apparmorstatus/" + name
    row["current_040_artifact_source"] = (
        "pinned original Linux AppArmor objectless singleton 0.4 XSD/semantic CI")
    updated["current_040_schema_and_original_source_validated"] = 27
    updated["current_040_original_xml_roundtrip_exported"] = 27
    updated["remaining_v003_compatible_without_current_040_proof"] = 135
    updated["scanner_result_parity_proven"] = 0
    require(sum(str(r.get("current_040_oval_xml_roundtrip", "")).startswith("PASS_")
                for r in updated["records"]) == 27,
            "exactly 27 original Definition roots certified")
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
