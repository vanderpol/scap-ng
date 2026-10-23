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
from hashlib import sha256
from pathlib import Path
import xml.etree.ElementTree as ET

from import_v04_oval_leaf_pilot import slug
from v04_flat_object_authoring import flatten_document, restore_document
from v04_native_bundle_compiler import compile_test_instruction


OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
APPARMOR_DEFINITION = "oval:com.jovalcm.test:def:967"
APPARMOR_SOURCE_SHA256 = "1e9b6d6bab5a40226db960cebf08c8124282b86e8b0c52316027d48b2c97a5d6"
APPARMOR_TEST = "oval:com.jovalcm.test:tst:1766"
APPARMOR_OBJECT = "oval:com.jovalcm.test:obj:1137"
APPARMOR_STATE = "oval:com.jovalcm.test:ste:1660"
# These additions attest only the immutable original graphs, not arbitrary
# environmentvariable58/uname constructs. Reuse existing capability mappings.
PINNED_DIRECT_SOURCES = {
    "oval:org.mitre.oval.test:def:354": "c6ac03ec0d2745e3545d16cb3fba38e8b7486cbbbb39c03edf5fa27960d49c73",
    "oval:navy.navwar.niwcatlantic.scc.test:def:932": "3c175c94a1a43a17049d39002f95d8e3ed9143eb943c76c47047f1f535c7c070",
}
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


def direct_selectors(original_object, old_object, namespace, capability, mapping, catalog):
    """Map direct scalar OVAL selectors, asserting all 0.3 operands exactly."""
    renames = mapping["native"].get("selector_map", {})
    ensure(set(old_object) == {"capability", "object_title", "select"}
           and old_object["capability"] == capability
           and (old_object["object_title"] is None or
                isinstance(old_object["object_title"], str))
           and original_object.get("comment") == old_object["object_title"],
           "original Object/0.3 mapped Object identity differs")
    source_selectors = old_object["select"]
    ensure(isinstance(source_selectors, dict) and bool(source_selectors)
           and len(source_selectors) == len(original_object)
           and set(source_selectors) <= set(renames),
           "source Object not direct mapped scalar selectors")
    obj = {}
    if old_object["object_title"] is not None:
        obj["object_title"] = old_object["object_title"]
    for node in original_object:
        if capability == "independent.environmentvariable58":
            # Caller has attested the immutable Definition/source. Verify every
            # operand against mature lowering before rendering existing grammar.
            field = node.tag.rsplit("}", 1)[-1]
            old = source_selectors.get(field)
            if node.get("{http://www.w3.org/2001/XMLSchema-instance}nil") == "true":
                ensure(field == "pid" and old is None and node.text is None,
                       "nil PID differs from 0.3 selector")
                obj[renames[field]] = None
                continue
            op = node.get("operation", "equals").replace(" ", "_")
            dtype = "integer" if node.get("datatype") == "int" else "string"
            value = int(node.text) if dtype == "integer" else node.text
            ensure(old == {"operation": op, "datatype": dtype, "value": value},
                   "environment selector differs from mature lowering")
            obj[renames[field]] = {("matches_regex" if op == "pattern_match" else op): old["value"]}
            continue
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
    return obj


