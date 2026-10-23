#!/usr/bin/env python3
"""Shared-source OVAL -> canonical 0.4 converter integration checkpoint.

The source lowering is the mature 0.3 converter; native 0.4 projection is a
strict, separately checked boundary. Only two independently proven leaf
shapes are admitted for now. This is NOT general OVAL 5.12.3 coverage.

Refs #232 #229 #248.
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from compare_v04_fresh_oval_import import compare as compare_independent
from import_v04_oval_leaf_pilot import convert as independent_leaf_import
from oval_semantic_ir import parse as parse_oval_semantic_ir
from scap_upconvert_v003.build_rhel9_review_slice import lower_definition
from scap_upconvert_v003.convert_collection_review import postprocess_automated_assessment
from v04_field_requirement import promote_test, restore_test
from v04_flat_object_authoring import flatten_document, load_catalog, restore_document
from v04_native_bundle_compiler import compile_test_instruction


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
    exact_keys(entry, {"field", "value", "operation", "datatype",
                       "entity_check", "entity_existence"}, "State predicate")
    require(entry["field"] == field and entry["operation"] == operation
            and entry["datatype"] == "string" and entry["entity_check"] == "all"
            and entry["entity_existence"] == "at_least_one_exists"
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
    require(set(old_test) in ({"test_title", "capability", "object", "check_existence", "check", "reported_elements"},
                              {"test_title", "capability", "object", "check_existence", "check", "states", "reported_elements"}),
            "unsupported Test source attributes")
    require(old_test.get("check_existence") == "at_least_one_exists"
            and old_test.get("reported_elements") == "all", "unproven Test existence/report policy")
    require(not a.get("variables"), "Variables require their own 0.4 semantic proof")
    require(a.get("mode") == "automated" and a.get("class") in {"inventory", "compliance"},
            "unsupported OVAL Definition class")
    require(a.get("specification", {}).get("version") == "0.3.0", "expected aligned 0.3 source")
    require(isinstance(source_obj.get("object_title"), str), "Object title missing")

    if cap == "independent.shellcommand":
        require(old_test.get("check") == "all" and "states" not in old_test,
                "shell Test supports presence only; Filter predicates are separate")
        exact_keys(source_obj, {"capability", "select", "filters", "object_title"}, "shell Object")
        selectors = source_obj["select"]
        exact_keys(selectors, {"shell", "command"}, "shell selectors")
        shell = literal_selector(selectors["shell"], "shell")
        command = literal_selector(selectors["command"], "command")
        require(shell == "powershell" and bool(command), "unsupported shell command source")
        require(len(source_obj["filters"]) == 1, "shell leaf requires one direct Filter")
        fil = source_obj["filters"][0]
        exact_keys(fil, {"action", "state"}, "shell Filter")
        require(fil["action"] == "include", "unproven Filter action")
        state_id, state = only_entry(a.get("states"), "Filter State")
        require(fil["state"] == state_id and state.get("capability") == cap,
                "source Filter State binding mismatch")
        value = scalar_state(state.get("state"), "stdout_line", "case insensitive equals")
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
        require(old_test.get("check") == "only one" and len(old_test.get("states", [])) == 1,
                "unsupported registry Test check or State count")
        exact_keys(source_obj, {"capability", "select", "object_title"}, "registry Object")
        selectors = source_obj["select"]
        exact_keys(selectors, {"hive", "key", "name"}, "registry selectors")
        values = {key: literal_selector(selectors[key], key)
                  for key in ("hive", "key", "name")}
        require(values["hive"] == "HKEY_LOCAL_MACHINE"
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


def convert(source_path: Path, definition_id: str, *, assessment_id=None):
    """Use existing semantic IR + v003 lowering, then fail-closed v04 projection."""
    source_path = Path(source_path)
    original = source_path.read_bytes()
    ir = parse_oval_semantic_ir(source_path)
    require(not ir["unresolved_references"], "unresolved OVAL references")
    definitions = [d for d in ir["definitions"] if d["id"] == definition_id]
    require(len(definitions) == 1 and definitions[0]["deprecated"] not in ("true", "1"),
            "missing or deprecated OVAL Definition")
    # The independent importer remains a temporary two-leaf *scope oracle*;
    # it does not supply native output. Extend this boundary only with new proof.
    independent = independent_leaf_import(original, definition_id, assessment_id=assessment_id)
    ident = independent["assessment"]["id"]
    provenance = {}
    lower, err = lower_definition(ET.fromstring(original), definition_id,
                                  ident, collection_graph=True, provenance=provenance)
    require(err is None, "0.3 source lowering failed: " + str(err))
    aligned, modern = postprocess_automated_assessment(lower, target_ng_version="0.3.0")
    require(modern is None, "unexpected 0.3 modernization")
    native = project_v003_to_v04(aligned)
    # The independent original-OVAL importer predates the final flat Object
    # syntax. Normalize it using the *same invertible* approved 0.4 pass;
    # compare executable fields only after both are in canonical 0.4 grammar.
    independent_flat, flat_proof = flatten_document(independent, flat_catalog())
    require(restore_document(independent_flat, flat_proof) == independent,
            "independent OVAL leaf normalization not invertible")
    compare_independent(native, independent_flat)  # Author identities only ignored.
    evidence = {
        "status": "V003_SHARED_LOWERING_TO_CANONICAL_V04_TWO_LEAF_LOCKSTEP",
        "source_sha256": hashlib.sha256(original).hexdigest(),
        "definition_id": definition_id, "capability": next(iter(native["assessment"]["tests"].values()))["capability"],
        "shared_semantic_ir": ir["ir_version"], "v003_source_lowering_reused": True,
        "v004_flat_and_requirement_inverse_checked": True,
        "independent_leaf_import_agreement": True,
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
