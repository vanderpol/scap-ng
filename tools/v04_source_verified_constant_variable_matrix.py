#!/usr/bin/env python3
"""Project original-source-proven integer constant Variable matrices via v0.3.

This is a projection of the mature v0.3 lowered graph. The separately
implemented pinned-original-OVAL importer is used only as a differential
oracle; its emitted executable fields are never copied into the projection.
"""
from __future__ import annotations

from hashlib import sha256
import xml.etree.ElementTree as ET

from convert_v04_oval_constant_variable_matrix import OD, index, one
from convert_v04_oval_variable_datatype_suite import (
    CASES as DATATYPE_CASES, OD as DATATYPE_OD, IND as DATATYPE_IND,
    NATIVE_DTYPE as DATATYPE_NATIVE, OP as DATATYPE_OPERATIONS,
)
from v04_native_bundle_compiler import compile_test_instruction
from v04_field_requirement import promote_test


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
        new_tests[name], _ = promote_test(new_tests[name], legacy_review=True)
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


# The original OVAL source and independent native 0.4 importer already pin
# these two datatype suites, so this projects the ALIGNED v0.3 graph only.
# More source families require their own typed comparison/lexeme proof.
DATATYPE_REUSE_CASES = frozenset({"oval_boolean_datatype.xml",
                                   "oval_string_datatype.xml",
                                   "oval_int_datatype.xml"})


def _source_tree(node, source_test_names):
    """Reconstruct the original flat/nested AND/NOT graph by original IDs."""
    if node.tag == "{" + DATATYPE_OD + "}criterion":
        demand(set(node.attrib) <= {"comment", "test_ref", "negate"}
               and node.get("test_ref") in source_test_names
               and node.get("negate", "false") in {"true", "false"},
               "original criterion identity/negation")
        leaf = {"test": source_test_names[node.get("test_ref")]}
        return {"not": leaf} if node.get("negate") == "true" else leaf
    demand(node.tag == "{" + DATATYPE_OD + "}criteria"
           and node.get("operator", "AND") == "AND"
           and set(node.attrib) <= {"operator", "comment"}
           and len(node) > 0, "source AND tree shape")
    return {"all": [_source_tree(c, source_test_names) for c in node]}


def _lowered_expression(expr, aliases):
    """Remap the v0.3 expression with no operation or negation collapse."""
    demand(isinstance(expr, dict) and len(expr) == 1, "lowered criteria node")
    kind, value = next(iter(expr.items()))
    if kind == "test":
        demand(value in aliases, "unrecognized lowered Test identity")
        return {"test": aliases[value]}
    if kind == "not":
        return {"not": _lowered_expression(value, aliases)}
    demand(kind == "all" and isinstance(value, list) and bool(value),
           "unproved nested Boolean operator")
    return {"and": [_lowered_expression(part, aliases) for part in value]}


def _source_typed_value(raw, datatype):
    if datatype == "boolean":
        demand(raw in {"true", "false", "1", "0"}, "boolean source lexical form")
        return raw in {"true", "1"}
    if datatype == "int":
        demand(isinstance(raw, str), "integer source lexical form")
        try:
            return int(raw)
        except ValueError as exc:
            raise ValueError("v0.3 constant Variable projection drift: integer lexeme") from exc
    demand(datatype == "string", "only reviewed scalar datatype suites admitted")
    return raw