def convert(v003, source_xml, definition_id, provenance, catalog_dir, catalog,
            *, source_criterion_ref=None):
    """Reconcile one source Test/Object and optional scalar State with OVAL.

    A selected criterion of a verified flat AND allows the multi-Test adapter
    to reuse this complete leaf proof without synthesizing altered source XML.
    The caller must separately prove whole-graph criterion and reference
    closure; the selected Test still comes directly from original source.
    """
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
    apparmor = capability == "linux.apparmorstatus"
    uname = capability == "unix.uname"
    environment = capability == "independent.environmentvariable58"
    if uname or environment:
        ensure(definition_id in PINNED_DIRECT_SOURCES
               and sha256(source_xml).hexdigest() == PINNED_DIRECT_SOURCES[definition_id],
               "unproved environmentvariable58/uname source SHA/Definition")
    if apparmor:
        # Integer singleton support is attested for precisely this original
        # graph, not a general integer-State or singleton-shape expansion.
        ensure(definition_id == APPARMOR_DEFINITION and source_criterion_ref is None
               and sha256(source_xml).hexdigest() == APPARMOR_SOURCE_SHA256,
               "pinned AppArmor source SHA/Definition differs")
        ensure(set(a) == {"id", "version", "assessment_title", "mode", "class", "purpose",
                          "specification", "objects", "states", "tests", "evaluate"}
               and a["objects"] == {} and a["purpose"] == "assessment"
               and a["specification"] == {"id": "scap-ng.pre-alpha.assessment", "version": "0.3.0"}
               and singleton and with_state,
               "pinned AppArmor lowered Assessment graph changed")
        ensure(provenance.get("source_definition") == APPARMOR_DEFINITION
               and provenance.get("source_variable_bindings") == {}
               and provenance.get("source_collection_bindings") == {
                   APPARMOR_OBJECT: "singleton-apparmorstatus-object-collection"},
               "pinned AppArmor source provenance changed")
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
    if apparmor:
        ensure(all(len(child(root, section)) == 1 for section in
                   ("definitions", "tests", "objects", "states"))
               and root.find("{" + OD + "}variables") is None,
               "pinned AppArmor source graph population differs")
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
           and criteria.get("operator", "AND") == "AND", "non-AND source criteria")
    if source_criterion_ref is None:
        ensure(len(criteria) == 1, "nontrivial source criteria")
        criterion = criteria[0]
    else:
        ensure(len(criteria) >= 2, "selected criterion is not a multi-Test AND")
        chosen = [c for c in criteria if c.get("test_ref") == source_criterion_ref]
        ensure(len(chosen) == 1 and all(
            c.tag == "{" + OD + "}criterion"
            and set(c.attrib) <= {"test_ref", "comment", "negate"}
            and c.get("negate", "false") == "false" and c.get("test_ref")
            for c in criteria), "selected source criterion not uniquely present in flat AND")
        criterion = chosen[0]
    ensure(criterion.tag == "{" + OD + "}criterion"
           and set(criterion.attrib) <= {"test_ref", "comment", "negate"}
           and criterion.get("negate", "false") == "false", "non-direct criterion")
    oval_test_id = criterion.get("test_ref")
    ensure(provenance.get("source_test_bindings") == {oval_test_id: test_id},
           "source Test identity lost by 0.3 lowering")
    if apparmor:
        ensure(oval_test_id == APPARMOR_TEST, "pinned AppArmor Test identity differs")
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
    if apparmor:
        ensure(original_object_id == APPARMOR_OBJECT
               and original_test[1].get("state_ref") == APPARMOR_STATE,
               "pinned AppArmor Object/State reference differs")
    if singleton:
        ensure(len(original_object) == 0, "native singleton has unexpected source fields")
        obj = {}
    else:
        obj = direct_selectors(original_object, old_object, namespace,
                               capability, mapping, catalog)

    native_states = None
    if with_state:
        original_state = source_by_id(root, original_test[1].get("state_ref"))
        ensure(original_state.tag == "{" + namespace + "}" + source["state"]
               and set(original_state.attrib) <= {"id", "version", "comment"}
               and original_state.get("version") is not None
               and original_state.get("comment") == old_state["state_title"]
               and len(original_state) == (6 if uname else 1),
               "source State title/type or scalar cardinality changed")
        old_fields = old_state["state"].get("all") if uname else [old_state["state"]]
        ensure(isinstance(old_fields, list) and len(old_fields) == len(original_state)
               and (not uname or set(old_state["state"]) == {"all"}),
               "source State AND field closure changed")
        native_fields = []
        for element, old_field in zip(original_state, old_fields):
            ensure(isinstance(old_field, dict) and
                   set(old_field) == {"field", "value", "operation", "datatype", "match", "existence"}
                   and (type(old_field["value"]) is int if apparmor else
                        isinstance(old_field["value"], str)),
                   "mapped State must be one literal scalar comparison")
            field = element.tag.rsplit("}", 1)[-1]
            rename = mapping["native"].get("state_field_map", {})
            datatype = element.get("datatype", "string")
            if apparmor:
                ensure(field == "loaded_profiles_count" and datatype == "int"
                       and element.get("operation") == "greater than or equal"
                       and element.text == "0" and old_field["value"] == 0
                       and old_test["match"] == "all",
                       "pinned AppArmor integer State/Test check changed")
            ensure(datatype in ({"int"} if apparmor else {"string", "version"}) and
                   element.tag == "{" + namespace + "}" + field
                   and field in rename and rename[field] == old_field["field"]
                   and not list(element)
                   and set(element.attrib) <= {"operation", "datatype", "entity_check",
                                              "entity_existence"}
                   and element.get("entity_check", "all") == "all"
                   and element.get("entity_existence", "at_least_one_exists") ==
                       "at_least_one_exists"
                   and old_field["datatype"] == ("integer" if apparmor else datatype)
                   and old_field["match"] == "all"
                   and old_field["existence"] == "one_or_more"
                   and (int(element.text) if apparmor else (element.text or "")) == old_field["value"],
                   "source State field/existence/check/value mismatch")
            operation = element.get("operation", "equals")
            operation_map = ({"greater than or equal": ("greater_than_or_equal", "greater_than_or_equal")}
                             if apparmor else {**SOURCE_OPERATIONS, **({"case insensitive not equal":
                                 ("case_insensitive_not_equal", "case_insensitive_not_equal")}
                                if environment else {})} if datatype == "string" else VERSION_OPERATIONS)
            ensure(operation in operation_map
                   and old_field["operation"] == operation_map[operation][0],
                   "source State operation lost by mature 0.3 lowering")
            native_fields.append({rename[field]: {
                "require": "at_least_one_exists_and_all_match",
                operation_map[operation][1]: old_field["value"],
                **({"datatype": old_field["datatype"]} if apparmor else {})}})
        native_states = [{"and": native_fields}] if uname else native_fields

    native_id = "loaded-apparmor-profiles-test" if apparmor else slug(old_test["test_title"])
    if environment and not native_id.startswith("test-"):
        native_id = "test-" + native_id
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
        "evaluate": {"and": [{"test": native_id}]} if apparmor or uname else {"test": native_id},
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
