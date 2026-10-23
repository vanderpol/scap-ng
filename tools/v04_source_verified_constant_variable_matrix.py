#!/usr/bin/env python3
"""Project original-source-proven integer constant Variable matrices via v0.3.

This is a projection of the mature v0.3 lowered graph. The separately
implemented pinned-original-OVAL importer is used only as a differential
oracle; its emitted executable fields are never copied into the projection.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from convert_v04_oval_constant_variable_matrix import OD, index, one
from v04_native_bundle_compiler import compile_test_instruction


REQUIRE_ALL = "at_least_one_exists_and_all_match"
OPERATIONS = {"equals", "greater_than", "less_than"}
VALUE_MATCHES = {"all", "one_or_more", "one", "none"}


def demand(ok, reason):
    if not ok:
        raise ValueError("v0.3 constant Variable projection drift: " + reason)


def keys(value, expected, context):
    demand(isinstance(value, dict) and set(value) == set(expected),
           context + " field shape")


def expression(expr, mapping):
    if "test" in expr:
        keys(expr, {"test"}, "criterion")
        demand(expr["test"] in mapping, "unknown lowered criterion")
        return {"test": mapping[expr["test"]]}
    keys(expr, {"not"}, "negated criterion")
    return {"not": expression(expr["not"], mapping)}


def project(v003, provenance, original, oracle_proof):
    """Convert the original 0.3 graph, with complete source identity closure."""
    a = v003["assessment"]
    demand(a.get("specification", {}).get("version") == "0.3.0"
           and a.get("mode") == "automated"
           and a.get("class") == "miscellaneous"
           and a.get("purpose") == "assessment"
           and a.get("objects") == {}, "lowered Definition metadata or Objects")

    root = ET.fromstring(original)
    source_vars = index(one(root, OD, "variables"), "Variable")
    source_tests = index(one(root, OD, "tests"), "Test")
    var_bindings = provenance.get("source_variable_bindings", {})
    test_bindings = provenance.get("source_test_bindings", {})
    old_vars, old_tests, old_states = (a.get(x) for x in ("variables", "tests", "states"))
    demand(isinstance(old_vars, dict) and isinstance(old_tests, dict)
           and isinstance(old_states, dict), "missing mature 0.3 lowering")
    demand(set(var_bindings) == set(source_vars)
           and set(var_bindings.values()) == set(old_vars), "Variable source identity closure")
    demand(set(test_bindings) == set(source_tests)
           and set(test_bindings.values()) == set(old_tests), "Test source identity closure")

    var_names = {source_id: f"source-{i}-variable"
                 for i, source_id in enumerate(source_vars, 1)}
    renamed_vars = {var_bindings[source_id]: name
                    for source_id, name in var_names.items()}
    new_vars = {}
    for source_id, new_name in var_names.items():
        old = old_vars[var_bindings[source_id]]
        keys(old, {"kind", "datatype", "title", "expression"}, "Variable")
        keys(old["expression"], {"literal"}, "Variable literal")
        demand(old["kind"] == "constant" and old["datatype"] == "integer"
               and isinstance(old["title"], str), "Variable kind/datatype")
        lowered = old["expression"]["literal"]
        lowered = lowered if isinstance(lowered, list) else [lowered]
        demand(bool(lowered) and all(isinstance(v, str) for v in lowered),
               "integer Variables must be losslessly convertible strings")
        values = [int(v) for v in lowered]
        demand(all(str(v) == s for v, s in zip(values, lowered)),
               "noncanonical integer literal")
        new_vars[new_name] = {**old, "expression": {"literal": values}}

    pairs = oracle_proof.get("original_test_pairings")
    demand(isinstance(pairs, list) and len(pairs) == len(old_tests),
           "independent OVAL source Test count")
    renamed_tests = {}
    new_tests = {}
    used_states = set()
    for pair in pairs:
        keys(pair, {"source_test", "source_object", "source_state", "native_test"},
             "source pairing")
        source_id, name = pair["source_test"], pair["native_test"]
        demand(source_id in test_bindings and name not in new_tests,
               "original Test identity/order")
        old_id = test_bindings[source_id]
        renamed_tests[old_id] = name
        t = old_tests[old_id]
        keys(t, {"test_title", "capability", "states", "reported_elements",
                 "existence", "match", "variable"}, "lowered Test")
        demand(t["capability"] == "variable.value" and t["reported_elements"] == "all"
               and t["existence"] == "one_or_more" and t["match"] == "all"
               and t["variable"] in renamed_vars
               and isinstance(t["states"], list) and len(t["states"]) == 1,
               "Test source quantifier and Variable binding")
        state_id = t["states"][0]
        demand(state_id in old_states, "missing source State")
        used_states.add(state_id)
        state = old_states[state_id]
        keys(state, {"state_title", "capability", "state"}, "lowered State")
        s = state["state"]
        demand(isinstance(s, dict), "State predicate shape")
        keys(s, ({"field", "value", "operation", "datatype", "match", "existence"}
                 | ({"value_match"} if isinstance(s["value"], dict) else set())),
             "State comparison")
        demand(state["capability"] == "variable.value" and s["field"] == "value"
               and s["operation"] in OPERATIONS and s["datatype"] == "integer"
               and s["match"] == "all" and s["existence"] == "one_or_more",
               "State operation/datatype/quantifier")
        if isinstance(s["value"], dict):
            keys(s["value"], {"variable"}, "State var_ref")
            demand(s["value"]["variable"] in renamed_vars
                   and s["value_match"] in VALUE_MATCHES, "State value var_check")
            operand = {"variable": renamed_vars[s["value"]["variable"]]}
            match = {"value_match": s["value_match"]}
        else:
            demand(type(s["value"]) is int, "State integer literal")
            operand, match = s["value"], {}
        new_tests[name] = {
            "test_title": t["test_title"], "capability": "variable.value",
            "variable": renamed_vars[t["variable"]],
            "states": [{"value": {s["operation"]: operand,
                                  "datatype": "integer", **match,
                                  "require": REQUIRE_ALL}}],
            "reported_elements": "all", "require": REQUIRE_ALL,
        }
        compile_test_instruction(name, new_tests[name])
    demand(used_states == set(old_states), "source States not fully consumed")
    old_eval = a.get("evaluate")
    keys(old_eval, {"all"}, "OVAL conjunction")
    demand(len(old_eval["all"]) == len(new_tests), "Test expression count")
    converted_eval = {"and": [expression(expr, renamed_tests)
                              for expr in old_eval["all"]]}
    demand([pair["native_test"] for pair in pairs] ==
           [next(iter(branch.values()))["test"] if "not" in branch else branch["test"]
            for branch in converted_eval["and"]], "criterion order differs from original")
    return {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"], "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": new_vars, "tests": new_tests,
        "evaluate": converted_eval,
    }}
