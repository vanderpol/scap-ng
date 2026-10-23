#!/usr/bin/env python3
"""Narrow original-OVAL-verified 0.3 -> 0.4 direct Object/Test bridge.

The mature 0.3 lowering supplies the entire authoring graph. The original
OVAL XML independently attests its direct Test, Object, selector values and
check_existence, plus a supported singleton scalar State if present.
Unsupported semantics fail closed. This is a converter
coverage proof, not a scanner six-state equivalence claim.

Refs #232 #248 #229.
"""
from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from import_v04_oval_leaf_pilot import slug
from v04_flat_object_authoring import flatten_document, restore_document
from v04_native_bundle_compiler import compile_test_instruction


OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
SOURCE_EXISTENCE = {
    "any_exist": ("optional", "may_be_absent"),
    "at_least_one_exists": ("one_or_more", "one_or_more"),
    "none_exist": ("none", "none"),
    "only_one_exists": ("one", "exactly_one"),
}
SOURCE_OPERATIONS = {"equals": ("equals", "equals"),
                     "pattern match": ("pattern_match", "matches_regex")}
SOURCE_ITEM_CHECK = {"all": "all", "at least one": "one_or_more"}
VERSION_OPERATIONS = {"greater than": ("greater_than", "version_greater_than"),
                      "greater than or equal": ("greater_than_or_equal",
                                                "version_greater_than_or_equal"),
                      "less than": ("less_than", "version_less_than"),
                      "less than or equal": ("less_than_or_equal",
                                             "version_less_than_or_equal"),
                      "equals": ("equals", "version_equals")}


def ensure(condition, reason):
    if not condition:
        raise ValueError("Direct Object/Test original OVAL source proof: " + reason)


def one(source, kind):
    ensure(isinstance(source, dict) and len(source) == 1,
           "expected precisely one " + kind)
    return next(iter(source.items()))


def source_by_id(root, reference):
    matched = [node for node in root.iter() if node.get("id") == reference]
    ensure(len(matched) == 1, "missing or duplicate OVAL ID " + str(reference))
    return matched[0]


def child(node, name):
    matched = [entry for entry in node if entry.tag == "{" + OD + "}" + name]
    ensure(len(matched) == 1, "expected one " + name)
    return matched[0]


