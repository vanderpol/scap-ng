#!/usr/bin/env python3
"""Original OVAL Windows lockoutpolicy singleton/multi-field native 0.4 proof.

The source has one empty XML Object and four ANDed State fields. The 0.4
Assessment omits the meaningless Object and uses explicit logical AND for
the four comparisons; scalar datatype is capability-defined. No scanner.
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
FILE = "windows/win-def_lockoutpolicy_test.xml"
SHA = "30818be7d856dde1975e451858029e8de8deeb53c370dc979581256995681ade"
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
WIN = OD + "#windows"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
SOURCE_DEF = "oval:org.mitre.oval.test:def:705"
SOURCE_TEST = "oval:org.mitre.oval.test:tst:1268"
SOURCE_OBJ = "oval:org.mitre.oval.test:obj:76"
SOURCE_STATE = "oval:org.mitre.oval.test:ste:1077"
NEW = "oval:scapng.04.lockoutpolicy:"
NAME = "windows-lockout-settings-test"
REQUIRE = "at_least_one_exists_and_all_match"
FIELDS = ("force_logoff", "lockout_duration", "lockout_observation_window",
          "lockout_threshold")
VALUES = dict.fromkeys(FIELDS, 0) | {"force_logoff": -1}
SPECS = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}


def tag(namespace, name):
    return "{" + namespace + "}" + name


def require(ok, message):
    if not ok:
        raise ValueError("pinned original Windows lockout source: " + message)


def one(parent, namespace, local):
    found = parent.findall(tag(namespace, local))
    require(len(found) == 1, "one original " + local)
    return found[0]


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "original source XML SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL Definitions namespace")
    sections = [one(root, OD, kind) for kind in
                ("definitions", "tests", "objects", "states")]
    require(all(len(section) == 1 for section in sections) and
            root.find(tag(OD, "variables")) is None,
            "one original Definition/Test/empty Object/State, no Variables")
    definition, test, obj, state = (s[0] for s in sections)
    require(definition.get("id") == SOURCE_DEF and
            definition.get("version") == "1" and
            definition.get("class") == "miscellaneous" and
            test.tag == tag(WIN, "lockoutpolicy_test") and
            test.get("id") == SOURCE_TEST and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "all" and
            one(test, WIN, "object").get("object_ref") == SOURCE_OBJ and
            one(test, WIN, "state").get("state_ref") == SOURCE_STATE,
            "original Windows Test cardinalities and references")
    require(obj.tag == tag(WIN, "lockoutpolicy_object") and
            obj.get("id") == SOURCE_OBJ and not len(obj) and
            state.tag == tag(WIN, "lockoutpolicy_state") and
            state.get("id") == SOURCE_STATE and len(state) == 4,
            "empty original Windows singleton Object and four State fields")
    for name in FIELDS:
        field = one(state, WIN, name)
        require(field.get("datatype") == "int" and
                field.get("operation") == "greater than or equal" and
                field.text == str(VALUES[name]),
                "exact source field condition " + name)
    criteria = one(definition, OD, "criteria")
    criterion = one(criteria, OD, "criterion")
    require(len(criteria) == 1 and
            criteria.get("operator", "AND") == "AND" and
            criterion.get("test_ref") == SOURCE_TEST and
            criterion.get("negate", "false") == "false",
            "original positive Windows criterion")
    title = one(one(definition, OD, "metadata"), OD, "title").text
    return {"assessment": {
        "id": "original-windows-lockoutpolicy-assessment", "version": 1,
        "assessment_title": title, "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": SPECS,
        "tests": {NAME: {
            "test_title": test.get("comment"),
            "capability": "windows.lockoutpolicy",
            "states": [{"and": [
                {name: {"greater_than_or_equal": VALUES[name], "require": REQUIRE}}
                for name in FIELDS]}],
            "reported_elements": "all", "require": REQUIRE,
        }},
        "evaluate": {"test": NAME},
    }}


def native_to_oval(doc):
    require(set(doc) == {"assessment"}, "native Assessment root")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"} and
            a["id"] == "original-windows-lockoutpolicy-assessment" and
            a["version"] == 1 and a["mode"] == "automated" and
            a["class"] == "miscellaneous" and a["purpose"] == "assessment" and
            a["specification"] == SPECS and a["evaluate"] == {"test": NAME} and
            set(a["tests"]) == {NAME}, "native Assessment graph")
    test = a["tests"][NAME]
    require(set(test) == {"test_title", "capability", "states",
                          "reported_elements", "require"} and
            test["capability"] == "windows.lockoutpolicy" and
            test["require"] == REQUIRE and test["reported_elements"] == "all" and
            isinstance(test["test_title"], str) and
            isinstance(test["states"], list) and len(test["states"]) == 1,
            "native Windows Test source and existence")
    require(test["states"] == [{"and": [
        {name: {"greater_than_or_equal": VALUES[name], "require": REQUIRE}}
        for name in FIELDS]}], "four source field conditions must be ANDed")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("win-def", WIN)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 original lockout policy proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    definition = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "1", "class": "miscellaneous"})
    meta = ET.SubElement(definition, tag(OD, "metadata"))
    ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(meta, tag(OD, "description")).text = "Windows lockout policy"
    criteria = ET.SubElement(definition, tag(OD, "criteria"), {"operator": "AND"})
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:1"})
    tests = ET.SubElement(root, tag(OD, "tests"))
    t = ET.SubElement(tests, tag(WIN, "lockoutpolicy_test"), {
        "id": NEW + "tst:1", "version": "1", "comment": test["test_title"],
        "check_existence": "at_least_one_exists", "check": "all"})
    ET.SubElement(t, tag(WIN, "object"), {"object_ref": NEW + "obj:1"})
    ET.SubElement(t, tag(WIN, "state"), {"state_ref": NEW + "ste:1"})
    objects = ET.SubElement(root, tag(OD, "objects"))
    ET.SubElement(objects, tag(WIN, "lockoutpolicy_object"), {
        "id": NEW + "obj:1", "version": "1"})
    states = ET.SubElement(root, tag(OD, "states"))
    s = ET.SubElement(states, tag(WIN, "lockoutpolicy_state"), {
        "id": NEW + "ste:1", "version": "1"})
    for predicate in test["states"][0]["and"]:
        name, field = next(iter(predicate.items()))
        ET.SubElement(s, tag(WIN, name), {
            "datatype": "int", "operation": "greater than or equal"}).text = str(
                field["greater_than_or_equal"])
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/windows-lockout.assessment.json": doc},
                  _schema_validators(schema_root))
    errors = validate(materialize("windows.lockoutpolicy"), "test",
                      doc["assessment"]["tests"][NAME])
    require(not errors, "generated canonical capability schema " + str(errors[:2]))
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
    xsd = check(xsd_root, exported, "windows")
    require(xsd["status"] == "PASS", "OVAL 5.12.3 Windows XSD " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sem = compare(source, exported, source_root=SOURCE_DEF,
                  regenerated_root=NEW + "def:1", root_only=True)
    require(sem["equal"], "independent original-root four-field semantic graph")
    (out / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    changed = raw.replace(b'greater than or equal', b'greater than', 1)
    require(changed != raw, "construct source operation mutation")
    try:
        source_to_native(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted altered original OVAL comparison")
    for field, extra in (("object", {}), ("result", "true")):
        altered = deepcopy(doc)
        altered["assessment"]["tests"][NAME][field] = extra
        try:
            native_to_oval(altered)
        except ValueError:
            continue
        raise AssertionError("accepted invented Windows singleton " + field)
    wrong = deepcopy(doc)
    wrong["assessment"]["tests"][NAME]["states"][0]["or"] = (
        wrong["assessment"]["tests"][NAME]["states"][0].pop("and"))
    try:
        native_to_oval(wrong)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted OR instead of original four-field AND")
    proof = {
        "source_revision": PIN, "source_file": FILE,
        "original_xml_sha256": SHA, "original_definition_id": SOURCE_DEF,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_root_semantic_graph": "PASS", "source_mutation": "REJECTED",
        "extraneous_singleton_object": "REJECTED", "four_field_or_mutation": "REJECTED",
        "scanner_parity": False,
    }
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, sort_keys=True, indent=2) + "\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--schema-root", type=Path, required=True)
    p.add_argument("--xsd-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prove(a.source, a.schema_root, a.xsd_root, a.output), sort_keys=True))
