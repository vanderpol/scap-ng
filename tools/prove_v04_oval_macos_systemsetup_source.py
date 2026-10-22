#!/usr/bin/env python3
"""Pinned macOS systemsetup singleton two-State-field 0.4/OVAL proof.

Original XML → native 0.4 YAML/JSON → independent OVAL 5.12.3 XSD and
source-root semantic comparison; never a claim of scanner execution.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

from prove_v04_oval_windows_cmdlet_source import OD, OC, SPECS, tag, require, one
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check


PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
FILE = "macos/macos-def_systemsetup_test.xml"
SHA = "7c357cda4df4959cbf188e96bebbfcec7f70e79d41eabf88ce0936c5ec1c5077"
OLD_DEF = "oval:navy.navwar.niwcatlantic.scc.test:def:1"
NEW = "oval:scapng.04.systemsetup:"
MAC = OD + "#macos"
CAPABILITY = "macos.systemsetup"
ASSESSMENT_ID = "original-macos-systemsetup-two-field-assessment"
NAME = "systemsetup-state-test"


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned original macOS systemsetup SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "original OVAL namespace")
    definition = one(root, OD, "definitions")[0]
    test = one(root, OD, "tests")[0]
    obj = one(root, OD, "objects")[0]
    state = one(root, OD, "states")[0]
    require(len(one(root, OD, "definitions")) == 1 and
            len(one(root, OD, "tests")) == 1 and
            len(one(root, OD, "objects")) == 1 and
            len(one(root, OD, "states")) == 1,
            "one original Definition, Test, singleton Object and State")
    criterion = one(one(definition, OD, "criteria"), OD, "criterion")
    require(definition.get("id") == OLD_DEF and
            definition.get("class") == "compliance" and
            criterion.get("test_ref") == test.get("id") and
            test.tag == tag(MAC, "systemsetup_test") and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "all" and
            one(test, MAC, "object").get("object_ref") == obj.get("id") and
            one(test, MAC, "state").get("state_ref") == state.get("id") and
            obj.tag == tag(MAC, "systemsetup_object") and len(obj) == 0 and
            state.tag == tag(MAC, "systemsetup_state") and len(state) == 2,
            "original singleton and Test/State links")
    sleep = one(state, MAC, "computersleep")
    computer = one(state, MAC, "computername")
    require(sleep.get("datatype") == "int" and
            sleep.get("operation") == "greater than or equal" and
            sleep.text == "0" and
            computer.get("operation") == "pattern match" and
            computer.text == r"\S+" and
            computer.get("datatype") is None,
            "original typed sleep threshold and computername regex")
    return {"assessment": {
        "id": ASSESSMENT_ID, "version": int(definition.get("version")),
        "assessment_title": one(one(definition, OD, "metadata"), OD, "title").text,
        "mode": "automated", "class": "compliance", "purpose": "assessment",
        "specification": SPECS,
        "tests": {NAME: {
            "test_title": test.get("comment"), "capability": CAPABILITY,
            "states": [{"and": [
                {"computersleep": {
                    "greater_than_or_equal": int(sleep.text),
                    "require": "at_least_one_exists_and_all_match"}},
                {"computername": {
                    "matches_regex": computer.text,
                    "require": "at_least_one_exists_and_all_match"}},
            ]}],
            "reported_elements": "all",
            "require": "at_least_one_exists_and_all_match",
        }},
        "evaluate": {"test": NAME},
    }}


def native_to_oval(doc):
    require(set(doc) == {"assessment"}, "native Assessment document")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == ASSESSMENT_ID and a["version"] == 1 and
            a["mode"] == "automated" and a["class"] == "compliance" and
            a["purpose"] == "assessment" and a["specification"] == SPECS and
            a["evaluate"] == {"test": NAME} and set(a["tests"]) == {NAME},
            "single native Assessment and source Test identity")
    t = a["tests"][NAME]
    require(set(t) == {"test_title", "capability", "states",
                       "reported_elements", "require"} and
            t["capability"] == CAPABILITY and t["reported_elements"] == "all" and
            t["require"] == "at_least_one_exists_and_all_match" and
            t["states"] == [{"and": [
                {"computersleep": {"greater_than_or_equal": 0,
                                   "require": "at_least_one_exists_and_all_match"}},
                {"computername": {"matches_regex": r"\S+",
                                  "require": "at_least_one_exists_and_all_match"}},
            ]}], "separate typed numeric and regex State field semantics")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("mac-def", MAC)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG macOS systemsetup proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    states = ET.SubElement(root, tag(OD, "states"))
    d = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "1", "class": "compliance"})
    meta = ET.SubElement(d, tag(OD, "metadata"))
    ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(meta, tag(OD, "description")).text = "Original systemsetup proof"
    criteria = ET.SubElement(d, tag(OD, "criteria"))
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:1"})
    tt = ET.SubElement(tests, tag(MAC, "systemsetup_test"), {
        "id": NEW + "tst:1", "version": "1", "comment": t["test_title"],
        "check": "all", "check_existence": "at_least_one_exists"})
    ET.SubElement(tt, tag(MAC, "object"), {"object_ref": NEW + "obj:1"})
    ET.SubElement(tt, tag(MAC, "state"), {"state_ref": NEW + "ste:1"})
    ET.SubElement(objects, tag(MAC, "systemsetup_object"), {
        "id": NEW + "obj:1", "version": "1"})
    st = ET.SubElement(states, tag(MAC, "systemsetup_state"), {
        "id": NEW + "ste:1", "version": "1"})
    ET.SubElement(st, tag(MAC, "computersleep"), {
        "datatype": "int", "operation": "greater than or equal"}).text = "0"
    ET.SubElement(st, tag(MAC, "computername"), {
        "operation": "pattern match"}).text = r"\S+"
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/original-macos-systemsetup.json": doc},
                  _schema_validators(schema_root))
    problems = validate(materialize(CAPABILITY), "test",
                        doc["assessment"]["tests"][NAME])
    require(not problems, "generated macOS systemsetup State schema " +
            str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    native_yml = dump_hybrid(doc)
    require(yaml.safe_load(native_yml) == doc, "YAML and JSON native equality")
    (out / "native-040.assessment.yaml").write_text(native_yml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(doc).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "macos")
    require(xsd["status"] == "PASS", "OVAL 5.12.3 macOS XSD " +
            str(xsd.get("diagnostics", [])[:4]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sem = compare(source, exported, source_root=OLD_DEF,
                  regenerated_root=NEW + "def:1", root_only=True)
    require(sem["equal"], "original macOS systemsetup root semantic graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    wrong_source = raw.replace(b'operation="greater than or equal"',
                               b'operation="greater than"', 1)
    require(wrong_source != raw, "source threshold operation mutation fixture")
    try:
        source_to_native(wrong_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted mutated original systemsetup threshold")
    changed = deepcopy(doc)
    changed["assessment"]["tests"][NAME]["states"][0]["and"][1][
        "computername"]["matches_regex"] = ".*"
    try:
        native_to_oval(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed native computername regex")
    proof = {"source_file": FILE, "source_revision": PIN,
             "original_xml_sha256": SHA, "original_definition_id": OLD_DEF,
             "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
             "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
             "original_root_semantic_graph": "PASS",
             "singleton_object_omitted": "PASS", "typed_sleep_and_regex": "PASS",
             "source_operation_mutation": "REJECTED",
             "native_regex_mutation": "REJECTED", "scanner_parity": False}
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--schema-root", required=True, type=Path)
    p.add_argument("--xsd-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prove(a.source, a.schema_root, a.xsd_root, a.output),
                     sort_keys=True))
