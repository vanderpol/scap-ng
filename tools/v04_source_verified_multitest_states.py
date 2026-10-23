#!/usr/bin/env python3
"""Compose the existing single-Test source proof for flat multi-State ANDs.

Reuses mature 0.3 semantic lowering and the original-OVAL-attested direct
Object/State adapter for each distinct Test. No standalone OVAL converter.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import xml.etree.ElementTree as ET

from v04_flat_object_authoring import flatten_document, restore_document
from v04_native_bundle_compiler import compile_assessment_program
from v04_source_verified_object_presence import (
    OD, child, ensure, source_by_id, convert as project_single,
)


def convert(v003, original, definition_id, provenance, catalog_dir, catalog):
    a = v003["assessment"]
    tests = a.get("tests") or {}
    objects = a.get("objects") or {}
    states = a.get("states") or {}
    ensure(a.get("specification", {}).get("version") == "0.3.0"
           and a.get("mode") == "automated"
           and a.get("class") in {"miscellaneous", "inventory", "compliance"}
           and not a.get("variables") and "shared_objects" not in a
           and 2 <= len(tests) <= 15 and bool(states),
           "multi-State AND requires 2-15 Tests and mapped States, no Variables")

    root = ET.fromstring(original)
    ensure(root.tag == "{" + OD + "}oval_definitions", "not original OVAL")
    definition = source_by_id(root, definition_id)
    ensure(definition.tag == "{" + OD + "}definition"
           and definition.get("deprecated", "false") == "false"
           and definition.get("class") == a["class"]
           and int(definition.get("version", "-1")) == a["version"],
           "source Definition class/version drift")
    criteria = child(definition, "criteria")
    ensure(set(criteria.attrib) <= {"operator"}
           and criteria.get("operator", "AND") == "AND"
           and len(criteria) == len(tests), "Boolean expression not a flat AND")
    original_ids = []
    for c in criteria:
        ensure(c.tag == "{" + OD + "}criterion"
               and set(c.attrib) <= {"comment", "test_ref", "negate"}
               and c.get("negate", "false") == "false" and c.get("test_ref"),
               "non-direct or negated criterion")
        original_ids.append(c.get("test_ref"))
    ensure(len(set(original_ids)) == len(original_ids), "duplicate OVAL Test criteria")
    bindings = provenance.get("source_test_bindings", {})
    ensure(set(bindings) == set(original_ids)
           and set(bindings.values()) == set(tests), "0.3 Test source closure")
    ensure(a.get("evaluate") == {"all": [{"test": bindings[tid]}
                                      for tid in original_ids]},
           "0.3 Test Boolean order/semantics changed")

    collection_bindings = provenance.get("source_collection_bindings", {})
    ensure(isinstance(collection_bindings, dict), "source collection binding shape")
    new_tests = {}
    used_objects, used_states, used_source_objects = set(), set(), set()
    test_order = []
    for oval_test_id in original_ids:
        tid = bindings[oval_test_id]
        old_test = tests[tid]
        ensure(isinstance(old_test, dict), "mapped Test shape")
        old_object_id = old_test.get("object")
        subobjects = {}
        if old_object_id is not None:
            ensure(old_object_id in objects and old_object_id not in used_objects,
                   "shared/missing mapped Object needs separate semantics")
            subobjects[old_object_id] = objects[old_object_id]
            used_objects.add(old_object_id)
        state_ids = old_test.get("states", [])
        ensure(isinstance(state_ids, list) and len(state_ids) <= 1
               and all(s in states for s in state_ids),
               "one source scalar State per Test is the proven boundary")
        sub_states = {s: states[s] for s in state_ids}
        used_states.update(state_ids)
        original_test = source_by_id(root, oval_test_id)
        ensure(len(original_test) >= 1 and original_test[0].tag.rsplit("}", 1)[-1]
               == "object" and "object_ref" in original_test[0].attrib,
               "source Test lacks directly referenced original Object")
        source_object_id = original_test[0].get("object_ref")
        ensure(source_object_id in collection_bindings
               and source_object_id not in used_source_objects,
               "missing/shared original Object binding")
        used_source_objects.add(source_object_id)
        sub = deepcopy(v003)
        suba = sub["assessment"]
        suba["tests"] = {tid: old_test}
        suba["objects"] = subobjects
        suba["states"] = sub_states
        suba["evaluate"] = {"test": tid}
        sub_provenance = {
            "source_test_bindings": {oval_test_id: tid},
            "source_collection_bindings": {
                source_object_id: collection_bindings[source_object_id]},
        }
        leaf = project_single(sub, original, definition_id, sub_provenance,
                              Path(catalog_dir), catalog,
                              source_criterion_ref=oval_test_id)
        leaf_tests = leaf["assessment"]["tests"]
        ensure(len(leaf_tests) == 1, "source Test was not projected once")
        name, result = next(iter(leaf_tests.items()))
        ensure(name not in new_tests, "native Test ID collision")
        new_tests[name] = result
        test_order.append(name)
    ensure(used_objects == set(objects) and used_states == set(states)
           and used_source_objects == set(collection_bindings),
           "0.3 source Object/State closure changed")

    candidate = {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"], "mode": "automated",
        "class": a["class"], "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": new_tests,
        "evaluate": {"and": [{"test": name} for name in test_order]},
    }}
    flat, inverse = flatten_document(candidate, catalog)
    ensure(not inverse["edits"] and restore_document(flat, inverse) == candidate,
           "multi-Test projection not native flat 0.4 grammar")
    program = compile_assessment_program(candidate["assessment"])
    ensure(len(program["test_instructions"]) == len(tests),
           "multi-State source Test lost during native compilation")
    return candidate
