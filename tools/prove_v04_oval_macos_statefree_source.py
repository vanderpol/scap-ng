#!/usr/bin/env python3
"""Three pinned original state-free macOS singleton Test roundtrips.

OVAL filevault, firmwarepassword and profiles: no State references, but
required empty XML Objects and at_least_one_exists source semantics.
Native/schema/export/OVAL 5.12.3 XSD/source-root proof; not scanner parity.
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
MAC = OD + "#macos"
OLD = "oval:org.joval.test:"
NEW = "oval:scapng.04.macos-statefree-"
CASES = {
    "filevault": {
        "source_file": "macos/macos-def_filevault_test.xml",
        "source_sha256": "83a66de7e3f997cfad206ff33335e28b939717738003329d5c4be0c630e3d22d",
        "id_number": 120002,
    },
    "firmwarepassword": {
        "source_file": "macos/macos-def_firmwarepassword_test.xml",
        "source_sha256": "200c768c7add252fb437f3d38b2bcdb839a12b119d1c7af36c82b316d6c01bd2",
        "id_number": 220002,
    },
    "profiles": {
        "source_file": "macos/macos-def_profiles_test.xml",
        "source_sha256": "21c845bb2076a939d216ca9ea8fa37c1dc783ded7d04a881e274b70df8c6abce",
        "id_number": 320002,
    },
}


def source_to_native(raw, kind):
    case = CASES[kind]
    require(sha256(raw).hexdigest() == case["source_sha256"],
            "pinned original macOS " + kind + " SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL source namespace")
    definition = one(root, OD, "definitions")[0]
    test = one(root, OD, "tests")[0]
    obj = one(root, OD, "objects")[0]
    states = root.findall(tag(OD, "states"))
    require(len(one(root, OD, "definitions")) == 1 and
            len(one(root, OD, "tests")) == 1 and
            len(one(root, OD, "objects")) == 1 and
            not states, "one Definition, Test, Object and no States")
    idx = str(case["id_number"])
    criterion = one(one(definition, OD, "criteria"), OD, "criterion")
    require(definition.get("id") == OLD + "def:" + idx and
            definition.get("version") == "0" and
            definition.get("class") == "compliance" and
            criterion.get("test_ref") == test.get("id") and
            test.tag == tag(MAC, kind + "_test") and
            test.get("version") == "0" and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "all" and
            one(test, MAC, "object").get("object_ref") == obj.get("id") and
            not test.findall(tag(MAC, "state")) and
            obj.tag == tag(MAC, kind + "_object") and len(obj) == 0,
            "source state-free singleton, exact Test/Definition and check axes")
    title = one(one(definition, OD, "metadata"), OD, "title").text
    name = kind + "-exists-test"
    return {"assessment": {
        "id": "original-macos-" + kind + "-statefree-assessment",
        # Original OVAL Definition version 0 is schema-valid in OVAL 5.12.3;
        # new native Assessment versions start at 1. Original source version
        # is retained in the pinned source evidence and re-export mapping.
        "version": 1, "assessment_title": title,
        "mode": "automated", "class": "compliance",
        "purpose": "assessment", "specification": SPECS,
        "tests": {name: {
            "test_title": test.get("comment"),
            "capability": "macos." + kind,
            "reported_elements": "all", "require": "at_least_one_exists",
        }},
        "evaluate": {"test": name},
    }}


def native_to_oval(doc, kind):
    case = CASES[kind]
    require(set(doc) == {"assessment"}, "single Assessment document")
    a = doc["assessment"]
    name = kind + "-exists-test"
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == "original-macos-" + kind + "-statefree-assessment" and
            a["version"] == 1 and a["mode"] == "automated" and
            a["class"] == "compliance" and a["purpose"] == "assessment" and
            a["specification"] == SPECS and a["evaluate"] == {"test": name} and
            set(a["tests"]) == {name}, "state-free Assessment contract")
    t = a["tests"][name]
    require(set(t) == {"test_title", "capability", "reported_elements", "require"} and
            t["capability"] == "macos." + kind and
            t["require"] == "at_least_one_exists" and
            t["reported_elements"] == "all",
            "no invented State or Object and preserved Test existence requirement")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("mac-def", MAC)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG " + kind + " source proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    new = NEW + kind + ":"
    d = ET.SubElement(defs, tag(OD, "definition"), {
        "id": new + "def:1", "version": "0", "class": "compliance"})
    meta = ET.SubElement(d, tag(OD, "metadata"))
    ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(meta, tag(OD, "description")).text = "Original state-free " + kind + " proof"
    criterion = ET.SubElement(d, tag(OD, "criteria"))
    ET.SubElement(criterion, tag(OD, "criterion"), {"test_ref": new + "tst:1"})
    tt = ET.SubElement(tests, tag(MAC, kind + "_test"), {
        "id": new + "tst:1", "version": "0", "comment": t["test_title"],
        "check": "all", "check_existence": "at_least_one_exists"})
    ET.SubElement(tt, tag(MAC, "object"), {"object_ref": new + "obj:1"})
    ET.SubElement(objects, tag(MAC, kind + "_object"), {
        "id": new + "obj:1", "version": "1"})
    return ET.ElementTree(root)


def prove_one(kind, source, schema_root, xsd_root, output):
    case = CASES[kind]
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw, kind)
    validate_docs({"authoring/original-macos-" + kind + ".json": doc},
                  _schema_validators(schema_root))
    test = next(iter(doc["assessment"]["tests"].values()))
    problems = validate(materialize("macos." + kind), "test", test)
    require(not problems, "generated native macOS state-free Test " + str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    yml = dump_hybrid(doc)
    require(yaml.safe_load(yml) == doc, "original native YAML/JSON parity")
    (out / "native-040.assessment.yaml").write_text(yml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(doc, kind).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "macos")
    require(xsd["status"] == "PASS", "macOS OVAL 5.12.3 XSD " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    source_root = OLD + "def:" + str(case["id_number"])
    graph = compare(source, exported, source_root=source_root,
                    regenerated_root=NEW + kind + ":def:1", root_only=True)
    require(graph["equal"], "original macOS " + kind + " root semantic graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(graph, indent=2) + "\n")
    wrong_source = raw.replace(b'check_existence="at_least_one_exists"',
                               b'check_existence="none_exist"', 1)
    require(wrong_source != raw, "source mutation fixture")
    try:
        source_to_native(wrong_source, kind)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted original altered existence: " + kind)
    changed = deepcopy(doc)
    changed["assessment"]["tests"][kind + "-exists-test"]["require"] = "none_exist"
    try:
        native_to_oval(changed, kind)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted altered native requirement: " + kind)
    proof = {"source_file": case["source_file"], "source_revision": PIN,
             "original_xml_sha256": case["source_sha256"],
             "original_definition_id": source_root,
             "original_oval_definition_version": 0,
             "native_assessment_version": 1,
             "source_version_remap_documented": True,
             "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
             "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
             "original_root_semantic_graph": "PASS",
             "state_free_test": "PASS", "empty_singleton_object_omitted": "PASS",
             "source_existence_mutation": "REJECTED",
             "native_existence_mutation": "REJECTED", "scanner_parity": False}
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n")
    return proof


def prove(source_root, schema_root, xsd_root, output):
    return {kind: prove_one(kind, Path(source_root) / case["source_file"],
                            schema_root, xsd_root,
                            Path(output) / ("macos-" + kind + "-one"))
            for kind, case in CASES.items()}


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-root", required=True, type=Path)
    p.add_argument("--schema-root", required=True, type=Path)
    p.add_argument("--xsd-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prove(a.source_root, a.schema_root, a.xsd_root, a.output),
                     indent=2, sort_keys=True))
