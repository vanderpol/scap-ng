#!/usr/bin/env python3
"""Pinned macOS diskinfo original Object selector and State-free Test roundtrip.

Source selector pattern matching is distinct from the Test's existence
requirement; verifies native/schema/OVAL root parity, not scanner execution.
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
FILE = "macos/macos-def_diskinfo_test.xml"
SHA = "b11a4b5d8eb387cd577b59712dcceaaf59c773d744d1fd54d1cef4edd4794ba9"
OLD_DEF = "oval:org.joval.oval:def:9620"
NEW = "oval:scapng.04.diskinfo:"
MAC = OD + "#macos"
CAPABILITY = "macos.diskinfo"
ASSESSMENT_ID = "original-macos-diskinfo-device-selector-assessment"
NAME = "diskinfo-device-selection-exists-test"


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned original macOS diskinfo SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions") and
            all(len(one(root, OD, section)) == 1
                for section in ("definitions", "tests", "objects")) and
            not root.findall(tag(OD, "states")),
            "original single Definition/Test/Object and no State")
    definition = one(root, OD, "definitions")[0]
    test = one(root, OD, "tests")[0]
    obj = one(root, OD, "objects")[0]
    criterion = one(one(definition, OD, "criteria"), OD, "criterion")
    selector = one(obj, MAC, "device_identifier")
    require(definition.get("id") == OLD_DEF and
            definition.get("version") == "1" and
            definition.get("class") == "miscellaneous" and
            criterion.get("test_ref") == test.get("id") and
            test.tag == tag(MAC, "diskinfo_test") and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "at least one" and
            one(test, MAC, "object").get("object_ref") == obj.get("id") and
            not test.findall(tag(MAC, "state")) and
            obj.tag == tag(MAC, "diskinfo_object") and len(obj) == 1 and
            selector.get("operation") == "pattern match" and
            selector.text == ".*", "source State-free Test and device regex selector")
    return {"assessment": {
        "id": ASSESSMENT_ID, "version": 1,
        "assessment_title": one(one(definition, OD, "metadata"), OD, "title").text,
        "mode": "automated", "class": "miscellaneous", "purpose": "assessment",
        "specification": SPECS,
        "tests": {NAME: {
            "test_title": test.get("comment"), "capability": CAPABILITY,
            "object": {
                "device_identifier": {"matches_regex": selector.text},
            },
            "reported_elements": "all", "require": "at_least_one_exists",
        }},
        "evaluate": {"test": NAME},
    }}


def native_to_oval(doc):
    require(set(doc) == {"assessment"}, "one native Assessment")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == ASSESSMENT_ID and a["version"] == 1 and
            a["mode"] == "automated" and a["class"] == "miscellaneous" and
            a["purpose"] == "assessment" and a["specification"] == SPECS and
            a["evaluate"] == {"test": NAME} and set(a["tests"]) == {NAME},
            "original root and Assessment identity")
    test = a["tests"][NAME]
    require(set(test) == {"test_title", "capability", "object",
                          "reported_elements", "require"} and
            test["capability"] == CAPABILITY and
            test["object"] == {
                "device_identifier": {"matches_regex": ".*"}} and
            test["reported_elements"] == "all" and
            test["require"] == "at_least_one_exists",
            "one Object selector, no invented States, one-or-more Items")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("mac-def", MAC)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG diskinfo proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    d = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "1", "class": "miscellaneous"})
    metadata = ET.SubElement(d, tag(OD, "metadata"))
    ET.SubElement(metadata, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(metadata, tag(OD, "description")).text = "Original diskinfo proof"
    criteria = ET.SubElement(d, tag(OD, "criteria"))
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:1"})
    tt = ET.SubElement(tests, tag(MAC, "diskinfo_test"), {
        "id": NEW + "tst:1", "version": "1", "comment": test["test_title"],
        "check_existence": "at_least_one_exists", "check": "at least one"})
    ET.SubElement(tt, tag(MAC, "object"), {"object_ref": NEW + "obj:1"})
    obj = ET.SubElement(objects, tag(MAC, "diskinfo_object"), {
        "id": NEW + "obj:1", "version": "1"})
    ET.SubElement(obj, tag(MAC, "device_identifier"), {
        "operation": "pattern match"}).text = ".*"
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/original-macos-diskinfo.json": doc},
                  _schema_validators(schema_root))
    problems = validate(materialize(CAPABILITY), "test",
                        doc["assessment"]["tests"][NAME])
    require(not problems, "generated macOS diskinfo schema: " + str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    native_yaml = dump_hybrid(doc)
    require(yaml.safe_load(native_yaml) == doc, "YAML/JSON native graph equality")
    (out / "native-040.assessment.yaml").write_text(native_yaml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(doc).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "macos")
    require(xsd["status"] == "PASS", "OVAL 5.12.3 macOS XSD: " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sem = compare(source, exported, source_root=OLD_DEF,
                  regenerated_root=NEW + "def:1", root_only=True)
    require(sem["equal"], "original diskinfo Definition semantic-root graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    bad_source = raw.replace(b'operation="pattern match">.*</device_identifier>',
                             b'operation="pattern match">.+</device_identifier>', 1)
    require(bad_source != raw, "source selector mutation fixture")
    try:
        source_to_native(bad_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted mutated original diskinfo selector")
    changed = deepcopy(doc)
    changed["assessment"]["tests"][NAME]["object"][
        "device_identifier"]["matches_regex"] = ".+"
    try:
        native_to_oval(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed native device selector")
    proof = {"source_file": FILE, "source_revision": PIN,
             "original_xml_sha256": SHA, "original_definition_id": OLD_DEF,
             "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
             "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
             "original_root_semantic_graph": "PASS",
             "device_selector_preserved": "PASS", "no_state_invented": "PASS",
             "source_selector_mutation": "REJECTED",
             "native_selector_mutation": "REJECTED", "scanner_parity": False}
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
