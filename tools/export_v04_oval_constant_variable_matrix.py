#!/usr/bin/env python3
"""Independent native 0.4.0 constant-variable Test -> OVAL 5.12.3 XML.

This exporter reads native authoring only. It rejects unsupported semantics
instead of consulting original XML or guessing how a field should behave.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
SPEC = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
REQUIRE = "at_least_one_exists_and_all_match"
OPERATIONS = {"equals": "equals", "greater_than": "greater than",
              "less_than": "less than"}
CHECKS = {"all": "all", "one_or_more": "at least one",
          "one": "only one", "none": "none satisfy"}
IDS = {"oval-def-constant-variable-assessment": (2, 2),
       "oval-check-enumeration-variable-values-assessment": (2, 10)}


def demand(ok, reason):
    if not ok:
        raise ValueError("unverified native constant Variable export: " + reason)


def q(ns, name):
    return "{" + ns + "}" + name


def emit(document):
    assessment = document.get("assessment") if isinstance(document, dict) else None
    demand(isinstance(assessment, dict) and
           set(assessment) == {"id", "version", "assessment_title", "mode",
                               "class", "purpose", "specification", "variables",
                               "tests", "evaluate"}, "Assessment contract")
    demand(assessment["id"] in IDS and assessment["specification"] == SPEC
           and assessment["mode"] == "automated"
           and assessment["class"] == "miscellaneous"
           and assessment["purpose"] == "assessment"
           and type(assessment["version"]) is int,
           "version/source identity/mode/class")
    variable_count, test_count = IDS[assessment["id"]]
    variables = assessment["variables"]
    tests = assessment["tests"]
    demand(type(variables) is dict and
           list(variables) == [f"source-{i}-variable"
                               for i in range(1, variable_count+1)],
           "Variable identities/ordering")
    demand(type(tests) is dict and
           list(tests) == [f"source-{i}-test" for i in range(1, test_count+1)],
           "Test identities/ordering")
    for name, var in variables.items():
        demand(type(var) is dict and
               set(var) == {"kind", "datatype", "title", "expression"} and
               var["kind"] == "constant" and var["datatype"] == "integer"
               and type(var["title"]) is str
               and type(var["expression"]) is dict
               and set(var["expression"]) == {"literal"}, "constant integer " + name)
        vals = var["expression"]["literal"]
        demand(type(vals) is list and vals and all(type(x) is int for x in vals),
               "integer values " + name)

    expression = assessment["evaluate"]
    demand(type(expression) is dict and set(expression) == {"and"} and
           type(expression["and"]) is list and
           len(expression["and"]) == test_count, "original AND expression")
    negated = []
    for i, node in enumerate(expression["and"], 1):
        name = f"source-{i}-test"
        if node == {"test": name}:
            negated.append(False)
        elif node == {"not": {"test": name}}:
            negated.append(True)
        else:
            raise ValueError("unverified original Test order/negation")

    for prefix, ns in (("oval-def", OD), ("oval", OC), ("ind-def", IND)):
        ET.register_namespace(prefix, ns)
    root = ET.Element(q(OD, "oval_definitions"))
    generator = ET.SubElement(root, q(OD, "generator"))
    ET.SubElement(generator, q(OC, "product_name")).text = (
        "SCAP-NG 0.4 independently exported constant Variable Tests")
    ET.SubElement(generator, q(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, q(OC, "timestamp")).text = "2026-10-21T00:00:00Z"
    prefix = "oval:scapng.04.constant.variable:"
    definition_id = prefix + "def:1"
    defs = ET.SubElement(root, q(OD, "definitions"))
    definition = ET.SubElement(defs, q(OD, "definition"), {
        "id": definition_id, "version": str(assessment["version"]),
        "class": assessment["class"],
    })
    meta = ET.SubElement(definition, q(OD, "metadata"))
    ET.SubElement(meta, q(OD, "title")).text = assessment["assessment_title"]
    ET.SubElement(meta, q(OD, "description")).text = (
        "Native constant Variable semantics exported for OVAL comparison")
    criteria = ET.SubElement(definition, q(OD, "criteria"), {"operator": "AND"})
    out_tests = ET.SubElement(root, q(OD, "tests"))
    out_objects = ET.SubElement(root, q(OD, "objects"))
    out_states = ET.SubElement(root, q(OD, "states"))
    out_vars = ET.SubElement(root, q(OD, "variables"))

    varids, objectids = {}, {}
    for i, (name, var) in enumerate(variables.items(), 1):
        varids[name] = prefix + f"var:{i}"
        objectids[name] = prefix + f"obj:{i}"
        v = ET.SubElement(out_vars, q(OD, "constant_variable"), {
            "id": varids[name], "version": str(assessment["version"]),
            "datatype": "int", "comment": var["title"],
        })
        for value in var["expression"]["literal"]:
            ET.SubElement(v, q(OD, "value")).text = str(value)
        o = ET.SubElement(out_objects, q(IND, "variable_object"), {
            "id": objectids[name], "version": str(assessment["version"]),
        })
        ET.SubElement(o, q(IND, "var_ref")).text = varids[name]

    stateids = {}
    for i, (name, test) in enumerate(tests.items(), 1):
        demand(type(test) is dict and
               set(test) == {"test_title", "capability", "variable", "states",
                             "reported_elements", "require"} and
               type(test["test_title"]) is str and
               test["capability"] == "variable.value" and
               test["variable"] in variables and
               test["reported_elements"] == "all" and
               test["require"] == REQUIRE and
               type(test["states"]) is list and len(test["states"]) == 1 and
               type(test["states"][0]) is dict and
               set(test["states"][0]) == {"value"},
               "Test semantics " + name)
        pred = test["states"][0]["value"]
        demand(type(pred) is dict and pred.get("require") == REQUIRE and
               pred.get("datatype") == "integer", "State field semantics")
        operations = set(pred) & set(OPERATIONS)
        demand(len(operations) == 1 and
               set(pred) <= {"require", "datatype", "value_match"} | set(OPERATIONS),
               "exactly one supported State operation")
        op = next(iter(operations))
        operand = pred[op]
        attrs = {"datatype": "int"}
        if op != "equals":
            attrs["operation"] = OPERATIONS[op]
        if type(operand) is dict:
            demand(set(operand) == {"variable"} and
                   operand["variable"] in variables and
                   pred.get("value_match") in CHECKS,
                   "typed Variable State reference + var_check")
            attrs["var_ref"] = varids[operand["variable"]]
            attrs["var_check"] = CHECKS[pred["value_match"]]
        else:
            demand(type(operand) is int and "value_match" not in pred,
                   "integer scalar State cannot carry var_check")
        key = json.dumps([op, attrs, operand], sort_keys=True)
        if key not in stateids:
            state_id = prefix + f"ste:{len(stateids)+1}"
            stateids[key] = state_id
            state = ET.SubElement(out_states, q(IND, "variable_state"), {
                "id": state_id, "version": str(assessment["version"]),
            })
            field = ET.SubElement(state, q(IND, "value"), attrs)
            if type(operand) is int:
                field.text = str(operand)
        tid = prefix + f"tst:{i}"
        crt = {"test_ref": tid}
        if negated[i-1]:
            crt["negate"] = "true"
        ET.SubElement(criteria, q(OD, "criterion"), crt)
        t = ET.SubElement(out_tests, q(IND, "variable_test"), {
            "id": tid, "version": str(assessment["version"]),
            "comment": test["test_title"], "check": "all",
            "check_existence": "at_least_one_exists",
        })
        ET.SubElement(t, q(IND, "object"), {
            "object_ref": objectids[test["variable"]]})
        ET.SubElement(t, q(IND, "state"), {"state_ref": stateids[key]})
    return ET.ElementTree(root), definition_id


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--native", required=True, type=Path)
    cli.add_argument("--output", required=True, type=Path)
    args = cli.parse_args()
    tree, _ = emit(json.loads(args.native.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