def convert(v003, source_xml, definition_id, provenance, catalog_dir, catalog):
    """Reconcile one direct Test + Object and zero/one scalar State with OVAL."""
    a = v003["assessment"]
    ensure(a.get("specification", {}).get("version") == "0.3.0"
           and a.get("mode") == "automated"
           and a.get("class") in {"miscellaneous", "inventory", "compliance"},
           "unexpected 0.3 assessment envelope")
    ensure(not a.get("variables") and "shared_objects" not in a,
           "Variable/shared Object graph not supported")
    with_state = bool(a.get("states"))
    if with_state:
        state_id, old_state = one(a.get("states"), "mapped scalar State")
        expected_test_keys = {"test_title", "capability", "object", "states",
                              "reported_elements", "existence", "match"}
    else:
        state_id, old_state = None, None
        expected_test_keys = {"test_title", "capability", "object",
                              "reported_elements", "existence", "match"}
    test_id, old_test = one(a.get("tests"), "mapped Test")
    singleton = not a.get("objects")
    if singleton:
        object_id, old_object = None, None
        expected_test_keys.discard("object")
        ensure(with_state, "objectless direct Test requires a State")
    else:
        object_id, old_object = one(a.get("objects"), "mapped Object")
    ensure(a.get("evaluate") == {"test": test_id} and
           set(old_test) == expected_test_keys
           and (singleton or old_test["object"] == object_id)
           and old_test["reported_elements"] == "all"
           and old_test["match"] in SOURCE_ITEM_CHECK.values(),
           "unsupported Test graph/check")
    if with_state:
        ensure(old_test["states"] == [state_id]
               and old_test["existence"] == "one_or_more"
               and set(old_state) == {"state_title", "capability", "state"}
               and old_state["capability"] == old_test["capability"],
               "unsupported State reference/existence")
    if not singleton:
        ensure(set(old_object) == {"capability", "object_title", "select"}
               and old_object["capability"] == old_test["capability"]
               and (old_object["object_title"] is None or
                    isinstance(old_object["object_title"], str)),
               "unsupported Object graph")
    capability = old_test["capability"]
    catalog_path = catalog_dir / (capability + ".json")
    ensure(catalog_path.is_file() and capability in catalog,
           "unmapped source capability")
    mapping = json.loads(catalog_path.read_text(encoding="utf-8"))
    source = mapping["source"]
    renames = mapping["native"].get("selector_map", {})
    if singleton:
        ensure(mapping["native"].get("test_source", {}).get("kind") == "none"
               and mapping.get("migration_crosswalk", {}).get("object", {}).get(
                   source["object"]) == "omitted_native_singleton_system_source",
               "source Object is not an explicitly declared singleton capability")

    root = ET.fromstring(source_xml)
    ensure(root.tag == "{" + OD + "}oval_definitions", "not OVAL Definitions")
    original_definition = source_by_id(root, definition_id)
    ensure(original_definition.tag == "{" + OD + "}definition"
           and original_definition.get("deprecated", "false") == "false"
           and original_definition.get("class") == a["class"]
           and int(original_definition.get("version", "-1")) == a["version"],
           "OVAL Definition class/version/deprecation changed")
    title = child(child(original_definition, "metadata"), "title")
    ensure(title.text is not None and title.text.strip() == a["assessment_title"],
           "Definition metadata title differs from 0.3 lowering")
    criteria = child(original_definition, "criteria")
    ensure(set(criteria.attrib) <= {"operator"}
           and criteria.get("operator", "AND") == "AND"
           and len(criteria) == 1, "nontrivial source criteria")
    criterion = criteria[0]
    ensure(criterion.tag == "{" + OD + "}criterion"
           and set(criterion.attrib) <= {"test_ref", "comment", "negate"}
           and criterion.get("negate", "false") == "false", "non-direct criterion")
    oval_test_id = criterion.get("test_ref")
    ensure(provenance.get("source_test_bindings") == {oval_test_id: test_id},
           "source Test identity lost by 0.3 lowering")
    original_test = source_by_id(root, oval_test_id)
    namespace = source["namespace"]
    ensure(original_test.tag == "{" + namespace + "}" + source["test"]
           and set(original_test.attrib) <= {
               "id", "version", "comment", "check_existence", "check"}
           and original_test.get("comment") == old_test["test_title"]
           and original_test.get("check", "all") in SOURCE_ITEM_CHECK
           and SOURCE_ITEM_CHECK[original_test.get("check", "all")] == old_test["match"]
           and original_test.get("version") is not None,
           "source Test type/title/check/options changed")
    original_existence = original_test.get("check_existence", "at_least_one_exists")
    ensure(original_existence in SOURCE_EXISTENCE,
           "unproven OVAL check_existence " + original_existence)
    mapped_existence, native_existence = SOURCE_EXISTENCE[original_existence]
    ensure(old_test["existence"] == mapped_existence,
           "0.3 Test existence differs from original OVAL")
    ensure(len(original_test) == (2 if with_state else 1)
           and original_test[0].tag in {"{" + OD + "}object", "{" + namespace + "}object"}
           and set(original_test[0].attrib) == {"object_ref"},
           "source Test uses unsupported Object/State structure")
    if with_state:
        ensure(original_test[1].tag in {"{" + OD + "}state", "{" + namespace + "}state"}
               and set(original_test[1].attrib) == {"state_ref"},
               "source Test State binding not direct")
    original_object_id = original_test[0].get("object_ref")
    source_bindings = provenance.get("source_collection_bindings", {})
    ensure(set(source_bindings) == {original_object_id}
           and len(set(source_bindings.values())) == 1,
           "0.3 source Object reference was not uniquely bound")
    original_object = source_by_id(root, original_object_id)
    ensure(original_object.tag == "{" + namespace + "}" + source["object"]
           and set(original_object.attrib) <= {"id", "version", "comment"}
           and (singleton or original_object.get("comment") == old_object["object_title"])
           and original_object.get("version") is not None,
           "source Object type/title/attributes changed")
    source_selectors = {} if singleton else old_object["select"]
    ensure((singleton and len(original_object) == 0) or
           (isinstance(source_selectors, dict) and bool(source_selectors)
            and len(source_selectors) == len(original_object)
            and len(source_selectors) == len(set(source_selectors))
            and set(source_selectors) <= set(renames)),
           "source Object not an empty singleton or direct scalar selectors")
    obj = {}
    if not singleton and old_object["object_title"] is not None:
        obj["object_title"] = old_object["object_title"]
    for node in original_object:
        field = node.tag.rsplit("}", 1)[-1]
        ensure(node.tag == "{" + namespace + "}" + field
               and field in source_selectors and field in renames
               and not list(node) and set(node.attrib) <= {"operation", "datatype"}
               and node.get("datatype", "string") == "string"
               and "var_ref" not in node.attrib,
               "OVAL Object has unsupported selector/behaviors/filter/set")
        operation = node.get("operation", "equals")
        ensure(operation in SOURCE_OPERATIONS,
               "unmapped original selector operation " + operation)
        old_operation, native_operation = SOURCE_OPERATIONS[operation]
        original_value = node.text or ""
        ensure(source_selectors[field] == {
            "operation": old_operation, "datatype": "string", "value": original_value},
            "0.3 selector/operation/value drift from original OVAL")
        native_name = renames[field]
        ensure(native_name in catalog[capability]["selectors"]
               and native_name not in obj, "selector native mapping collided")
        obj[native_name] = {native_operation: original_value}

    native_states = None
    if with_state:
        original_state = source_by_id(root, original_test[1].get("state_ref"))
        ensure(original_state.tag == "{" + namespace + "}" + source["state"]
               and set(original_state.attrib) <= {"id", "version", "comment"}
               and original_state.get("version") is not None
               and original_state.get("comment") == old_state["state_title"]
               and len(original_state) == 1,
               "source State title/type or scalar cardinality changed")
        element = original_state[0]
        old_field = old_state["state"]
        ensure(isinstance(old_field, dict) and
               set(old_field) == {"field", "value", "operation", "datatype", "match", "existence"}
               and isinstance(old_field["value"], str),
               "mapped State must be one literal scalar comparison")
        field = element.tag.rsplit("}", 1)[-1]
        rename = mapping["native"].get("state_field_map", {})
        datatype = element.get("datatype", "string")
        ensure(datatype in {"string", "version"} and
               element.tag == "{" + namespace + "}" + field
               and field in rename and rename[field] == old_field["field"]
               and not list(element)
               and set(element.attrib) <= {"operation", "datatype", "entity_check",
                                          "entity_existence"}
               and element.get("entity_check", "all") == "all"
               and element.get("entity_existence", "at_least_one_exists") ==
                   "at_least_one_exists"
               and old_field["datatype"] == datatype
               and old_field["match"] == "all"
               and old_field["existence"] == "one_or_more"
               and (element.text or "") == old_field["value"],
               "source State field/existence/check/value mismatch")
        operation = element.get("operation", "equals")
        operation_map = SOURCE_OPERATIONS if datatype == "string" else VERSION_OPERATIONS
        ensure(operation in operation_map
               and old_field["operation"] == operation_map[operation][0],
               "source State operation lost by mature 0.3 lowering")
        native_states = [{rename[field]: {
            "require": "at_least_one_exists_and_all_match",
            operation_map[operation][1]: old_field["value"]}}]

    native_id = slug(old_test["test_title"])
    native_test = {
        "test_title": old_test["test_title"], "capability": capability,
        "reported_elements": "all",
        "require": ({"items": native_existence} if not with_state else
                    "at_least_one_exists_and_" +
                    ("all_match" if old_test["match"] == "all" else "some_match")),
    }
    if not singleton:
        native_test["object"] = obj
    if native_states is not None:
        native_test["states"] = native_states
    candidate = {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"],
        "mode": "automated", "class": a["class"],
        "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": {native_id: native_test},
        "evaluate": {"test": native_id},
    }}
    # Invertible no-op here proves we have already emitted the native flat
    # grammar: neither source wrappers nor hidden collection containers remain.
    flattened, proof = flatten_document(candidate, catalog)
    ensure(not proof["edits"] and restore_document(flattened, proof) == candidate,
           "flat 0.4 projection source reconstruction failed")
    compiled = compile_test_instruction(native_id, candidate["assessment"]["tests"][native_id])
    ensure(compiled["opcode"] == ("CHECK_SOURCE_EXACT_STATES" if with_state else
                                  "CHECK_COLLECTION_PRESENCE"),
           "0.4 compiler dropped source-exact Test/State semantics")
    return candidate
