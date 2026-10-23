#!/usr/bin/env python3
"""Shared-source OVAL -> canonical 0.4 converter integration checkpoint.

The source lowering is the mature 0.3 converter; native 0.4 projection is a
strict, separately checked boundary. Original-source-attested direct
Object-only presence checks extend the two narrow leaf and two pinned
Variable cases. This is NOT general OVAL 5.12.3 coverage.

Refs #232 #229 #248.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from compare_v04_fresh_oval_import import compare as compare_independent
from convert_v04_oval_family_constant_variable import (
    convert as independent_family_import,
    NAME as FAMILY_VARIABLE_NAME,
    TEST_NAME as FAMILY_TEST_NAME,
)
from convert_v04_oval_independent_variable_test import (
    convert as independent_variable_import,
    NAMED_TESTS as VARIABLE_TEST_NAMES,
    VARS as VARIABLE_NAMES,
)
from import_v04_oval_leaf_pilot import convert as independent_leaf_import
from oval_semantic_ir import parse as parse_oval_semantic_ir
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from v04_field_requirement import promote_test, restore_test
from v04_flat_object_authoring import flatten_document, load_catalog, restore_document
from v04_native_bundle_compiler import compile_test_instruction
from v04_source_verified_object_presence import convert as project_object_presence


def require(ok, reason):
    if not ok:
        raise ValueError("Shared 0.3 -> canonical 0.4 converter: " + reason)


def only_entry(entries, name):
    require(isinstance(entries, dict) and len(entries) == 1,
            "exactly one " + name + " supported by initial native adapter")
    return next(iter(entries.items()))


def exact_keys(node, expected, name):
    require(isinstance(node, dict) and set(node) == set(expected),
            f"{name}: unexpected source structure {sorted(node) if isinstance(node, dict) else type(node).__name__}")


def literal_selector(value, field):
    exact_keys(value, {"operation", "datatype", "value"}, field)
    require(value["operation"] == "equals" and value["datatype"] == "string"
            and isinstance(value["value"], str), field + ": not a literal string equality")
    return value["value"]


def scalar_state(entry, field, operation):
    # Mature 0.3 capability mappings canonicalize OVAL entity_check and
    # check_existence into match/existence, and operation into snake_case.
    exact_keys(entry, {"field", "value", "operation", "datatype",
                       "match", "existence"}, "mapped 0.3 State predicate")
    require(entry["field"] == field and entry["operation"] == operation
            and entry["datatype"] == "string" and entry["match"] == "all"
            and entry["existence"] == "one_or_more"
            and isinstance(entry["value"], str),
            "State predicate falls outside proven string/quantifier mapping")
    return entry["value"]


@lru_cache(maxsize=1)
def flat_catalog():
    return load_catalog(Path(__file__).resolve().parents[1] /
                        "schema/v0.4.0/capability-mappings/supported")


def project_v003_to_v04(v003):
    """Project two source-exact aligned 0.3 shapes via existing 0.4 passes."""
    a = v003["assessment"]
    tid, old_test = only_entry(a.get("tests"), "Test")
    require(a.get("evaluate") == {"test": tid}, "only one plain OVAL criterion")
    obj_id = old_test.get("object")
    object_id, source_obj = only_entry(a.get("objects"), "Object")
    require(obj_id == object_id, "Test must reference its unique source Object")
    cap = old_test.get("capability")
    require(source_obj.get("capability") == cap, "Object/Test capability mismatch")
    require(set(old_test) in ({"test_title", "capability", "object", "existence", "match", "reported_elements"},
                              {"test_title", "capability", "object", "existence", "match", "states", "reported_elements"}),
            "unsupported Test source attributes")
    require(old_test.get("existence") == "one_or_more"
            and old_test.get("reported_elements") == "all", "unproven Test existence/report policy")
    require(not a.get("variables"), "Variables require their own 0.4 semantic proof")
    require(a.get("mode") == "automated" and a.get("class") in {"inventory", "compliance"},
            "unsupported OVAL Definition class")
    require(a.get("specification", {}).get("version") == "0.3.0", "expected aligned 0.3 source")
    require(isinstance(source_obj.get("object_title"), str), "Object title missing")

    if cap == "independent.shellcommand":
        require(old_test.get("match") == "all" and "states" not in old_test,
                "shell Test supports presence only; Filter predicates are separate")
        # The *0.3 mapper*, not the original OVAL, wraps a direct-filtered
        # shell Object in a single-operand UNION Set. Verify that synthetic
        # wrapper precisely before rendering the original direct Filter.
        exact_keys(source_obj, {"capability", "set", "object_title"}, "mapped shell Object")
        set_expr = source_obj["set"]
        exact_keys(set_expr, {"operator", "operands"}, "mapped shell Set")
        require(set_expr["operator"] == "union"
                and isinstance(set_expr["operands"], list)
                and len(set_expr["operands"]) == 1, "unproven Set/Filter lowering")
        operand = set_expr["operands"][0]
        exact_keys(operand, {"object", "filters"}, "mapped direct Filter operand")
        inner = operand["object"]
        exact_keys(inner, {"capability", "object_title", "collect"}, "mapped shell leaf")
        require(inner["capability"] == cap and inner["object_title"] == source_obj["object_title"],
                "mapped shell Set/Object identity mismatch")
        selectors = inner["collect"]
        exact_keys(selectors, {"shell", "command", "error_if_exit_status_not_0",
                               "error_if_stderr_exists"}, "mapped shell acquisition")
        shell, command = selectors["shell"], selectors["command"]
        require(shell == "powershell" and bool(command), "unsupported shell command source")
        require(selectors["error_if_exit_status_not_0"] is False
                and selectors["error_if_stderr_exists"] is False,
                "non-default shell error policy")
        require(len(operand["filters"]) == 1, "shell leaf requires one direct Filter")
        fil = operand["filters"][0]
        exact_keys(fil, {"action", "state"}, "shell Filter")
        require(fil["action"] == "include", "unproven Filter action")
        state_id, state = only_entry(a.get("states"), "Filter State")
        require(fil["state"] == state_id and state.get("capability") == cap,
                "source Filter State binding mismatch")
        value = scalar_state(state.get("state"), "stdout_line", "case_insensitive_equals")
        test = {"test_title": old_test["test_title"], "capability": cap,
                "object": {"object_title": source_obj["object_title"],
                           "collect": {"shell": shell, "command": command,
                                       "error_if_exit_status_not_0": False,
                                       "error_if_stderr_exists": False},
                           "filters": [{"include": {"stdout_line": {
                               "require": "at_least_one_exists_and_all_match",
                               "case_insensitive_equals": value}}}]},
                "reported_elements": "all", "require": {"items": "one_or_more"}}
    elif cap == "windows.registry":
        require(old_test.get("match") == "one" and len(old_test.get("states", [])) == 1,
                "unsupported registry Test check or State count")
        exact_keys(source_obj, {"capability", "select", "object_title"}, "registry Object")
        selectors = source_obj["select"]
        exact_keys(selectors, {"hive", "key", "name"}, "registry selectors")
        values = {key: literal_selector(selectors[key], key)
                  for key in ("key", "name")}
        require(selectors["hive"] == "local_machine"
                and bool(values["key"] and values["name"]), "unproven registry selectors")
        state_id, state = only_entry(a.get("states"), "registry State")
        require(old_test["states"] == [state_id] and state.get("capability") == cap,
                "source registry State binding mismatch")
        value = scalar_state(state.get("state"), "value", "equals")
        test = {"test_title": old_test["test_title"], "capability": cap,
                "object": {"object_title": source_obj["object_title"],
                           "select": {"hive": {"equals": "local_machine"},
                                      "key": {"equals": values["key"]},
                                      "name": {"equals": values["name"]}}},
                "states": [{"value": {"require": "at_least_one_exists_and_all_match",
                                      "equals": value}}],
                "reported_elements": "all",
                "require": "at_least_one_exists_and_only_one_matches"}
    else:
        raise ValueError("Shared 0.3 -> canonical 0.4 converter: unproved capability " + str(cap))

    candidate = {"assessment": {
        "id": a["id"], "version": a["version"], "assessment_title": a["assessment_title"],
        "mode": "automated", "class": a["class"],
        "purpose": "applicability" if a["class"] == "inventory" else "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {tid: test}, "evaluate": {"test": tid},
    }}
    flattened, object_proof = flatten_document(candidate, flat_catalog())
    require(len(object_proof["edits"]) == 1 and restore_document(flattened, object_proof) == candidate,
            "0.4 flat Object projection inverse failed")
    updated, requirement_proof = promote_test(flattened["assessment"]["tests"][tid])
    require(restore_test(updated, requirement_proof) == flattened["assessment"]["tests"][tid],
            "0.4 requirement projection inverse failed")
    flattened["assessment"]["tests"][tid] = updated
    compile_test_instruction(tid, updated)  # Same canonical Test check as the 0.4 compiler.
    return flattened


def project_v003_variable_to_v04(v003, provenance, original):
    """Map the mature 0.3 four-way variable graph, never the oracle's output.

    The pinned OVAL source has a dedicated independently audited 0.4 importer;
    it supplies the *scope check* and the external differential, not any
    executable Test, State, or Variable in this projection.
    """
    a = v003["assessment"]
    require(a.get("specification", {}).get("version") == "0.3.0"
            and a.get("mode") == "automated" and a.get("class") == "miscellaneous"
            and a.get("purpose") == "assessment", "unexpected 0.3 variable Definition")
    require(a.get("objects") == {}, "variable.value must bind variables directly")
    old_variables = a.get("variables")
    old_tests = a.get("tests")
    old_states = a.get("states")
    require(isinstance(old_variables, dict) and len(old_variables) == 2
            and isinstance(old_tests, dict) and len(old_tests) == 4
            and isinstance(old_states, dict) and len(old_states) == 2,
            "wrong 0.3 four-way Variable/Test/State graph")

    from audit_v04_original_oval_variable_test import BASE, tag

    tree = ET.fromstring(original)
    variables_node = tree.find(tag(BASE, "variables"))
    definition = tree.find(tag(BASE, "definitions"))
    require(variables_node is not None and definition is not None
            and len(definition) == 1, "unexpected source Variable/Definition scope")
    criteria = definition[0].find(tag(BASE, "criteria"))
    require(criteria is not None and len(criteria) == 4,
            "source criteria not four distinct OVAL Tests")
    source_variables = [v.get("id") for v in variables_node]
    source_test_ids = [entry.get("test_ref") for entry in criteria]
    variable_bindings = provenance.get("source_variable_bindings", {})
    test_bindings = provenance.get("source_test_bindings", {})
    require(set(variable_bindings) == set(source_variables)
            and set(test_bindings) == set(source_test_ids),
            "0.3 lowering omitted/added source identities")
    require(set(variable_bindings.values()) == set(old_variables)
            and set(test_bindings.values()) == set(old_tests),
            "0.3 source identities do not cover the lowered graph")
    require(a.get("evaluate") == {"all": [
        {"test": test_bindings[tid]} for tid in source_test_ids]},
        "OVAL conjunction/order not preserved in 0.3 graph")

    names = {variable_bindings[ident]: name
             for ident, name in zip(source_variables, VARIABLE_NAMES)}
    projected_variables = {}
    for old_id, name in names.items():
        variable = old_variables[old_id]
        exact_keys(variable, {"kind", "datatype", "title", "expression"},
                   "0.3 constant Variable")
        require(variable["kind"] == "constant" and variable["datatype"] == "string"
                and isinstance(variable["title"], str), "unproven Variable type")
        expression = variable["expression"]
        exact_keys(expression, {"literal"}, "0.3 constant Variable expression")
        require(isinstance(expression["literal"], list)
                and len(expression["literal"]) == 4
                and all(isinstance(x, str) for x in expression["literal"]),
                "unproven Variable literal values")
        projected_variables[name] = dict(variable)

    used_states = set()
    projected_tests = {}
    for criterion, new_test_id in zip(criteria, VARIABLE_TEST_NAMES):
        old_test_id = test_bindings[criterion.get("test_ref")]
        old_test = old_tests[old_test_id]
        exact_keys(old_test, {"test_title", "capability", "states", "reported_elements",
                              "existence", "match", "variable"}, "0.3 variable Test")
        require(old_test["capability"] == "variable.value"
                and old_test["reported_elements"] == "all"
                and old_test["existence"] == "one_or_more"
                and old_test["match"] == "one_or_more"
                and old_test["variable"] in names
                and isinstance(old_test["states"], list)
                and len(old_test["states"]) == 1,
                "unproved variable Test binding or source quantifier")
        state_id = old_test["states"][0]
        require(state_id in old_states, "Test references missing 0.3 State")
        used_states.add(state_id)
        state = old_states[state_id]
        exact_keys(state, {"state_title", "capability", "state"}, "0.3 variable State")
        exact_keys(state["state"], {"field", "value", "operation", "datatype",
                                    "match", "value_match", "existence"},
                   "0.3 variable State predicate")
        comparison = state["state"]
        exact_keys(comparison["value"], {"variable"}, "0.3 State Variable reference")
        require(state["capability"] == "variable.value"
                and comparison["field"] == "value"
                and comparison["operation"] == "equals"
                and comparison["datatype"] == "string"
                and comparison["match"] == "all"
                and comparison["value_match"] == "one_or_more"
                and comparison["existence"] == "one_or_more"
                and comparison["value"]["variable"] in names,
                "unproven source State operation or var_check")
        # The requirement aliases have already been independently proved
        # OVAL-roundtrip-equivalent for THIS exact source quantifier tuple.
        projected_tests[new_test_id] = {
            "test_title": criterion.get("comment") or old_test["test_title"],
            "capability": old_test["capability"],
            "variable": names[old_test["variable"]],
            "states": [{"value": {
                "equals": {"variable": names[comparison["value"]["variable"]]},
                "datatype": comparison["datatype"],
                "value_match": comparison["value_match"],
                "require": "at_least_one_exists_and_some_match",
            }}],
            "reported_elements": old_test["reported_elements"],
            "require": "at_least_one_exists_and_some_match",
        }
        compile_test_instruction(new_test_id, projected_tests[new_test_id])
    require(used_states == set(old_states), "unused or missing 0.3 source State")
    return {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"], "mode": "automated",
        "class": a["class"], "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": projected_variables,
        "tests": projected_tests,
        "evaluate": {"and": [{"test": name} for name in VARIABLE_TEST_NAMES]},
    }}


def project_v003_family_to_v04(v003, provenance):
    """Project a single regex-backed family State from the mature 0.3 graph."""
    a = v003["assessment"]
    require(a.get("specification", {}).get("version") == "0.3.0"
            and a.get("mode") == "automated" and a.get("class") == "miscellaneous"
            and a.get("purpose") == "assessment" and a.get("objects") == {},
            "unproven 0.3 independent.family source/empty Object")
    var_id, var = only_entry(a.get("variables"), "constant family Variable")
    tid, old_test = only_entry(a.get("tests"), "independent.family Test")
    state_id, old_state = only_entry(a.get("states"), "independent.family State")
    require(set(provenance.get("source_test_bindings", {}).values()) == {tid}
            and set(provenance.get("source_variable_bindings", {}).values()) == {var_id}
            and len(provenance.get("source_test_bindings", {})) == 1
            and len(provenance.get("source_variable_bindings", {})) == 1,
            "0.3 family Test/Variable source identity dropped")
    require(a.get("evaluate") == {"test": tid}, "family Test Boolean expression changed")
    exact_keys(var, {"kind", "datatype", "title", "expression"}, "0.3 family Variable")
    exact_keys(var["expression"], {"literal"}, "0.3 family Variable expression")
    require(var["kind"] == "constant" and var["datatype"] == "string"
            and isinstance(var["title"], str) and isinstance(var["expression"]["literal"], str)
            and bool(var["expression"]["literal"]), "family Variable must be one string literal")
    exact_keys(old_test, {"test_title", "capability", "states", "reported_elements",
                          "existence", "match"}, "0.3 family Test")
    require(old_test["capability"] == "independent.family"
            and old_test["states"] == [state_id]
            and old_test["reported_elements"] == "all"
            and old_test["existence"] == "one_or_more"
            and old_test["match"] == "one_or_more",
            "family Test quantifier or source State changed")
    exact_keys(old_state, {"state_title", "capability", "state"}, "0.3 family State")
    s = old_state["state"]
    exact_keys(s, {"field", "value", "operation", "datatype", "match",
                   "value_match", "existence"}, "0.3 family State comparison")
    exact_keys(s["value"], {"variable"}, "0.3 family State var_ref")
    require(old_state["capability"] == "independent.family" and s["field"] == "family"
            and s["operation"] == "pattern_match" and s["datatype"] == "string"
            and s["match"] == "all" and s["value_match"] == "all"
            and s["existence"] == "one_or_more" and s["value"]["variable"] == var_id,
            "family State regex/var_check or source var_ref changed")
    native_test = {
        "test_title": old_test["test_title"], "capability": "independent.family",
        "states": [{"family": {
            "matches_regex": {"variable": FAMILY_VARIABLE_NAME},
            "datatype": s["datatype"], "value_match": s["value_match"],
            "require": "at_least_one_exists_and_all_match",
        }}],
        "reported_elements": old_test["reported_elements"],
        "require": "at_least_one_exists_and_some_match",
    }
    compile_test_instruction(FAMILY_TEST_NAME, native_test)
    return {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"],
        "mode": "automated", "class": a["class"], "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": {FAMILY_VARIABLE_NAME: dict(var)},
        "tests": {FAMILY_TEST_NAME: native_test},
        "evaluate": {"test": FAMILY_TEST_NAME},
    }}


def convert(source_path: Path, definition_id: str, *, assessment_id=None):
    """Use existing semantic IR + v003 lowering, then fail-closed v04 projection."""
    source_path = Path(source_path)
    original = source_path.read_bytes()
    mappings = Path(__file__).resolve().parents[1] / "schema/v0.3.0/capability-mappings/supported"
    require((mappings / "independent.shellcommand.json").is_file()
            and (mappings / "independent.family.json").is_file()
            and (mappings / "variable.value.json").is_file()
            and (mappings / "windows.registry.json").is_file(),
            "complete 0.3 capability mapping files required (no unmapped fallback)")
    ir = parse_oval_semantic_ir(source_path)
    require(not ir["unresolved_references"], "unresolved OVAL references")
    definitions = [d for d in ir["definitions"] if d["id"] == definition_id]
    require(len(definitions) == 1 and definitions[0]["deprecated"] not in ("true", "1"),
            "missing or deprecated OVAL Definition")
    variable_source = definition_id == "oval:org.mitre.oval.test:def:538"
    family_source = definition_id == "oval:org.mitre.oval.test:def:95"
    if variable_source:
        # A separately source-audited and source-roundtrip-proved 0.4 adapter.
        independent, independent_proof = independent_variable_import(original)
        require(independent_proof["original_definition_id"] == definition_id,
                "pinned Variable source identity mismatch")
        if assessment_id:
            independent["assessment"]["id"] = assessment_id
    elif family_source:
        independent, independent_proof = independent_family_import(source_path)
        require(independent_proof["original_definition_id"] == definition_id,
                "pinned independent.family Definition identity mismatch")
        if assessment_id:
            independent["assessment"]["id"] = assessment_id
    else:
        # The independently written leaf importer handles its approved source
        # families. Direct Object-only source cases use their own narrow,
        # original-OVAL-verified proof; neither code path asserts scanner parity.
        try:
            independent = independent_leaf_import(original, definition_id,
                                                  assessment_id=assessment_id)
        except ValueError:
            independent = None
    ident = (independent["assessment"]["id"] if independent is not None else
             assessment_id or re.sub(r"[^a-z0-9]+", "-", definition_id.lower()).strip("-")
             + ".assessment")
    provenance = {}
    lower, err = lower_definition(ET.fromstring(original), definition_id,
                                  ident, collection_graph=True, provenance=provenance)
    require(err is None, "0.3 source lowering failed: " + str(err))
    aligned, modern = postprocess_automated_assessment(lower, target_ng_version="0.3.0")
    require(modern is None, "unexpected 0.3 modernization")
    object_presence = independent is None
    native = (project_v003_variable_to_v04(aligned, provenance, original)
              if variable_source else project_v003_family_to_v04(aligned, provenance)
              if family_source else project_object_presence(
                  aligned, original, definition_id, provenance,
                  Path(__file__).resolve().parents[1] /
                  "schema/v0.4.0/capability-mappings/supported", flat_catalog())
              if object_presence else project_v003_to_v04(aligned))
    # The independent original-OVAL importer predates the final flat Object
    # syntax. Normalize it using the *same invertible* approved 0.4 pass;
    # compare executable fields only after both are in canonical 0.4 grammar.
    if variable_source or family_source or object_presence:
        independent_flat = independent
    else:
        independent_flat, flat_proof = flatten_document(independent, flat_catalog())
        require(restore_document(independent_flat, flat_proof) == independent,
                "independent OVAL leaf normalization not invertible")
    if variable_source or family_source:
        # The two-leaf comparator intentionally rejects these distinct source
        # shapes; compare the complete independently generated Assessment.
        require(native == independent_flat,
                "0.3 Variable/Test/State projection differs from independent 0.4 OVAL import")
    elif not object_presence:
        compare_independent(native, independent_flat)  # Author identities only ignored.
    evidence = {
        "status": ("V003_SHARED_LOWERING_TO_CANONICAL_V04_VARIABLE_FOUR_WAY_LOCKSTEP"
                   if variable_source else
                   "V003_SHARED_LOWERING_TO_CANONICAL_V04_FAMILY_VARIABLE_LOCKSTEP"
                   if family_source else
                   "V003_SHARED_LOWERING_TO_CANONICAL_V04_ORIGINAL_OVAL_OBJECT_PRESENCE"
                   if object_presence else
                   "V003_SHARED_LOWERING_TO_CANONICAL_V04_TWO_LEAF_LOCKSTEP"),
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "definition_id": definition_id, "capability": next(iter(native["assessment"]["tests"].values()))["capability"],
        "shared_semantic_ir": ir["ir_version"], "v003_source_lowering_reused": True,
        "v004_flat_and_requirement_inverse_checked": not(variable_source or family_source),
        "independent_leaf_import_agreement": not(variable_source or family_source or object_presence),
        "original_oval_object_presence_attested": object_presence,
        "independent_variable_import_agreement": variable_source,
        "independent_family_import_agreement": family_source,
        "full_oval_coverage": False, "scanner_parity": False,
    }
    return native, evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-xml", required=True, type=Path)
    p.add_argument("--definition-id", required=True)
    p.add_argument("--assessment-id")
    p.add_argument("--output", required=True, type=Path)
    p.add_argument("--evidence", type=Path)
    args = p.parse_args()
    native, evidence = convert(args.source_xml, args.definition_id,
                                assessment_id=args.assessment_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(native, indent=2) + "\n", encoding="utf-8")
    if args.evidence:
        args.evidence.parent.mkdir(parents=True, exist_ok=True)
        args.evidence.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evidence, sort_keys=True))


if __name__ == "__main__":
    main()