def project_datatype_suite(v003, provenance, original, source_name):
    """Project reviewed boolean/string suites using v0.3; source attests loss.

    No executable fields are copied from the independent native importer;
    only original literal lexical forms are read where 0.3 normalized a
    boolean (e.g. OVAL ``1`` and ``true`` both become ``True``).
    The caller compares the whole output against that independent importer.
    """
    demand(source_name in DATATYPE_REUSE_CASES, "unreviewed datatype suite")
    did, digest, dtype, ntests = DATATYPE_CASES[source_name]
    demand(sha256(original).hexdigest() == digest, "immutable original OVAL SHA")
    root = ET.fromstring(original)
    demand(root.tag == "{" + DATATYPE_OD + "}oval_definitions", "OVAL namespace")
    source_definitions = index(one(root, DATATYPE_OD, "definitions"), "Definition")
    demand(set(source_definitions) == {did}, "original Definition identity")
    source_variables = index(one(root, DATATYPE_OD, "variables"), "Variable")
    source_objects = index(one(root, DATATYPE_OD, "objects"), "Object")
    source_states = index(one(root, DATATYPE_OD, "states"), "State")
    source_tests = index(one(root, DATATYPE_OD, "tests"), "Test")
    demand(len(source_tests) == ntests, "pinned datatype suite Test count")
    a = v003["assessment"]
    demand(a.get("specification", {}).get("version") == "0.3.0"
           and a.get("mode") == "automated"
           and a.get("class") == "miscellaneous"
           and a.get("purpose") == "assessment"
           and not a.get("objects"), "mature v0.3 source-graph envelope")
    variable_bindings = provenance.get("source_variable_bindings", {})
    test_bindings = provenance.get("source_test_bindings", {})
    old_variables, old_tests, old_states = (a.get(k) for k in
                                             ("variables", "tests", "states"))
    demand(isinstance(old_variables, dict) and isinstance(old_tests, dict)
           and isinstance(old_states, dict)
           and set(variable_bindings) == set(source_variables)
           and set(variable_bindings.values()) == set(old_variables)
           and set(test_bindings) == set(source_tests)
           and set(test_bindings.values()) == set(old_tests),
           "complete original Variable/Test source reference closure")

    var_names = {vid: f"source-{i}-variable"
                 for i, vid in enumerate(source_variables, 1)}
    old_to_native_vars = {variable_bindings[vid]: var_names[vid]
                          for vid in source_variables}
    native_variables = {}
    native_datatype = DATATYPE_NATIVE.get(dtype, dtype)
    for vid, native_name in var_names.items():
        source = source_variables[vid]
        demand(source.tag == "{" + DATATYPE_OD + "}constant_variable"
               and source.get("datatype") == dtype
               and set(source.attrib) <= {"id", "version", "comment", "datatype"}
               and len(source) > 0, "direct source constant Variable")
        old = old_variables[variable_bindings[vid]]
        keys(old, {"kind", "datatype", "title", "expression"}, "v0.3 Variable")
        keys(old["expression"], {"literal"}, "v0.3 Variable literal")
        demand(old["kind"] == "constant" and old["datatype"] == native_datatype,
               "v0.3 Variable datatype/kind")
        lexemes = []
        for node in source:
            demand(node.tag == "{" + DATATYPE_OD + "}value"
                   and not node.attrib and node.text is not None,
                   "source constant literal lexical form")
            lexemes.append(node.text)
        lowered = old["expression"]["literal"]
        lowered = lowered if isinstance(lowered, list) else [lowered]
        demand(len(lowered) == len(lexemes) and
               all(_source_typed_value(s, dtype) == _source_typed_value(v, dtype)
                   for s, v in zip(lexemes, lowered)),
               "mature 0.3 constant literal drift")
        native_variables[native_name] = {**old,
                                         "expression": {"literal": lexemes}}

    test_names = {tid: f"source-{i}-test"
                  for i, tid in enumerate(source_tests, 1)}
    remapped_tests = {test_bindings[sid]: name
                      for sid, name in test_names.items()}
    native_tests = {}
    used_states = set()
    seen_objects = set()
    for source_tid, name in test_names.items():
        source_test = source_tests[source_tid]
        demand(source_test.tag == "{" + DATATYPE_IND + "}variable_test"
               and source_test.get("check") == "at least one"
               and source_test.get("check_existence") == "at_least_one_exists"
               and source_test.get("state_operator", "AND") == "AND"
               and set(source_test.attrib) <= {"id", "version", "comment",
                                               "check", "check_existence", "state_operator"}
               and len(source_test) == 2, "original Test/check semantics")
        original_obj = one(source_test, DATATYPE_IND, "object").get("object_ref")
        original_state = one(source_test, DATATYPE_IND, "state").get("state_ref")
        demand(original_obj in source_objects and original_state in source_states,
               "original Test reference resolution")
        seen_objects.add(original_obj)
        source_object = source_objects[original_obj]
        demand(source_object.tag == "{" + DATATYPE_IND + "}variable_object"
               and len(source_object) == 1, "original direct Variable Object")
        original_var = one(source_object, DATATYPE_IND, "var_ref").text
        demand(original_var in var_names, "original Object Variable reference")
        old_test = old_tests[test_bindings[source_tid]]
        keys(old_test, {"test_title", "capability", "states", "reported_elements",
                        "existence", "match", "variable"}, "v0.3 Test")
        demand(old_test["capability"] == "variable.value"
               and old_test["reported_elements"] == "all"
               and old_test["existence"] == "one_or_more"
               and old_test["match"] == "one_or_more"
               and old_test["variable"] == variable_bindings[original_var]
               and isinstance(old_test["states"], list)
               and len(old_test["states"]) == 1,
               "v0.3 Test quantifier/Variable binding")
        old_state_id = old_test["states"][0]
        demand(old_state_id in old_states, "v0.3 Test State closure")
        used_states.add(old_state_id)
        old_state = old_states[old_state_id]
        keys(old_state, {"state_title", "capability", "state"}, "v0.3 State")
        s = old_state["state"]
        keys(s, {"field", "value", "operation", "datatype", "match", "existence"},
             "v0.3 State scalar predicate")
        source_state = source_states[original_state]
        demand(source_state.tag == "{" + DATATYPE_IND + "}variable_state"
               and len(source_state) == 1, "original scalar State")
        state_value = one(source_state, DATATYPE_IND, "value")
        demand(set(state_value.attrib) <= {"datatype", "operation"}
               and state_value.get("datatype", "string") == dtype
               and state_value.text is not None, "original typed scalar State value")
        original_operation = state_value.get("operation", "equals")
        demand(original_operation in DATATYPE_OPERATIONS,
               "source operation not in reviewed OVAL vocabulary")
        native_operation = DATATYPE_OPERATIONS[original_operation]
        old_operation = ("pattern_match" if native_operation == "matches_regex"
                         else native_operation)
        demand(old_state["capability"] == "variable.value"
               and s["field"] == "value" and s["datatype"] == native_datatype
               and s["operation"] == old_operation
               and s["match"] == "all" and s["existence"] == "one_or_more"
               and s["value"] == _source_typed_value(state_value.text, dtype),
               "mature 0.3 scalar State operation/value drift")
        native_tests[name] = {
            "test_title": old_test["test_title"], "capability": "variable.value",
            "variable": old_to_native_vars[old_test["variable"]],
            "states": [{"value": {native_operation: state_value.text,
                                  "datatype": native_datatype,
                                  "require": REQUIRE_ALL}}],
            "reported_elements": "all",
            "require": "at_least_one_exists_and_some_match",
        }
        native_tests[name], _ = promote_test(native_tests[name], legacy_review=True)
        compile_test_instruction(name, native_tests[name])
    demand(used_states == set(old_states) and seen_objects == set(source_objects),
           "unconsumed source State/Object references")
    source_eval = _source_tree(one(source_definitions[did], DATATYPE_OD, "criteria"),
                               {tid: test_bindings[tid] for tid in source_tests})
    demand(a.get("evaluate") == source_eval,
           "nested/negated OVAL criteria lost by mature 0.3 lowering")
    candidate = {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"], "mode": "automated",
        "class": a["class"], "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": native_variables, "tests": native_tests,
        "evaluate": _lowered_expression(a["evaluate"], remapped_tests),
    }}
    return candidate
