#!/usr/bin/env python3
"""Independent strict variable.value 0.4 -> OVAL 5.12.3 four-Test exporter.

Consumes only native authoring; never reads or imports the original XML or
source converter. Reconstructs Variable Objects, value var_check States, Test
cardinality and four ordered Test pairings. Ref #248 #229 #228.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
EXPECTED_SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
REQUIRE = "at_least_one_exists_and_some_match"
VARIABLE_NAMES = ("first-source-variable", "second-source-variable")
TEST_NAMES = (
    "first-to-second-variable-test", "second-to-first-variable-test",
    "first-to-first-variable-test", "second-to-second-variable-test",
)


def demand(condition, reason):
    if not condition:
        raise ValueError("unsupported native 0.4 variable.value OVAL export: " + reason)


def q(uri, name):
    return "{" + uri + "}" + name


def emit(document):
    a = document.get("assessment") if isinstance(document, dict) else None
    demand(isinstance(a, dict), "Assessment required")
    demand(set(a) == {"id", "version", "assessment_title", "mode", "class",
                      "purpose", "specification", "variables", "tests", "evaluate"},
           "unreviewed Assessment properties")
    demand(a["specification"] == EXPECTED_SPEC and
           a["mode"] == "automated" and a["class"] == "miscellaneous" and
           a["purpose"] == "assessment" and type(a["version"]) is int,
           "different version/mode/class")
    variables = a["variables"]
    demand(type(variables) is dict and set(variables) == set(VARIABLE_NAMES),
           "two original constant Variable identities required")
    for key, variable in variables.items():
        demand(set(variable) == {"kind", "datatype", "title", "expression"} and
               variable["kind"] == "constant" and
               variable["datatype"] == "string" and
               isinstance(variable["title"], str) and
               set(variable["expression"]) == {"literal"}, "Variable shape/datatype")
        value = variable["expression"]["literal"]
        demand(type(value) is list and len(value) == 4 and
               all(type(x) is str and bool(x) for x in value),
               "four source variable string values required")
    demand(set(a["tests"]) == set(TEST_NAMES) and
           a["evaluate"] == {"and": [{"test": x} for x in TEST_NAMES]},
           "four-Test ordered source Boolean AND")
    sequence = []
    for testname in TEST_NAMES:
        test = a["tests"][testname]
        demand(set(test) == {"test_title", "capability", "variable", "states",
                              "reported_elements", "require"} and
               test["capability"] == "variable.value" and
               test["variable"] in variables and
               test["reported_elements"] == "all" and test["require"] == REQUIRE,
               "unsupported Test collection requirement or capability")
        demand(isinstance(test["test_title"], str) and
               len(test["states"]) == 1 and
               isinstance(test["states"][0], dict) and
               set(test["states"][0]) == {"value"}, "State cardinality")
        predicate = test["states"][0]["value"]
        demand(set(predicate) == {"equals", "datatype", "value_match", "require"} and
               predicate["datatype"] == "string" and
               predicate["value_match"] == "one_or_more" and
               predicate["require"] == REQUIRE and
               type(predicate["equals"]) is dict and
               set(predicate["equals"]) == {"variable"} and
               predicate["equals"]["variable"] in variables,
               "source State value/var_check mismatch")
        sequence.append((testname, test["variable"],
                         predicate["equals"]["variable"]))
    expected = {
        (VARIABLE_NAMES[0], VARIABLE_NAMES[1]),
        (VARIABLE_NAMES[1], VARIABLE_NAMES[0]),
        (VARIABLE_NAMES[0], VARIABLE_NAMES[0]),
        (VARIABLE_NAMES[1], VARIABLE_NAMES[1]),
    }
    demand({(a,b) for _,a,b in sequence} == expected,
           "four cross/diagonal source pairings missing")

    for prefix, uri in (("oval-def", OD), ("oval", OC), ("ind-def", IND)):
        ET.register_namespace(prefix, uri)
    root = ET.Element(q(OD, "oval_definitions"))
    gen = ET.SubElement(root, q(OD, "generator"))
    ET.SubElement(gen, q(OC, "product_name")).text = (
        "SCAP-NG 0.4 variable.value verified exporter")
    ET.SubElement(gen, q(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(gen, q(OC, "timestamp")).text = "2026-10-21T00:00:00Z"
    prefix = "oval:scapng.04.variable.value:"
    definition_id = prefix + "def:1"
    defs = ET.SubElement(root, q(OD, "definitions"))
    d = ET.SubElement(defs, q(OD, "definition"), {
        "id": definition_id, "version": str(a["version"]),
        "class": a["class"],
    })
    metadata = ET.SubElement(d, q(OD, "metadata"))
    ET.SubElement(metadata, q(OD, "title")).text = a["assessment_title"]
    ET.SubElement(metadata, q(OD, "description")).text = (
        "Source-backed four-way constant Variable Test semantics")
    criteria = ET.SubElement(d, q(OD, "criteria"), {"operator": "AND"})
    tests = ET.SubElement(root, q(OD, "tests"))
    objs = ET.SubElement(root, q(OD, "objects"))
    states = ET.SubElement(root, q(OD, "states"))
    variable_nodes = ET.SubElement(root, q(OD, "variables"))
    objids, stateids, varids = {}, {}, {}
    for n, name in enumerate(VARIABLE_NAMES, 1):
        varids[name] = prefix + "var:" + str(n)
        objids[name] = prefix + "obj:" + str(n)
        stateids[name] = prefix + "ste:" + str(n)
        variable = variables[name]
        v = ET.SubElement(variable_nodes, q(OD, "constant_variable"), {
            "id": varids[name], "version": str(a["version"]),
            "datatype": "string", "comment": variable["title"],
        })
        for value in variable["expression"]["literal"]:
            ET.SubElement(v, q(OD, "value")).text = value
        obj = ET.SubElement(objs, q(IND, "variable_object"), {
            "id": objids[name], "version": str(a["version"]),
        })
        ET.SubElement(obj, q(IND, "var_ref")).text = varids[name]
        state = ET.SubElement(states, q(IND, "variable_state"), {
            "id": stateids[name], "version": str(a["version"]),
        })
        ET.SubElement(state, q(IND, "value"), {
            "var_ref": varids[name], "var_check": "at least one",
        })
    for n, (name, objvar, statevar) in enumerate(sequence, 1):
        ident = prefix + "tst:" + str(n)
        ET.SubElement(criteria, q(OD, "criterion"), {"test_ref": ident})
        test = ET.SubElement(tests, q(IND, "variable_test"), {
            "id": ident, "version": str(a["version"]),
            "comment": a["tests"][name]["test_title"],
            "check": "at least one",
            "check_existence": "at_least_one_exists",
        })
        ET.SubElement(test, q(IND, "object"), {"object_ref": objids[objvar]})
        ET.SubElement(test, q(IND, "state"), {"state_ref": stateids[statevar]})
    return ET.ElementTree(root), definition_id


def emit_current(document):
    from v04_source_proof_contract import independent_export_view
    return emit(independent_export_view(document))


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--native", type=Path, required=True)
    cli.add_argument("--output", type=Path, required=True)
    args = cli.parse_args()
    tree, _ = emit_current(json.loads(args.native.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
