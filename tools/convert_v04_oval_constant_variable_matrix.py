#!/usr/bin/env python3
"""Source-constrained OVAL constant Variable Tests -> canonical 0.4.0.

Supports two pinned Self-Assertion Definitions exercising integer literals,
multi-value variable references, all four var_check quantifiers and negated
criteria. This is authoring/XSD round-trip work, not scanner execution.
Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
CASES = {
    "oval-def_constant_variable.xml": (
        "oval:org.mitre.oval.test:def:92",
        "57113e1d5991bec0c7cee30d2789ecf9bff5223d2f2ab78900098c187a716e91"),
    "oval_check_enumeration_variable_values.xml": (
        "oval:org.mitre.oval.test:def:170",
        "cb317fa5d8073a9fe994175e4ba270857f4278c3f00bd895096147e962e6e8be"),
}
OPERATIONS = {"equals": "equals", "greater than": "greater_than",
              "less than": "less_than"}
CHECKS = {"all": "all", "at least one": "one_or_more",
          "only one": "one", "none satisfy": "none"}
TEST_REQUIRE = "at_least_one_exists_and_all_match"


def demand(ok, reason):
    if not ok:
        raise ValueError("unproven constant Variable source: " + reason)


def one(parent, namespace, local):
    nodes = parent.findall("{" + namespace + "}" + local)
    demand(len(nodes) == 1, "exactly one " + local)
    return nodes[0]


def index(parent, kind):
    rows = {}
    for node in parent:
        ident = node.get("id")
        demand(ident and ident not in rows, "duplicate/missing " + kind)
        rows[ident] = node
    return rows


def convert(raw, source_name):
    demand(source_name in CASES, "unreviewed original file " + source_name)
    source_id, source_sha = CASES[source_name]
    demand(sha256(raw).hexdigest() == source_sha, "pinned original source SHA")
    root = ET.fromstring(raw)
    demand(root.tag == "{" + OD + "}oval_definitions", "root namespace")
    definitions = index(one(root, OD, "definitions"), "Definition")
    demand(set(definitions) == {source_id}, "Definition identity")
    definition = next(iter(definitions.values()))
    demand(definition.get("class") == "miscellaneous", "Definition class")
    metadata = one(definition, OD, "metadata")
    title = one(metadata, OD, "title").text
    criteria = one(definition, OD, "criteria")
    demand(criteria.get("operator") == "AND" and
           set(criteria.attrib) == {"operator"} and len(criteria) >= 2,
           "flat AND criteria only")

    srcvars = index(one(root, OD, "variables"), "Variable")
    variable_names = {ident: f"source-{i}-variable"
                      for i, ident in enumerate(srcvars, 1)}
    variables = {}
    for ident, var in srcvars.items():
        demand(var.tag == "{" + OD + "}constant_variable" and
               var.get("datatype") == "int" and len(var) >= 1,
               "only nonempty integer constant Variables")
        demand(set(var.attrib) <= {"id", "version", "comment", "datatype"},
               "no unreviewed Variable attributes")
        vals = []
        for value in var:
            demand(value.tag == "{" + OD + "}value" and not value.attrib and
                   value.text is not None, "literal integer Variable value")
            val = int(value.text)
            demand(str(val) == value.text.strip(), "canonical integer literal")
            vals.append(val)
        variables[variable_names[ident]] = {
            "kind": "constant", "datatype": "integer",
            "title": var.get("comment") or variable_names[ident],
            "expression": {"literal": vals},
        }

    source_objects = index(one(root, OD, "objects"), "Object")
    objects = {}
    for ident, obj in source_objects.items():
        demand(obj.tag == "{" + IND + "}variable_object" and len(obj) == 1,
               "direct independent.variable Object required")
        demand(set(obj.attrib) <= {"id", "version", "comment"},
               "no unreviewed Object attributes")
        ref = one(obj, IND, "var_ref")
        demand(not ref.attrib and ref.text in srcvars, "Object Variable reference")
        objects[ident] = variable_names[ref.text]

    source_states = index(one(root, OD, "states"), "State")
    states = {}
    for ident, state in source_states.items():
        demand(state.tag == "{" + IND + "}variable_state" and len(state) == 1
               and state.get("operator", "AND") == "AND" and
               set(state.attrib) <= {"id", "version", "comment", "operator"},
               "simple State")
        field = one(state, IND, "value")
        demand(field.get("datatype") == "int" and
               field.get("operation", "equals") in OPERATIONS and
               set(field.attrib) <= {"datatype", "operation", "var_ref", "var_check"},
               "State integer value/operation")
        operation = OPERATIONS[field.get("operation", "equals")]
        if field.get("var_ref"):
            demand(field.text in (None, "") and field.get("var_ref") in srcvars,
                   "referenced State value")
            check = field.get("var_check", "all")
            demand(check in CHECKS, "OVAL var_check enumeration")
            operand = {"variable": variable_names[field.get("var_ref")]}
            match = {"value_match": CHECKS[check]}
        else:
            demand("var_check" not in field.attrib and field.text is not None,
                   "literal State has no var_check")
            operand = int(field.text)
            demand(str(operand) == field.text.strip(), "canonical State integer")
            match = {}
        states[ident] = {"value": {
            operation: operand, "datatype": "integer",
            **match, "require": TEST_REQUIRE,
        }}

    source_tests = index(one(root, OD, "tests"), "Test")
    tests, expressions, pairs = {}, [], []
    for i, criterion in enumerate(criteria, 1):
        demand(criterion.tag == "{" + OD + "}criterion" and
               set(criterion.attrib) <= {"comment", "test_ref", "negate"} and
               criterion.get("negate", "false") in {"true", "false"},
               "unreviewed criteria expression")
        tid = criterion.get("test_ref")
        demand(tid in source_tests, "missing criterion Test")
        test = source_tests[tid]
        demand(test.tag == "{" + IND + "}variable_test" and
               test.get("check") == "all" and
               test.get("check_existence") == "at_least_one_exists" and
               test.get("state_operator", "AND") == "AND" and
               set(test.attrib) <= {"id", "version", "comment", "check",
                                    "check_existence", "state_operator"} and
               len(test) == 2, "Test existence/check semantics")
        obj = one(test, IND, "object").get("object_ref")
        state = one(test, IND, "state").get("state_ref")
        demand(obj in objects and state in states, "Test Object/State closure")
        name = f"source-{i}-test"
        tests[name] = {
            "test_title": test.get("comment") or name,
            "capability": "variable.value", "variable": objects[obj],
            "states": [states[state]], "reported_elements": "all",
            "require": TEST_REQUIRE,
        }
        expr = {"test": name}
        if criterion.get("negate") == "true":
            expr = {"not": expr}
        expressions.append(expr)
        pairs.append({"source_test": tid, "source_object": obj,
                      "source_state": state, "native_test": name})
    demand(len(tests) == len(source_tests) and len(pairs) == len(source_tests),
           "unused or duplicate original Test")
    assessment = {
        "id": source_name.removesuffix(".xml").replace("_", "-") + "-assessment",
        "version": int(definition.get("version")),
        "assessment_title": title, "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": variables, "tests": tests, "evaluate": {"and": expressions},
    }
    proof = {
        "status": "SOURCE_PINNED_NOT_SCANNER_EQUIVALENCE",
        "source_revision": PIN, "source_file": "agnostic/" + source_name,
        "original_xml_sha256": sha256(raw).hexdigest(),
        "original_definition_id": source_id,
        "original_test_pairings": pairs, "original_variable_count": len(srcvars),
        "native_test_count": len(tests), "scanner_parity": False,
    }
    return {"assessment": assessment}, proof


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--original", required=True, type=Path)
    cli.add_argument("--json", required=True, type=Path)
    cli.add_argument("--report", required=True, type=Path)
    args = cli.parse_args()
    doc, proof = convert(args.original.read_bytes(), args.original.name)
    for target in (args.json, args.report):
        target.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(doc, indent=2) + "\n")
    args.report.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
