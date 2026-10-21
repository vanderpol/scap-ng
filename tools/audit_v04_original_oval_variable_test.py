#!/usr/bin/env python3
"""Pinned OVAL 5.12.3 independent.variable_test source contract audit.

The original Self-Assertion fixture contains four Test/Object/State pairings,
two 4-value constant Variables, and distinct Test and state var_check axes.
This is a prerequisite for a correct 0.4 capability/importer, NOT a conversion
or runtime parity claim. Refs #248 #228 #229.
"""
from __future__ import annotations
from hashlib import sha256
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse

BASE = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = BASE + "#independent"
SOURCE = "agnostic/ind-def_variable_test.xml"
REVISION = "e3538595c5083b9c34d937a81d319234df9bbfaa"


def tag(ns, name):
    return "{" + ns + "}" + name


def require(ok, name):
    if not ok:
        raise ValueError("source variable_test contract changed: " + name)


def one(node, name, ns):
    found = node.findall(tag(ns, name))
    require(len(found) == 1, name + " cardinality")
    return found[0]


def keyed(node):
    result = {}
    for item in node:
        ident = item.get("id")
        require(ident and ident not in result, "duplicate/missing OVAL identity")
        result[ident] = item
    return result


def audit_bytes(xml):
    root = ET.fromstring(xml)
    require(root.tag == tag(BASE, "oval_definitions"), "root namespace")
    defs = keyed(one(root, "definitions", BASE))
    tests = keyed(one(root, "tests", BASE))
    objects = keyed(one(root, "objects", BASE))
    states = keyed(one(root, "states", BASE))
    variables = keyed(one(root, "variables", BASE))
    require(len(defs) == 1 and len(tests) == 4 and
            len(objects) == 2 and len(states) == 2 and len(variables) == 2,
            "pinned source graph population")
    did, definition = next(iter(defs.items()))
    require(did == "oval:org.mitre.oval.test:def:538" and
            definition.get("class") == "miscellaneous",
            "source definition identity/class")
    criteria = one(definition, "criteria", BASE)
    require(criteria.get("operator") == "AND" and len(criteria) == 4,
            "OVAL Boolean operator/cardinality")
    order = []
    for entry in criteria:
        require(entry.tag == tag(BASE, "criterion") and
                entry.get("test_ref") in tests and
                entry.get("negate", "false") == "false",
                "OVAL Test criteria closure")
        order.append(entry.get("test_ref"))
    require(len(set(order)) == 4, "duplicate criterion")
    vars_info = {}
    for ident, var in variables.items():
        require(var.tag == tag(BASE, "constant_variable") and
                var.get("datatype") == "string", "constant string Variable")
        values = [v.text for v in var]
        require(len(values) == 4 and all(isinstance(x, str) for x in values),
                "exact four original constant values")
        vars_info[ident] = values
    require(len({tuple(v) for v in vars_info.values()}) == 1,
            "source Variable value populations unexpectedly differ")
    object_refs = {}
    for oid, obj in objects.items():
        require(obj.tag == tag(IND, "variable_object") and len(obj) == 1,
                "independent.variable Object shape")
        ref = one(obj, "var_ref", IND).text
        require(ref in vars_info, "Object var_ref missing constant Variable")
        object_refs[oid] = ref
    require(len(set(object_refs.values())) == 2,
            "Object Variable source identities collapsed")
    state_refs = {}
    for sid, state in states.items():
        require(state.tag == tag(IND, "variable_state") and len(state) == 1,
                "independent.variable State shape")
        value = one(state, "value", IND)
        require(value.get("var_ref") in vars_info and
                value.get("var_check") == "at least one" and
                value.text in (None, ""), "original var_check or State value")
        state_refs[sid] = value.get("var_ref")
    require(len(set(state_refs.values())) == 2,
            "State Variable identities collapsed")
    pairs = []
    for tid in order:
        test = tests[tid]
        require(test.tag == tag(IND, "variable_test") and
                test.get("check_existence") == "at_least_one_exists" and
                test.get("check") == "at least one" and len(test) == 2,
                "OVAL Test semantics changed")
        objref = one(test, "object", IND).get("object_ref")
        stateref = one(test, "state", IND).get("state_ref")
        require(objref in object_refs and stateref in state_refs,
                "source Object/State reference unresolved")
        pairs.append((object_refs[objref], state_refs[stateref]))
    require(len(set(pairs)) == 4 and len({a for a, _ in pairs}) == 2
            and len({b for _, b in pairs}) == 2,
            "four distinct cross-Variable comparisons lost")
    require(set(pairs) == {(a,b) for a in vars_info for b in vars_info},
            "source requires all four Object/State Variable combinations")
    return {
        "status": "PINNED_OVAL_VARIABLE_TEST_SOURCE_GRAPH_CLOSED_NOT_NATIVE",
        "original_repository": "OVAL-Community/SCAP-Self-Assertion",
        "original_revision": REVISION,
        "original_path": SOURCE,
        "original_xml_sha256": sha256(xml).hexdigest(),
        "original_definition_id": did,
        "test_check": "at least one",
        "test_check_existence": "at_least_one_exists",
        "state_var_check": "at least one",
        "test_count": len(tests),
        "object_count": len(objects),
        "state_count": len(states),
        "constant_variable_count": len(vars_info),
        "variable_value_counts": sorted(len(x) for x in vars_info.values()),
        "cross_variable_comparisons": len(pairs),
        "comparisons": [
            {"test_id": tid, "object_variable": a, "state_variable": b}
            for tid, (a,b) in zip(order,pairs)
        ],
        "native_040_variable_capability": "NOT_YET_MAPPED",
        "native_040_schema": "NOT_TESTED",
        "oval_to_native_to_xml_roundtrip": "NOT_TESTED",
        "scanner_parity": False,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--original", required=True, type=Path)
    ap.add_argument("--report", required=True, type=Path)
    args=ap.parse_args()
    row=audit_bytes(args.original.read_bytes())
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(row, indent=2, sort_keys=True) + "\n")
    print(json.dumps({key:val for key,val in row.items()
                      if key != "comparisons"}, sort_keys=True))


if __name__ == "__main__":
    main()
