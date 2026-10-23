#!/usr/bin/env python3
"""Source-attested direct multi-Test presence AND projection, reusing 0.3.

Only a flat original OVAL AND over two or more direct, no-State scalar
Object Tests is accepted. The mature 0.3 graph supplies source lowering;
each original Test/selector/existence axis is independently checked before
current 0.4 schema and native program compilation. No scanner parity claim.

Refs #232 #248 #229.
"""
from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from import_v04_oval_leaf_pilot import slug
from v04_flat_object_authoring import flatten_document, restore_document
from v04_native_bundle_compiler import compile_assessment_program
from v04_source_verified_object_presence import (
    OD, SOURCE_EXISTENCE, SOURCE_ITEM_CHECK, child,
    direct_selectors, ensure, source_by_id,
)


def convert(v003, source_xml, definition_id, provenance, catalog_dir, catalog):
    a = v003["assessment"]
    tests = a.get("tests") or {}
    objects = a.get("objects") or {}
    ensure(a.get("specification", {}).get("version") == "0.3.0"
           and a.get("mode") == "automated"
           and a.get("class") in {"miscellaneous", "inventory", "compliance"}
           and not a.get("states") and not a.get("variables")
           and "shared_objects" not in a
           and 2 <= len(tests) <= 15 and len(objects) == len(tests),
           "multi-Test requires 2-15 direct Object Tests without State/Variable")
    root = ET.fromstring(source_xml)
    ensure(root.tag == "{" + OD + "}oval_definitions", "not OVAL Definitions")
    definition = source_by_id(root, definition_id)
    ensure(definition.tag == "{" + OD + "}definition"
           and definition.get("deprecated", "false") == "false"
           and definition.get("class") == a["class"]
           and int(definition.get("version", "-1")) == a["version"],
           "Definition identity/class/version changed")
    title = child(child(definition, "metadata"), "title")
    ensure(title.text is not None and title.text.strip() == a["assessment_title"],
           "Definition title changed")
    criteria = child(definition, "criteria")
    ensure(set(criteria.attrib) <= {"operator"}
           and criteria.get("operator", "AND") == "AND"
           and len(criteria) == len(tests),
           "source Boolean expression is not a flat AND")
    original_ids = []
    for criterion in criteria:
        ensure(criterion.tag == "{" + OD + "}criterion"
               and set(criterion.attrib) <= {"test_ref", "comment", "negate"}
               and criterion.get("negate", "false") == "false"
               and criterion.get("test_ref"),
               "non-direct, negated or missing OVAL criterion")
        original_ids.append(criterion.get("test_ref"))
    ensure(len(set(original_ids)) == len(original_ids),
           "repeated OVAL Test criterion needs explicit duplicate semantics")
    bindings = provenance.get("source_test_bindings", {})
    ensure(set(bindings) == set(original_ids)
           and set(bindings.values()) == set(tests),
           "mature 0.3 source Test coverage/bindings differ")
    evaluate = a.get("evaluate")
    ensure(isinstance(evaluate, dict) and set(evaluate) == {"all"}
           and evaluate["all"] == [
               {"test": bindings[tid]} for tid in original_ids],
           "mature 0.3 Boolean source-order/AND changed")

    new_tests = {}
    test_names = []
    used_source_objects = set()
    used_mapped_objects = set()
    for oval_id in original_ids:
        tid = bindings[oval_id]
        old_test = tests[tid]
        ensure(set(old_test) == {"test_title", "capability", "object",
                                 "reported_elements", "existence", "match"}
               and old_test["reported_elements"] == "all"
               and old_test["match"] in SOURCE_ITEM_CHECK.values()
               and old_test["object"] in objects,
               "one source Test has unsupported structure/State/check")
        source_test = source_by_id(root, oval_id)
        cap = old_test["capability"]
        mapping_path = Path(catalog_dir) / (cap + ".json")
        ensure(cap in catalog and mapping_path.is_file(),
               "source Test capability not mapped in current 0.4 catalog")
        mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
        src = mapping["source"]
        namespace = src["namespace"]
        ensure(source_test.tag == "{" + namespace + "}" + src["test"]
               and set(source_test.attrib) <= {"id", "version", "comment",
                                                    "check_existence", "check"}
               and source_test.get("version") is not None
               and source_test.get("comment") == old_test["test_title"]
               and source_test.get("check", "all") in SOURCE_ITEM_CHECK
               and SOURCE_ITEM_CHECK[source_test.get("check", "all")] == old_test["match"]
               and len(source_test) == 1
               and source_test[0].tag in {"{" + namespace + "}object", "{" + OD + "}object"}
               and set(source_test[0].attrib) == {"object_ref"},
               "source Test type/quantifier/State changed")
        ex = source_test.get("check_existence", "at_least_one_exists")
        ensure(ex in SOURCE_EXISTENCE and
               old_test["existence"] == SOURCE_EXISTENCE[ex][0],
               "source Test check_existence differs from mature 0.3")
        original_object_id = source_test[0].get("object_ref")
        source_obj = source_by_id(root, original_object_id)
        ensure(source_obj.tag == "{" + namespace + "}" + src["object"]
               and set(source_obj.attrib) <= {"id", "version", "comment"}
               and source_obj.get("version") is not None,
               "source Object type/attributes unsupported")
        old_object_id = old_test["object"]
        ensure(old_object_id not in used_mapped_objects
               and original_object_id not in used_source_objects,
               "shared/repeated Object needs separate shared-reference proof")
        used_mapped_objects.add(old_object_id)
        used_source_objects.add(original_object_id)
        projected_obj = direct_selectors(source_obj, objects[old_object_id],
                                         namespace, cap, mapping, catalog)
        new_id = slug(old_test["test_title"])
        ensure(new_id not in new_tests,
               "canonical Test ID collision requires independent identity mapping")
        new_tests[new_id] = {
            "test_title": old_test["test_title"], "capability": cap,
            "object": projected_obj, "reported_elements": "all",
            "require": {"items": SOURCE_EXISTENCE[ex][1]},
        }
        test_names.append(new_id)
    ensure(used_mapped_objects == set(objects)
           and set(provenance.get("source_collection_bindings", {})) == used_source_objects,
           "original Source Object closure differs from mature 0.3")

    result = {"assessment": {
        "id": a["id"], "version": a["version"],
        "assessment_title": a["assessment_title"], "mode": "automated",
        "class": a["class"], "purpose": a["purpose"],
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "tests": new_tests,
        "evaluate": {"and": [{"test": name} for name in test_names]},
    }}
    flattened, proof = flatten_document(result, catalog)
    ensure(not proof["edits"] and restore_document(flattened, proof) == result,
           "multi-Test flat Object inverse unexpectedly changed")
    program = compile_assessment_program(result["assessment"])
    ensure(len(program["test_instructions"]) == len(tests)
           and all(instruction["opcode"] == "CHECK_COLLECTION_PRESENCE"
                   for instruction in program["test_instructions"]),
           "native 0.4 compilation dropped an original source Test")
    return result
