#!/usr/bin/env python3
"""Original Linux AppArmor singleton Test -> native 0.4 -> independent XML.

An empty OVAL apparmorstatus_object is a required reference in legacy XML;
it is a singleton system collector in 0.4, not an author-defined Object.
The source may report 'not applicable' on a target system; this workflow
proves authoring semantics and XML shape, never live collector behavior.
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

from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
FILE = "linux/linux-def_apparmorstatus_test.xml"
SHA = "1e9b6d6bab5a40226db960cebf08c8124282b86e8b0c52316027d48b2c97a5d6"
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
LINUX = OD + "#linux"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
SOURCE_DEF = "oval:com.jovalcm.test:def:967"
SOURCE_TEST = "oval:com.jovalcm.test:tst:1766"
SOURCE_OBJ = "oval:com.jovalcm.test:obj:1137"
SOURCE_STATE = "oval:com.jovalcm.test:ste:1660"
NEW = "oval:scapng.04.apparmorstatus:"
NAME = "loaded-apparmor-profiles-test"
REQUIRE = "at_least_one_exists_and_all_match"
SPECS = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}


def tag(namespace, name):
    return "{" + namespace + "}" + name


def require(condition, message):
    if not condition:
        raise ValueError("pinned original Linux AppArmor source: " + message)


def one(parent, namespace, local):
    found = parent.findall(tag(namespace, local))
    require(len(found) == 1, "one original " + local)
    return found[0]


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "original OVAL XML source SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "original OVAL namespace")
    sections = [one(root, OD, kind) for kind in
                ("definitions", "tests", "objects", "states")]
    require(all(len(section) == 1 for section in sections),
            "one Definition, Test, Object and State")
    require(root.find(tag(OD, "variables")) is None, "no source Variables")
    definition, test, obj, state = (s[0] for s in sections)
    require(definition.get("id") == SOURCE_DEF and
            definition.get("version") == "2" and
            definition.get("class") == "miscellaneous" and
            test.tag == tag(LINUX, "apparmorstatus_test") and
            test.get("id") == SOURCE_TEST and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "all" and
            set(test.attrib) == {"id", "version", "comment", "check_existence", "check"},
            "exact source AppArmor Test cardinality")
    require(one(test, LINUX, "object").get("object_ref") == SOURCE_OBJ and
            one(test, LINUX, "state").get("state_ref") == SOURCE_STATE and
            obj.tag == tag(LINUX, "apparmorstatus_object") and
            obj.get("id") == SOURCE_OBJ and len(obj) == 0 and
            state.tag == tag(LINUX, "apparmorstatus_state") and
            state.get("id") == SOURCE_STATE,
            "genuinely empty original OVAL singleton Object")
    field = one(state, LINUX, "loaded_profiles_count")
    require(len(state) == 1 and field.get("datatype") == "int" and
            field.get("operation") == "greater than or equal" and
            field.text == "0", "source integer AppArmor State")
    criteria = one(definition, OD, "criteria")
    criterion = one(criteria, OD, "criterion")
    require(criteria.get("operator") == "AND" and
            len(criteria) == 1 and len(criterion) == 0 and
            criterion.get("test_ref") == SOURCE_TEST and
            criterion.get("negate", "false") == "false",
            "original positive criterion")
    title = one(one(definition, OD, "metadata"), OD, "title").text
    return {"assessment": {
        "id": "original-linux-apparmorstatus-assessment", "version": 2,
        "assessment_title": title, "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": SPECS,
        "tests": {NAME: {
            "test_title": test.get("comment"),
            "capability": "linux.apparmorstatus",
            "states": [{"loaded_profiles_count": {
                "greater_than_or_equal": 0, "datatype": "integer",
                "require": REQUIRE}}],
            "reported_elements": "all", "require": REQUIRE,
        }},
        "evaluate": {"and": [{"test": NAME}]},
    }}


def native_to_oval(doc):
    require(set(doc) == {"assessment"}, "native Assessment root")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == "original-linux-apparmorstatus-assessment" and
            a["version"] == 2 and a["mode"] == "automated" and
            a["class"] == "miscellaneous" and a["purpose"] == "assessment" and
            a["specification"] == SPECS and
            a["evaluate"] == {"and": [{"test": NAME}]} and
            set(a["tests"]) == {NAME}, "native Assessment Test graph")
    test = a["tests"][NAME]
    require(set(test) == {"test_title", "capability", "states",
                          "reported_elements", "require"} and
            test["capability"] == "linux.apparmorstatus" and
            test["require"] == REQUIRE and
            test["reported_elements"] == "all" and
            isinstance(test["test_title"], str) and
            test["states"] == [{"loaded_profiles_count": {
                "greater_than_or_equal": 0, "datatype": "integer",
                "require": REQUIRE}}], "native AppArmor integer Test and no Object")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("linux-def", LINUX)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 original Linux AppArmor proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    definition = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "2", "class": "miscellaneous"})
    meta = ET.SubElement(definition, tag(OD, "metadata"))
    ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(meta, tag(OD, "description")).text = "Linux AppArmor singleton item"
    criteria = ET.SubElement(definition, tag(OD, "criteria"), {"operator": "AND"})
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:1"})
    tests = ET.SubElement(root, tag(OD, "tests"))
    src_test = ET.SubElement(tests, tag(LINUX, "apparmorstatus_test"), {
        "id": NEW + "tst:1", "version": "2", "comment": test["test_title"],
        "check_existence": "at_least_one_exists", "check": "all"})
    ET.SubElement(src_test, tag(LINUX, "object"), {"object_ref": NEW + "obj:1"})
    ET.SubElement(src_test, tag(LINUX, "state"), {"state_ref": NEW + "ste:1"})
    objects = ET.SubElement(root, tag(OD, "objects"))
    ET.SubElement(objects, tag(LINUX, "apparmorstatus_object"), {
        "id": NEW + "obj:1", "version": "1"})
    states = ET.SubElement(root, tag(OD, "states"))
    s = ET.SubElement(states, tag(LINUX, "apparmorstatus_state"), {
        "id": NEW + "ste:1", "version": "2"})
    ET.SubElement(s, tag(LINUX, "loaded_profiles_count"), {
        "datatype": "int", "operation": "greater than or equal"}).text = "0"
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/linux-apparmorstatus.assessment.json": doc},
                  _schema_validators(schema_root))
    errors = validate(materialize("linux.apparmorstatus"), "test",
                      doc["assessment"]["tests"][NAME])
    require(not errors, "capability schema " + str(errors[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    yml = dump_hybrid(doc)
    require(yaml.safe_load(yml) == doc, "native YAML/JSON graph identity")
    (out / "native-040.assessment.yaml").write_text(yml)
    regenerated = native_to_oval(doc)
    exported = out / "roundtrip-oval.xml"
    regenerated.write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "linux")
    require(xsd["status"] == "PASS", "original OVAL 5.12.3 Linux XSD " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    semantic = compare(source, exported, source_root=SOURCE_DEF,
                       regenerated_root=NEW + "def:1", root_only=True)
    require(semantic["equal"], "independent source-root semantic graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(semantic, indent=2) + "\n")
    mutated = raw.replace(b'greater than or equal', b'greater than', 1)
    require(mutated != raw, "construct original source operation mutation")
    try:
        source_to_native(mutated)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted mutated original comparison")
    for field, extra in (("object", {}), ("set", {}), ("result", "true")):
        changed = deepcopy(doc)
        changed["assessment"]["tests"][NAME][field] = extra
        try:
            native_to_oval(changed)
        except ValueError:
            continue
        raise AssertionError("accepted extraneous singleton native " + field)
    proof = {
        "source_revision": PIN, "source_file": FILE,
        "original_xml_sha256": SHA, "original_definition_id": SOURCE_DEF,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_root_semantic_graph": "PASS", "source_mutation": "REJECTED",
        "extraneous_singleton_object": "REJECTED", "scanner_parity": False,
    }
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--schema-root", type=Path, required=True)
    p.add_argument("--xsd-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prove(a.source, a.schema_root, a.xsd_root, a.output), sort_keys=True))
