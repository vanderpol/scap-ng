#!/usr/bin/env python3
"""Independent native-only OVAL 5.12.3 exporter for pinned datatype suites.

Does not consult original XML. Rejects unreviewed native fields/operators and
exports the full Boolean/Test/Variable structure. Refs #248 #229 #232.
"""
from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from convert_v04_oval_variable_datatype_suite import (
    CASES, FIELD_REQUIRE, IP_DATATYPES, NATIVE_DTYPE, OP, PREFIX,
    TEST_REQUIRE, OD, IND, must,
)

OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
VARS = {"binary": 2, "boolean": 4, "string": 6, "float": 3,
        "evr_string": 5, "int": 5, "version": 12,
        "ipv4_address": 2, "ipv6_address": 2}


def tag(ns, name):
    return "{" + ns + "}" + name


def original_op(dtype, native):
    prefix = PREFIX.get(dtype, "")
    must(native.startswith(prefix), "operation datatype prefix")
    ordinary = native[len(prefix):]
    matches = [k for k, v in OP.items() if v == ordinary]
    must(len(matches) == 1, "OVAL typed comparator for " + native)
    if dtype not in PREFIX:
        must(native in OP.values(), "untyped comparator identity")
    return matches[0]


def emit(document):
    must(type(document) is dict and set(document) == {"assessment"},
         "native root")
    assessment = document["assessment"]
    must(type(assessment) is dict and
         set(assessment) == {"id", "version", "assessment_title", "mode",
                             "class", "purpose", "specification", "variables",
                             "tests", "evaluate"}, "Assessment contract")
    id_to_name = {filename.removesuffix(".xml").replace("_", "-") +
                  "-assessment": filename for filename in CASES}
    must(assessment["id"] in id_to_name and
         assessment["specification"] == SPEC and
         assessment["mode"] == "automated" and
         assessment["class"] == "miscellaneous" and
         assessment["purpose"] == "assessment" and
         type(assessment["version"]) is int and
         type(assessment["assessment_title"]) is str,
         "native Assessment source identity/type")
    filename = id_to_name[assessment["id"]]
    original_did, _, dtype, ntests = CASES[filename]
    expected_require = FIELD_REQUIRE if dtype in IP_DATATYPES else TEST_REQUIRE
    variables, tests = assessment["variables"], assessment["tests"]
    must(type(variables) is dict and type(tests) is dict and
         list(variables) == [f"source-{i}-variable" for i in range(1, VARS[dtype]+1)] and
         list(tests) == [f"source-{i}-test" for i in range(1, ntests+1)],
         "Variable/Test identity and count")
    for name, var in variables.items():
        must(type(var) is dict and
             set(var) == {"kind", "datatype", "title", "expression"} and
             var["kind"] == "constant" and
             var["datatype"] == NATIVE_DTYPE.get(dtype, dtype) and
             type(var["title"]) is str and
             type(var["expression"]) is dict and
             set(var["expression"]) == {"literal"} and
             type(var["expression"]["literal"]) is list and
             var["expression"]["literal"] and
             all(type(x) is str for x in var["expression"]["literal"]),
             "typed literal Variable " + name)

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("ind-def", IND)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = (
        "SCAP-NG 0.4 independent native datatype suite export")
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-21T00:00:00Z"
    prefix = "oval:scapng.04.datatype:"
    did = prefix + "def:1"
    definitions = ET.SubElement(root, tag(OD, "definitions"))
    definition = ET.SubElement(definitions, tag(OD, "definition"), {
        "id": did, "version": str(assessment["version"]),
        "class": "miscellaneous",
    })
    metadata = ET.SubElement(definition, tag(OD, "metadata"))
    ET.SubElement(metadata, tag(OD, "title")).text = assessment["assessment_title"]
    ET.SubElement(metadata, tag(OD, "description")).text = (
        "Independent source-pinned native typed-Variable semantic export")
    out_tests = ET.SubElement(root, tag(OD, "tests"))
    out_objects = ET.SubElement(root, tag(OD, "objects"))
    out_states = ET.SubElement(root, tag(OD, "states"))
    out_variables = ET.SubElement(root, tag(OD, "variables"))

    var_ids = {}
    obj_ids = {}
    for i, (name, var) in enumerate(variables.items(), 1):
        var_ids[name] = prefix + f"var:{i}"
        obj_ids[name] = prefix + f"obj:{i}"
        v = ET.SubElement(out_variables, tag(OD, "constant_variable"), {
            "id": var_ids[name], "version": str(assessment["version"]),
            "datatype": dtype, "comment": var["title"],
        })
        for value in var["expression"]["literal"]:
            ET.SubElement(v, tag(OD, "value")).text = value
        o = ET.SubElement(out_objects, tag(IND, "variable_object"), {
            "id": obj_ids[name], "version": str(assessment["version"]),
        })
        ET.SubElement(o, tag(IND, "var_ref")).text = var_ids[name]

    test_ids = {}
    for i, (name, test) in enumerate(tests.items(), 1):
        must(type(test) is dict and
             set(test) == {"test_title", "capability", "variable", "states",
                           "reported_elements", "require"} and
             type(test["test_title"]) is str and
             test["capability"] == "variable.value" and
             test["variable"] in variables and
             test["reported_elements"] == "all" and
             test["require"] == expected_require and
             type(test["states"]) is list and len(test["states"]) == 1 and
             type(test["states"][0]) is dict and
             set(test["states"][0]) == {"value"},
             "Test contract " + name)
        predicate = test["states"][0]["value"]
        must(type(predicate) is dict and
             predicate.get("require") == FIELD_REQUIRE and
             predicate.get("datatype") == NATIVE_DTYPE.get(dtype, dtype) and
             len(predicate) == 3, "exact typed State field")
        ops = [k for k in predicate if k not in {"require", "datatype"}]
        must(len(ops) == 1 and type(predicate[ops[0]]) is str,
             "one lexical typed comparison")
        operation = original_op(dtype, ops[0])
        sid = prefix + f"ste:{i}"
        state = ET.SubElement(out_states, tag(IND, "variable_state"), {
            "id": sid, "version": str(assessment["version"]),
        })
        attrs = {}
        if dtype != "string":
            attrs["datatype"] = dtype
        if operation != "equals":
            attrs["operation"] = operation
        ET.SubElement(state, tag(IND, "value"), attrs).text = predicate[ops[0]]
        tid = prefix + f"tst:{i}"
        test_ids[name] = tid
        native = ET.SubElement(out_tests, tag(IND, "variable_test"), {
            "id": tid, "version": str(assessment["version"]),
            "comment": test["test_title"], "check": (
                "all" if dtype in IP_DATATYPES else "at least one"),
            "check_existence": "at_least_one_exists",
        })
        ET.SubElement(native, tag(IND, "object"), {
            "object_ref": obj_ids[test["variable"]],
        })
        ET.SubElement(native, tag(IND, "state"), {"state_ref": sid})

    covered = []
    def criteria(node, parent):
        must(type(node) is dict and len(node) == 1, "Boolean shape")
        if "test" in node:
            name = node["test"]
            must(name in test_ids, "referenced native Test")
            covered.append(name)
            ET.SubElement(parent, tag(OD, "criterion"), {
                "test_ref": test_ids[name],
            })
            return
        if "not" in node:
            child = node["not"]
            must(type(child) is dict and set(child) == {"test"} and
                 child["test"] in test_ids, "negative leaf Test only")
            covered.append(child["test"])
            ET.SubElement(parent, tag(OD, "criterion"), {
                "test_ref": test_ids[child["test"]], "negate": "true",
            })
            return
        must(set(node) == {"and"} and
             type(node["and"]) is list and node["and"],
             "nested AND only")
        group = ET.SubElement(parent, tag(OD, "criteria"), {"operator": "AND"})
        for child in node["and"]:
            criteria(child, group)
    criteria(assessment["evaluate"], definition)
    must(len(covered) == ntests and set(covered) == set(tests),
         "complete unique Test coverage")
    return ET.ElementTree(root), did


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    xml, _ = emit(json.loads(args.native.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    xml.write(args.output, encoding="utf-8", xml_declaration=True)
