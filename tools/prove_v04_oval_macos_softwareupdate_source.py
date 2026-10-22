#!/usr/bin/env python3
"""Pinned source-backed macOS softwareupdate singleton Boolean-State proof.

Proves original source -> canonical native 0.4 -> OVAL 5.12.3 XSD and
semantic-root graph. Never claims native scanner execution. Refs #248 #229 #232.
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
FILE = "macos/macos-def_softwareupdate_test.xml"
SHA = "77016edd47f380559b9e1f2beb4ec4998b11e410591bf67db92cad56f4b8c8a0"
OLD_DEF = "oval:navy.navwar.niwcatlantic.scc.test:def:1"
NEW = "oval:scapng.04.softwareupdate:"
MAC = OD + "#macos"
CAPABILITY = "macos.softwareupdate"
ASSESSMENT_ID = "original-macos-softwareupdate-schedule-assessment"
NAME = "softwareupdate-scheduler-test"


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned original softwareupdate SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "original OVAL namespace")
    require(all(len(one(root, OD, name)) == 1
                for name in ("definitions", "tests", "objects", "states")),
            "one original Definition, Test, Object and State")
    definition = one(root, OD, "definitions")[0]
    test = one(root, OD, "tests")[0]
    obj = one(root, OD, "objects")[0]
    state = one(root, OD, "states")[0]
    criterion = one(one(definition, OD, "criteria"), OD, "criterion")
    require(definition.get("id") == OLD_DEF and
            definition.get("version") == "1" and
            definition.get("class") == "miscellaneous" and
            criterion.get("test_ref") == test.get("id") and
            test.tag == tag(MAC, "softwareupdate_test") and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "all" and
            one(test, MAC, "object").get("object_ref") == obj.get("id") and
            one(test, MAC, "state").get("state_ref") == state.get("id") and
            obj.tag == tag(MAC, "softwareupdate_object") and
            len(obj) == 0 and
            state.tag == tag(MAC, "softwareupdate_state") and len(state) == 1,
            "original Test links and empty singleton Object")
    schedule = one(state, MAC, "schedule")
    require(schedule.get("datatype") == "boolean" and
            schedule.get("operation") == "equals" and
            schedule.text == "1", "original Boolean scheduler assertion")
    return {"assessment": {
        "id": ASSESSMENT_ID, "version": 1,
        "assessment_title": one(one(definition, OD, "metadata"), OD, "title").text,
        "mode": "automated", "class": "miscellaneous", "purpose": "assessment",
        "specification": SPECS,
        "tests": {NAME: {
            "test_title": test.get("comment"), "capability": CAPABILITY,
            "states": [{"schedule": {
                "equals": True,
                "require": "at_least_one_exists_and_all_match",
            }}],
            "reported_elements": "all",
            "require": "at_least_one_exists_and_all_match",
        }},
        "evaluate": {"test": NAME},
    }}


def native_to_oval(doc):
    require(set(doc) == {"assessment"}, "one native Assessment document")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == ASSESSMENT_ID and a["version"] == 1 and
            a["mode"] == "automated" and a["class"] == "miscellaneous" and
            a["purpose"] == "assessment" and a["specification"] == SPECS and
            a["evaluate"] == {"test": NAME} and set(a["tests"]) == {NAME},
            "original root/Assessment identity")
    test = a["tests"][NAME]
    require(set(test) == {"test_title", "capability", "states",
                          "reported_elements", "require"} and
            test["capability"] == CAPABILITY and
            test["states"] == [{"schedule": {
                "equals": True, "require": "at_least_one_exists_and_all_match"}}] and
            test["reported_elements"] == "all" and
            test["require"] == "at_least_one_exists_and_all_match",
            "Boolean schedule, State and Test existence/matching")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("mac-def", MAC)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG macOS softwareupdate proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    states = ET.SubElement(root, tag(OD, "states"))
    d = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "1", "class": "miscellaneous"})
    metadata = ET.SubElement(d, tag(OD, "metadata"))
    ET.SubElement(metadata, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(metadata, tag(OD, "description")).text = "Original softwareupdate proof"
    criteria = ET.SubElement(d, tag(OD, "criteria"))
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:1"})
    t = ET.SubElement(tests, tag(MAC, "softwareupdate_test"), {
        "id": NEW + "tst:1", "version": "1", "comment": test["test_title"],
        "check_existence": "at_least_one_exists", "check": "all"})
    ET.SubElement(t, tag(MAC, "object"), {"object_ref": NEW + "obj:1"})
    ET.SubElement(t, tag(MAC, "state"), {"state_ref": NEW + "ste:1"})
    ET.SubElement(objects, tag(MAC, "softwareupdate_object"), {
        "id": NEW + "obj:1", "version": "1"})
    st = ET.SubElement(states, tag(MAC, "softwareupdate_state"), {
        "id": NEW + "ste:1", "version": "1"})
    ET.SubElement(st, tag(MAC, "schedule"), {
        "datatype": "boolean", "operation": "equals"}).text = "1"
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/original-macos-softwareupdate.json": doc},
                  _schema_validators(schema_root))
    problems = validate(materialize(CAPABILITY), "test",
                        doc["assessment"]["tests"][NAME])
    require(not problems, "generated macOS softwareupdate native schema " +
            str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    native_yaml = dump_hybrid(doc)
    require(yaml.safe_load(native_yaml) == doc, "YAML and JSON native graph equality")
    (out / "native-040.assessment.yaml").write_text(native_yaml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(doc).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "macos")
    require(xsd["status"] == "PASS", "OVAL 5.12.3 macOS XSD: " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sem = compare(source, exported, source_root=OLD_DEF,
                  regenerated_root=NEW + "def:1", root_only=True)
    require(sem["equal"], "original softwareupdate Definition semantic-root graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    bad_raw = raw.replace(b'<schedule datatype="boolean" operation="equals">1</schedule>',
                          b'<schedule datatype="boolean" operation="equals">0</schedule>', 1)
    require(bad_raw != raw, "source Boolean mutation fixture exists")
    try:
        source_to_native(bad_raw)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted mutated source Boolean scheduler")
    altered = deepcopy(doc)
    altered["assessment"]["tests"][NAME]["states"][0]["schedule"]["equals"] = False
    try:
        native_to_oval(altered)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted altered native Boolean scheduler")
    proof = {"source_file": FILE, "source_revision": PIN, "original_xml_sha256": SHA,
             "original_definition_id": OLD_DEF, "native_assessment_schema": "PASS",
             "native_capability_schema": "PASS", "yaml_json_graph_equivalence": "PASS",
             "oval_5123_xsd": "PASS", "original_root_semantic_graph": "PASS",
             "empty_singleton_object_omitted": "PASS",
             "boolean_schedule_state_preserved": "PASS",
             "source_boolean_mutation": "REJECTED",
             "native_boolean_mutation": "REJECTED",
             "scanner_parity": False}
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
