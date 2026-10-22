#!/usr/bin/env python3
"""Pinned original OVAL independent.variable_test -> native variable.value 0.4.

Strictly one original Definition, four distinct Test/Object/State pairings,
two constant string Variables each with four original values. No invented
collection, no eliminated Object/State semantic axes. Ref #248 #228 #229.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from audit_v04_original_oval_variable_test import (
    audit_bytes, tag, BASE, IND, SOURCE, REVISION,
)
from v04_a_authoring_graph_index import canonical_json

SPECS = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
SOURCE_CAP = "variable.value"
VARS = ("first-source-variable", "second-source-variable")
NAMED_TESTS = (
    "first-to-second-variable-test", "second-to-first-variable-test",
    "first-to-first-variable-test", "second-to-second-variable-test",
)
REQUIRE = "at_least_one_exists_and_some_match"
FIELD_REQUIRE = "at_least_one_exists_and_some_match"


def only(parent, local, namespace):
    items = parent.findall(tag(namespace, local))
    if len(items) != 1:
        raise ValueError(f"original {local} cardinality changed")
    return items[0]


def convert(raw):
    source = audit_bytes(raw)
    tree = ET.fromstring(raw)
    variables = list(only(tree, "variables", BASE))
    original_to_native = {
        obj.get("id"): name for obj, name in zip(variables, VARS)
    }
    original_variable_values = {
        item.get("id"): [x.text for x in item]
        for item in variables
    }
    source_objects = {
        x.get("id"): only(x, "var_ref", IND).text
        for x in only(tree, "objects", BASE)
    }
    source_states = {
        x.get("id"): only(x, "value", IND).get("var_ref")
        for x in only(tree, "states", BASE)
    }
    tests = {x.get("id"): x for x in only(tree, "tests", BASE)}
    definition = next(iter(only(tree, "definitions", BASE)))
    criteria = only(definition, "criteria", BASE)
    pairs = []
    authored_tests = {}
    for i, criterion in enumerate(criteria):
        original_id = criterion.get("test_ref")
        src_test = tests[original_id]
        objid = only(src_test, "object", IND).get("object_ref")
        stateid = only(src_test, "state", IND).get("state_ref")
        obj_var = source_objects[objid]
        state_var = source_states[stateid]
        name = NAMED_TESTS[i]
        authored_tests[name] = {
            "test_title": criterion.get("comment") or src_test.get("comment"),
            "capability": SOURCE_CAP,
            "variable": original_to_native[obj_var],
            "states": [{
                "value": {
                    "equals": {"variable": original_to_native[state_var]},
                    "datatype": "string",
                    "value_match": "one_or_more",
                    "require": FIELD_REQUIRE,
                }
            }],
            "reported_elements": "all",
            "require": REQUIRE,
        }
        pairs.append({
            "original_test": original_id, "native_test": name,
            "original_object": objid, "original_state": stateid,
            "original_object_variable": obj_var,
            "original_state_variable": state_var,
            "native_object_variable": original_to_native[obj_var],
            "native_state_variable": original_to_native[state_var],
            "original_test_check": src_test.get("check"),
            "original_existence": src_test.get("check_existence"),
            "original_state_var_check": only(
                next(x for x in only(tree, "states", BASE)
                     if x.get("id") == stateid), "value", IND
            ).get("var_check"),
        })
    assessment = {
        "id": "oval-independent-variable-four-way-assessment",
        "version": int(definition.get("version")),
        "assessment_title": only(
            only(definition, "metadata", BASE), "title", BASE).text,
        "mode": "automated",
        "class": "miscellaneous",
        "purpose": "assessment",
        "specification": SPECS,
        "variables": {
            original_to_native[item.get("id")]: {
                "kind": "constant",
                "datatype": "string",
                "title": item.get("comment") or original_to_native[item.get("id")],
                "expression": {"literal": original_variable_values[item.get("id")]},
            } for item in variables
        },
        "tests": authored_tests,
        "evaluate": {"and": [{"test": name} for name in NAMED_TESTS]},
    }
    if len(assessment["tests"]) != 4 or len(assessment["variables"]) != 2:
        raise ValueError("four original Test/two Variable semantics lost")
    proof = {
        "status": "SOURCE_PINNED_NATIVE_040_VARIABLE_VALUE_CANDIDATE_NOT_SCANNER",
        "original_revision": REVISION,
        "original_path": SOURCE,
        "original_xml_sha256": sha256(raw).hexdigest(),
        "source_graph_status": source["status"],
        "original_definition_id": source["original_definition_id"],
        "native_assessment_sha256": sha256(canonical_json(
            {"assessment": assessment})).hexdigest(),
        "native_capability": SOURCE_CAP,
        "variable_names": original_to_native,
        "test_pairs": pairs,
        "native_schema_validated": False,
        "roundtrip_oval_5123_validated": False,
        "scanner_parity": False,
    }
    return {"assessment": assessment}, proof


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--original", type=Path, required=True)
    cli.add_argument("--json", type=Path, required=True)
    cli.add_argument("--report", type=Path, required=True)
    args = cli.parse_args()
    doc, proof = convert(args.original.read_bytes())
    for target in (args.json, args.report):
        target.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json.dumps(doc, indent=2) + "\n")
    args.report.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in proof.items()
                      if k not in ("test_pairs", "variable_names")}, sort_keys=True))


if __name__ == "__main__":
    main()
