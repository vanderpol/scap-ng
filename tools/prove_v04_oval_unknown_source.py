#!/usr/bin/env python3
"""Source-pinned OVAL unknown_test -> minimal native 0.4 -> independent XML.

The original OVAL 5.12.3 independent.unknown result is fixed at 'unknown'.
Legacy OVAL existence/matching attributes are mandated by its XML Test base
but do not govern the outcome; native authoring intentionally omits both.
This certifies an original source graph, not scanner/runtime parity.
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
FILE = "agnostic/ind-def_unknown_test.xml"
SHA = "f5e8901c703438819f20ef4761d1b4f9f62f630c6c8e96ca016d0d0dd67862a7"
SOURCE_DEF = "oval:org.mitre.oval.test:def:337"
SOURCE_TEST = "oval:org.mitre.oval.test:tst:939"
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
NEW_DEF = "oval:scapng.04.unknown:def:1"
NEW_TEST = "oval:scapng.04.unknown:tst:1"
NAME = "fixed-unknown-test"


def tag(ns, name):
    return "{" + ns + "}" + name


def require(condition, message):
    if not condition:
        raise ValueError("unreviewed original OVAL fixed-unknown source: " + message)


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned original XML SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "Definitions XML namespace")
    defs = root.find(tag(OD, "definitions"))
    tests = root.find(tag(OD, "tests"))
    require(defs is not None and tests is not None and len(defs) == len(tests) == 1,
            "one original Definition and one Test")
    definition, test = defs[0], tests[0]
    require(definition.tag == tag(OD, "definition") and
            definition.get("id") == SOURCE_DEF and
            definition.get("version") == "2" and
            definition.get("class") == "miscellaneous", "source Definition")
    require(test.tag == tag(IND, "unknown_test") and
            test.get("id") == SOURCE_TEST and
            test.get("version") == "1" and
            test.get("check_existence") == "at_least_one_exists" and
            test.get("check") == "at least one" and
            not list(test) and
            set(test.attrib) == {"id", "version", "comment", "check", "check_existence"},
            "fixed-result unknown Test with no Object or State")
    for section in ("objects", "states", "variables"):
        node = root.find(tag(OD, section))
        require(node is None or len(node) == 0, "no hidden " + section)
    metadata = definition.find(tag(OD, "metadata"))
    require(metadata is not None, "original metadata")
    title = metadata.find(tag(OD, "title"))
    require(title is not None and bool(title.text), "original title")
    criteria = definition.find(tag(OD, "criteria"))
    require(criteria is not None and len(criteria) == 1 and
            criteria.get("operator", "AND") == "AND" and
            set(criteria.attrib) <= {"operator"}, "one original criterion")
    criterion = criteria[0]
    require(criterion.tag == tag(OD, "criterion") and
            criterion.get("test_ref") == SOURCE_TEST and
            set(criterion.attrib) <= {"test_ref", "comment"},
            "single positive Test reference")
    return {"assessment": {
        "id": "independent-unknown-source-assessment", "version": 2,
        "assessment_title": title.text, "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {NAME: {"test_title": test.get("comment"),
                         "capability": "independent.unknown"}},
        "evaluate": {"test": NAME},
    }}


def native_to_oval(native):
    require(isinstance(native, dict) and set(native) == {"assessment"},
            "native Assessment root")
    a = native["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "tests", "evaluate"},
            "native Assessment fields")
    require(a["id"] == "independent-unknown-source-assessment" and
            a["version"] == 2 and a["mode"] == "automated" and
            a["class"] == "miscellaneous" and a["purpose"] == "assessment" and
            a["specification"] == {"id": "scap-ng.pre-alpha.assessment",
                                   "version": "0.4.0"} and
            a["evaluate"] == {"test": NAME} and
            isinstance(a["assessment_title"], str) and
            set(a["tests"]) == {NAME}, "Assessment identity and evaluation")
    test = a["tests"][NAME]
    require(set(test) == {"test_title", "capability"} and
            test["capability"] == "independent.unknown" and
            isinstance(test["test_title"], str), "minimal fixed unknown Test only")
    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("ind-def", IND)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 original unknown proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    definition = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW_DEF, "version": "2", "class": "miscellaneous"})
    metadata = ET.SubElement(definition, tag(OD, "metadata"))
    ET.SubElement(metadata, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(metadata, tag(OD, "description")).text = "Independent fixed-result unknown"
    criteria = ET.SubElement(definition, tag(OD, "criteria"), {"operator": "AND"})
    ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW_TEST})
    tests = ET.SubElement(root, tag(OD, "tests"))
    ET.SubElement(tests, tag(IND, "unknown_test"), {
        "id": NEW_TEST, "version": "1", "comment": test["test_title"],
        "check_existence": "at_least_one_exists", "check": "at least one"})
    return ET.ElementTree(root), NEW_DEF


def prove(source, schema_root, xsd_root, output):
    raw = Path(source).read_bytes()
    native = source_to_native(raw)
    validators = _schema_validators(schema_root)
    validate_docs({"authoring/independent-unknown.assessment.json": native}, validators)
    errors = validate(materialize("independent.unknown"), "test",
                      native["assessment"]["tests"][NAME])
    require(not errors, "current capability-specific schema " + str(errors[:2]))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    (output / "original.xml").write_bytes(raw)
    (output / "native-040.assessment.json").write_text(
        json.dumps(native, indent=2) + "\n")
    yml = dump_hybrid(native)
    require(yaml.safe_load(yml) == native, "YAML JSON graph identity")
    (output / "native-040.assessment.yaml").write_text(yml)
    xml, regen = native_to_oval(native)
    exported = output / "roundtrip-oval.xml"
    xml.write(exported, encoding="utf-8", xml_declaration=True)
    report = check(xsd_root, exported, "independent")
    require(report["status"] == "PASS", "regenerated 5.12.3 XSD " +
            str(report.get("diagnostics", [])[:2]))
    (output / "roundtrip-xsd.json").write_text(json.dumps(report, indent=2) + "\n")
    sem = compare(source, exported, source_root=SOURCE_DEF,
                  regenerated_root=regen, root_only=True)
    require(sem["equal"], "source-independent original-root semantic graph")
    (output / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    mutated = raw.replace(b'check="at least one"', b'check="all"', 1)
    require(mutated != raw, "construct original Test mutation")
    try:
        source_to_native(mutated)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted source Test mutation")
    for field, value in (("object", {}), ("states", []),
                         ("require", "at_least_one_exists"),
                         ("reported_elements", "all"), ("result", "unknown")):
        changed = deepcopy(native)
        changed["assessment"]["tests"][NAME][field] = value
        try:
            native_to_oval(changed)
        except ValueError:
            continue
        raise AssertionError("exported extra fixed-result field " + field)
    proof = {
        "source_revision": PIN, "source_file": FILE,
        "original_definition_id": SOURCE_DEF, "original_xml_sha256": SHA,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_root_semantic_graph": "PASS",
        "fixed_result": "unknown", "native_control_fields": ["test_title", "capability"],
        "source_mutation": "REJECTED", "extraneous_native_controls": "REJECTED",
        "scanner_parity": False,
    }
    (output / "source-and-mapping-proof.json").write_text(
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
