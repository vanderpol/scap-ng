#!/usr/bin/env python3
"""Source-checked canonical 0.4.0 multi-Test no-State conversion pilot.

Operates only on the pinned original OVAL Self-Assertion XML and independently
source-compatible 0.3 fallback used as a *secondary* Test naming oracle.
Exports direct flat Object native 0.4.0 Assessments; excludes Variables, Sets,
Filters, nil, uncommon checks, and expected-error synthetic cases. It never
claims executable result parity or conversion of all 167 Definitions.

Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml
from v04_flat_object_authoring import dump_hybrid, digest, load_catalog

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
SCHEMA = "scap-ng.pre-alpha.assessment"
PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
OPERATIONS = {"equals": "equals", "pattern match": "matches_regex"}
EXPECTED_SOURCE_COMPATIBLE = 162
EXPECTED_PREVIOUS_MULTITEST = 44


class Unsupported(ValueError):
    pass


def ensure(condition, code):
    if not condition:
        raise Unsupported(code)


def local(tag):
    return tag.rsplit("}", 1)[-1]


def indexed(root):
    entries = {}
    for node in root.iter():
        ident = node.get("id")
        if ident:
            ensure(ident not in entries, "DUPLICATE_SOURCE_OVAL_ID")
            entries[ident] = node
    return entries


def source_criteria(definition, source_ids):
    parent = next((x for x in definition if local(x.tag) == "criteria"), None)
    ensure(parent is not None, "SOURCE_CRITERIA_MISSING")
    ensure(set(parent.attrib) <= {"operator"} and
           parent.get("operator", "AND") == "AND",
           "SOURCE_BOOLEAN_EXPRESSION_NOT_SIMPLE_AND")
    refs = []
    for node in parent:
        ensure(local(node.tag) == "criterion" and
               set(node.attrib) <= {"test_ref", "comment", "negate"} and
               node.get("negate", "false") == "false" and
               node.get("test_ref") in source_ids,
               "SOURCE_CRITERIA_HAS_NESTED_OR_UNSUPPORTED_ELEMENT")
        refs.append(node.get("test_ref"))
    ensure(len(refs) >= 2 and len(refs) == len(set(refs)),
           "SOURCE_CRITERIA_NOT_DISTINCT_MULTITEST")
    return refs


def convert_one(review, original_file, catalog):
    source = review["source"]
    native = review["A_source_compatibility_fallback"]
    ensure(source["file"] == original_file.relative_to(
        original_file.parents[2]).as_posix().replace("OVAL_Test_Content/", ""),
        "SOURCE_PATH_MISMATCH")
    raw = original_file.read_bytes()
    ensure(sha256(raw).hexdigest() == source["source_file_sha256"],
           "PINNED_ORIGINAL_XML_SHA_MISMATCH")
    root = ET.fromstring(raw)
    ids = indexed(root)
    definition = ids.get(source["definition_id"])
    ensure(definition is not None and local(definition.tag) == "definition",
           "SOURCE_DEFINITION_MISSING")
    ensure(definition.get("class") == native.get("class") and
           int(definition.get("version", "-1")) == native.get("version"),
           "SOURCE_DEFINITION_CLASS_OR_VERSION_DRIFT")
    metadata = next((x for x in definition if local(x.tag) == "metadata"), None)
    title = next((x.text or "" for x in metadata
                  if local(x.tag) == "title"), None) if metadata is not None else None
    ensure(title == native.get("assessment_title"),
           "SOURCE_DEFINITION_TITLE_DRIFT")
    refs = source_criteria(definition, ids)
    original = native.get("tests") or {}
    objects = native.get("objects") or {}
    ensure(2 <= len(original) <= 15 and len(refs) == len(original),
           "MULTITEST_COUNT_NOT_SAFE")
    ensure(not native.get("states") and not native.get("variables") and
           not native.get("shared_objects"),
           "STATE_VARIABLE_OR_SHARED_GRAPH_UNSUPPORTED")
    tree=native.get("evaluate")
    ensure(isinstance(tree,dict) and set(tree)=={"all"} and
           isinstance(tree["all"],list) and
           len(tree["all"])==len(original) and
           all(isinstance(branch,dict) and set(branch)=={"test"} and
               isinstance(branch["test"],str) for branch in tree["all"]),
           "AUTHORING_BOOLEAN_TREE_NOT_DIRECT_AND")
    test_names = [entry["test"] for entry in native["evaluate"]["all"]]
    ensure(len(test_names) == len(set(test_names)) and set(test_names) == set(original),
           "AUTHORING_TEST_REFERENCE_MISMATCH")
    # Canonical 0.4 Test references end in '-test'. Historical 0.3
    # conversion identifiers are source-derived but often do not. Build a
    # one-to-one rewrite and preserve each original source name in provenance.
    canonical_names={}
    for old_name in original:
        # The archived converter added a mechanical test- prefix to many
        # source Test comments. Remove that noise rather than authoring
        # canonical Test IDs like test-test-...-test.
        new_name=old_name
        while new_name.startswith("test-"):
            new_name=new_name[len("test-"):]
        if not new_name.endswith("-test"):
            new_name+="-test"
        ensure(new_name not in canonical_names.values() and
               all(x.islower() or x.isdigit() or x=="-" for x in new_name) and
               not new_name.startswith("-") and "--" not in new_name,
               "TEST_ID_REWRITE_COLLISION_OR_INVALID")
        canonical_names[old_name]=new_name

    original_by_comment = {}
    for ref in refs:
        src_test = ids[ref]
        comment = src_test.get("comment")
        ensure(comment and comment not in original_by_comment,
               "SOURCE_TEST_COMMENT_NOT_UNIQUE")
        original_by_comment[comment] = src_test
    ensure(set(original_by_comment) == {
        entry.get("test_title") for entry in original.values()
    }, "SOURCE_TEST_TITLE_PARITY_FAILURE")

    output = deepcopy({key: native[key] for key in (
        "id", "version", "assessment_title", "mode", "class", "purpose", "evaluate")})
    ensure(output["mode"] == "automated", "NOT_AUTOMATED")
    output["specification"] = {"id": SCHEMA, "version": "0.4.0"}
    # Original OVAL criteria default AND. The explicitly preferred 0.4
    # equivalent is 'and', not the legacy deprecated 'all' spelling.
    output["evaluate"] = {"and": [{"test": canonical_names[x["test"]]}
                                  for x in tree["all"]]}
    output["tests"] = {}
    ledger = []
    seen_obj_refs = set()
    for name, oldtest in original.items():
        allowed = {"test_title","capability","check","check_existence",
                   "object","reported_elements"}
        ensure(set(oldtest) == allowed, "TEST_EXTRA_ATTRIBUTES")
        ensure(oldtest["check"] == "all" and
               oldtest["check_existence"] == "at_least_one_exists",
               "TEST_QUANTIFIER_UNSUPPORTED")
        ensure(oldtest["reported_elements"] == "all",
               "TEST_REPORTED_ELEMENTS_UNSUPPORTED")
        ensure("expected result" not in oldtest["test_title"].lower(),
               "EXPECTED_ERROR_CASE_OUTSIDE_PILOT")
        cap = oldtest["capability"]
        ensure(cap in catalog and catalog[cap]["selectors"],
               "CAPABILITY_NOT_MAPPED_OR_SELECTORLESS")
        ref = oldtest["object"]
        ensure(type(ref) is str and ref in objects and ref not in seen_obj_refs,
               "SOURCE_OBJECT_REFERENCE_NOT_SINGLE_USE")
        seen_obj_refs.add(ref)
        old_obj = objects[ref]
        ensure(set(old_obj) == {"capability", "object_title", "select"} and
               old_obj["capability"] == cap, "COMPLEX_SOURCE_OBJECT")
        source_selectors = old_obj["select"]
        ensure(isinstance(source_selectors, dict) and bool(source_selectors),
               "EMPTY_SOURCE_SELECTORS")
        # The native mapping contains OVAL entity names to renamed 0.4 field
        # names, e.g. unix.symlink filepath -> full_path.
        mapping = catalog[cap]["selector_names"]
        required = set(source_selectors)
        ensure(required <= set(mapping) and
               set(mapping[k] for k in required) <= catalog[cap]["selectors"],
               "UNMAPPED_SOURCE_SELECTOR")
        obj = {}
        if old_obj["object_title"] is not None:
            obj["object_title"] = old_obj["object_title"]
        for key, field in source_selectors.items():
            ensure(isinstance(field, dict) and
                   set(field) == {"datatype", "operation", "value"} and
                   field["datatype"] == "string" and
                   type(field["value"]) is str and
                   field["operation"] in OPERATIONS,
                   "SOURCE_TYPED_SELECTOR_OR_NIL_UNSUPPORTED")
            obj[mapping[key]] = {OPERATIONS[field["operation"]]: field["value"]}

        source_test = original_by_comment[oldtest["test_title"]]
        ensure(source_test.get("check", "all") == "all" and
               source_test.get("check_existence", "at_least_one_exists") ==
               "at_least_one_exists", "SOURCE_TEST_QUANTIFIER_DRIFT")
        ensure(local(source_test.tag) == cap.split(".")[1].replace(".", "") + "_test"
               or local(source_test.tag).endswith("_test"),
               "SOURCE_TEST_TYPE_UNSUPPORTED")
        source_ref = next((x for x in source_test if local(x.tag) == "object"), None)
        ensure(source_ref is not None and len(source_test) == 1 and
               bool(source_ref.get("object_ref")),
               "SOURCE_TEST_OBJECT_OR_STATE_BINDING_UNSUPPORTED")
        src_obj = ids.get(source_ref.get("object_ref"))
        ensure(src_obj is not None and local(src_obj.tag).endswith("_object"),
               "SOURCE_OVAL_OBJECT_NOT_FOUND")
        elements = list(src_obj)
        ensure(len(elements) == len(source_selectors) and
               not any(local(e.tag) in {"set", "filter", "behaviors"} for e in elements),
               "SOURCE_OVAL_SET_FILTER_OR_BEHAVIOR_UNSUPPORTED")
        for field in elements:
            n = local(field.tag)
            old_field = source_selectors.get(n)
            ensure(old_field is not None and
                   field.get("operation", "equals") == old_field["operation"] and
                   field.get("datatype", "string") == old_field["datatype"] and
                   set(field.attrib) <= {"operation", "datatype"} and
                   field.text == old_field["value"],
                   "ORIGINAL_OVAL_SELECTOR_MISMATCH")
        output["tests"][canonical_names[name]] = {
            "test_title": oldtest["test_title"],
            "capability": cap,
            "object": obj,
            "reported_elements": "all",
            "require": {"items": "one_or_more"}
        }
        ledger.append({
            "previous_source_test_name": name,
            "canonical_040_test_name": canonical_names[name],
            "oval_test_id": source_test.get("id"),
            "oval_object_id": src_obj.get("id"),
            "source_object_name": ref,
            "capability": cap
        })
    ensure(len(seen_obj_refs) == len(objects),
           "UNUSED_OR_SHARED_SOURCE_OBJECTS_UNACCOUNTED")
    proof = {
        "source_repository_revision": PIN,
        "source_file": source["file"],
        "source_file_sha256": source["source_file_sha256"],
        "source_definition_id": source["definition_id"],
        "original_assessment_graph_sha256": digest(native),
        "current_040_assessment_graph_sha256": digest(output),
        "source_test_count": len(refs),
        "converted_tests": ledger,
        "original_oval_closure_comparison": "PASS_LIMITED_DIRECT_TEST_OBJECT_SELECTOR",
        "native_schema_validation": "PENDING_CI",
        "scanner_result_equivalence": "NOT_PROVEN"
    }
    return {"assessment": output}, proof


def load_catalog_renames(root):
    catalog = load_catalog(root)
    for cap, item in catalog.items():
        path = root / (cap+".json")
        src = json.loads(path.read_text())
        item["selector_names"] = src.get("native", {}).get("selector_map", {})
    return catalog


def build(source_root, original_root, catalog_root, output_root):
    source_root = Path(source_root)
    original_root = Path(original_root)
    output_root = Path(output_root)
    catalog = load_catalog_renames(Path(catalog_root))
    review_index = json.loads((source_root/"c-review/manifest.json").read_text())
    c = json.loads((source_root/"c-native/conversion-manifest.json").read_text())
    ensure(review_index["source_revision"] == PIN and
           c["source_compatible_not_yet_native_C"] == 126, "SOURCE_PIN_DRIFT")
    entries = {(r["file"],r["definition_id"]): r
               for r in review_index["exported_views"]}
    old = [r for r in c["unsupported"] if r["reason"].startswith("MULTI_TEST")]
    ensure(len(old) == EXPECTED_PREVIOUS_MULTITEST, "MULTITEST_SOURCE_DENOMINATOR_DRIFT")
    output_root.mkdir(parents=True, exist_ok=True)
    records=[]
    accepted=0
    for row in sorted(old,key=lambda r:(r["file"],r["definition_id"])):
        key=(row["file"],row["definition_id"])
        ensure(key in entries,"OVAL_DEFINITION_NOT_IN_SOURCE_COMPATIBLE_REVIEW")
        raw = json.loads((source_root/"c-review"/entries[key]["review_file"]).read_text())
        path=original_root/row["file"]
        try:
            generated,proof=convert_one(raw,path,catalog)
        except Unsupported as exc:
            records.append({"file":row["file"],"definition_id":row["definition_id"],
                            "status":"UNSUPPORTED_IN_CURRENT_NARROW_PILOT",
                            "reason":str(exc)})
            continue
        tag=sha256((row["file"]+"\x00"+row["definition_id"]).encode()).hexdigest()[:24]
        base=output_root/"authoring"/tag
        base.parent.mkdir(parents=True,exist_ok=True)
        (base.with_suffix(".json")).write_text(
            json.dumps(generated,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        (base.with_suffix(".yaml")).write_text(dump_hybrid(generated),encoding="utf-8")
        (base.with_suffix(".proof.json")).write_text(
            json.dumps(proof,indent=2)+"\n",encoding="utf-8")
        records.append({"file":row["file"],"definition_id":row["definition_id"],
                        "status":"CURRENT_040_FLAT_OBJECT_SOURCE_MATCHED_SCHEMA_PENDING",
                        "assessment_json":"authoring/"+tag+".json",
                        "assessment_yaml":"authoring/"+tag+".yaml",
                        "proof_file":"authoring/"+tag+".proof.json",
                        "source_tests":proof["source_test_count"]})
        accepted+=1
    reasons=Counter(x.get("reason","") for x in records if x["status"].startswith("UNSUPPORTED"))
    print("Source-checked multi-Test conversion diagnostics:",
          json.dumps({"accepted":accepted,"reasons":dict(sorted(reasons.items())),
                      "first_rejections":[x for x in records
                                          if x["status"].startswith("UNSUPPORTED")][:12]},
                     indent=2),flush=True)
    ensure(len(records)==EXPECTED_PREVIOUS_MULTITEST and accepted>=2,
           "NO_MEANINGFUL_NATIVE_040_SOURCE_PROGRESS: "+repr(dict(reasons)))
    status={"pin":PIN,"source_multitest_denominator":len(old),
            "native_040_source_matched_pending_schema":accepted,
            "not_yet_covered":len(old)-accepted,
            "schema_status":"PENDING",
            "original_oval_xml_semantics":"LIMITED_DIRECT_TEST_OBJECT_SELECTOR_ONLY",
            "scanner_result_equivalence":"NOT_PROVEN",
            "cases":records}
    (output_root/"manifest.json").write_text(json.dumps(status,indent=2)+"\n")
    return status


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-review",type=Path,required=True)
    parser.add_argument("--original-oval",type=Path,required=True)
    parser.add_argument("--catalog",type=Path,default=Path(__file__).resolve().parents[1] /
                        "schema/v0.4.0/capability-mappings/supported")
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    report=build(args.source_review,args.original_oval,args.catalog,args.output)
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},indent=2))


if __name__ == "__main__":
    main()
