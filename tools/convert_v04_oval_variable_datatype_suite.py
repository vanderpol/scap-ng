#!/usr/bin/env python3
"""Ten pinned original OVAL independent.variable datatype suites -> native 0.4.

This deliberately narrow reusable importer preserves the original literal
lexemes, multi-valued Variables, typed operations, Test quantifiers, nested
criteria and leaf negation. Unsupported OVAL source features fail closed.
Refs #248 #229 #232. This is NOT scanner execution parity.
"""
from __future__ import annotations

from hashlib import sha256
import xml.etree.ElementTree as ET

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
CASES = {
    "oval_binary_datatype.xml": ("oval:org.mitre.oval.test:def:707", "eb50e4c0ad2e1d94941e0a1c31d43dd31c6ce030c072790f5dbb3793aa8e1e91", "binary", 4),
    "oval_boolean_datatype.xml": ("oval:org.mitre.oval.test:def:709", "f58c191f31a8c1e32a5f4503a9252702cbc308ccc1462d36569f71dee09e2cef", "boolean", 8),
    "oval_string_datatype.xml": ("oval:org.mitre.oval.test:def:252", "58ca3747e110831969600ecdd72f591c37adf099658e4cc3babf03779a2a9a2e", "string", 10),
    "oval_float_datatype.xml": ("oval:org.mitre.oval.test:def:275", "006e8d8d293849e3478c1fa727eb3b7bda14ca490395608b40ea49dc686ec07e", "float", 16),
    "oval_evr_string_datatype.xml": ("oval:org.mitre.oval.test:def:392", "d47f8b10868e052481aa9cfbe67f616d683f244a93c7810ee40c20b62c21d179", "evr_string", 16),
    "oval_int_datatype.xml": ("oval:org.mitre.oval.test:def:356", "bf3ae1b0f7dbbe4dde8bae9e30b16202ffd6101bfc42f053110eefaa97fa5965", "int", 20),
    "oval_version_datatype.xml": ("oval:org.mitre.oval.test:def:291", "c20249735d1900285a293b958f03a94b359eb00b1023b87e22d8c2a9776737df", "version", 48),
    "oval_ipv4address_datatype.xml": ("oval:org.mitre.oval.test:def:884", "cb45247269fcb983047c4f06d1aa3dfcf7fb9f5ed690f3c0358f87f308115d2b", "ipv4_address", 13),
    "oval_ipv6address_datatype.xml": ("oval:org.mitre.oval.test:def:231", "7eb8fd0c02a044435981684cf02650e49b3c87247b3da45050a38dbe51c376b7", "ipv6_address", 13),
    "oval_check_enumeration_entity.xml": ("oval:org.mitre.oval.test:def:687", "f9e0c3706ecbe282f2e0ece9a833cfa419510557356bc0dfc3edd0d2a29ca19a", "int", 10),
}
OP = {
    "equals": "equals", "not equal": "not_equal",
    "case insensitive equals": "case_insensitive_equals",
    "case insensitive not equal": "case_insensitive_not_equal",
    "pattern match": "matches_regex",
    "greater than": "greater_than", "greater than or equal": "greater_than_or_equal",
    "less than": "less_than", "less than or equal": "less_than_or_equal",
    "bitwise and": "bitwise_and", "bitwise or": "bitwise_or",
    "subset of": "subset_of", "superset of": "superset_of",
}
PREFIX = {"float": "float_", "version": "version_", "evr_string": "rpm_evr_",
          "ipv4_address": "ipv4_", "ipv6_address": "ipv6_"}
NATIVE_DTYPE = {"int": "integer", "evr_string": "rpm_evr",
                "ipv4_address": "ipv4", "ipv6_address": "ipv6"}
TEST_REQUIRE = "at_least_one_exists_and_some_match"
FIELD_REQUIRE = "at_least_one_exists_and_all_match"
IP_DATATYPES = frozenset({"ipv4_address", "ipv6_address"})
ENTITY_CASE = "oval_check_enumeration_entity.xml"
ENTITY_CHECK_REQUIRE = {
    "all": FIELD_REQUIRE,
    "at least one": "at_least_one_exists_and_some_match",
    "none satisfy": "at_least_one_exists_and_none_match",
    "only one": "at_least_one_exists_and_only_one_matches",
}


def must(ok, reason):
    if not ok:
        raise ValueError("unreviewed original OVAL datatype suite: " + reason)


def tag(ns, name):
    return "{" + ns + "}" + name


def single(parent, ns, name):
    found = parent.findall(tag(ns, name))
    must(len(found) == 1, "single " + name)
    return found[0]


def indexed(parent, kind):
    rows = {}
    for e in parent:
        must(e.get("id") and e.get("id") not in rows, "unique " + kind + " IDs")
        rows[e.get("id")] = e
    return rows


def native_op(dtype, operation):
    must(operation in OP, "unreviewed OVAL comparison " + operation)
    raw = OP[operation]
    # Preserve typed version, RPM EVR and floating-point comparisons;
    # lexical/string comparison must not replace these ordering semantics.
    return PREFIX.get(dtype, "") + raw if dtype in PREFIX else raw


def convert(raw: bytes, filename: str):
    must(filename in CASES, "unreviewed source filename " + filename)
    did, digest, dtype, ntests = CASES[filename]
    must(sha256(raw).hexdigest() == digest, "pinned original source SHA")
    root = ET.fromstring(raw)
    must(root.tag == tag(OD, "oval_definitions"), "root namespace")
    defs = indexed(single(root, OD, "definitions"), "Definition")
    must(set(defs) == {did}, "one pinned Definition")
    definition = defs[did]
    must(definition.get("class") == "miscellaneous" and
         set(definition.attrib) <= {"id", "version", "class"}, "Definition metadata")
    title = single(single(definition, OD, "metadata"), OD, "title").text
    source_vars = indexed(single(root, OD, "variables"), "Variable")
    names = {ident: f"source-{i}-variable" for i, ident in enumerate(source_vars, 1)}
    variables = {}
    for sid, var in source_vars.items():
        must(var.tag == tag(OD, "constant_variable") and
             var.get("datatype") == dtype and len(var) >= 1 and
             set(var.attrib) <= {"id", "version", "comment", "datatype"},
             "constant typed Variable " + sid)
        values = []
        for value in var:
            must(value.tag == tag(OD, "value") and not value.attrib and
                 value.text is not None, "literal Variable value " + sid)
            values.append(value.text)  # Keep 1/0, scientific notation, EVR strings intact.
        variables[names[sid]] = {
            "kind": "constant", "datatype": NATIVE_DTYPE.get(dtype, dtype),
            "title": var.get("comment") or names[sid],
            "expression": {"literal": values},
        }
    source_objects = indexed(single(root, OD, "objects"), "Object")
    objects = {}
    for oid, obj in source_objects.items():
        must(obj.tag == tag(IND, "variable_object") and len(obj) == 1 and
             set(obj.attrib) <= {"id", "version", "comment"}, "direct Variable Object")
        ref = single(obj, IND, "var_ref")
        must(not ref.attrib and ref.text in names, "Object var_ref")
        objects[oid] = names[ref.text]
    source_states = indexed(single(root, OD, "states"), "State")
    states = {}
    for sid, state in source_states.items():
        must(state.tag == tag(IND, "variable_state") and len(state) == 1 and
             state.get("operator", "AND") == "AND" and
             set(state.attrib) <= {"id", "version", "comment", "operator"},
             "single-field State " + sid)
        value = single(state, IND, "value")
        allowed_attrs = ({"datatype", "operation", "entity_check"}
                         if filename == ENTITY_CASE else {"datatype", "operation"})
        must(set(value.attrib) <= allowed_attrs and
             value.get("datatype", "string") == dtype and value.text is not None,
             "State typed literal " + sid)
        op = native_op(dtype, value.get("operation", "equals"))
        if filename == ENTITY_CASE:
            must(value.get("entity_check") in ENTITY_CHECK_REQUIRE,
                 "reviewed OVAL entity_check " + sid)
        field_require = (ENTITY_CHECK_REQUIRE[value.get("entity_check")]
                         if filename == ENTITY_CASE else FIELD_REQUIRE)
        # No Variable reference on the State side in this source group.
        states[sid] = {"value": {
            op: value.text, "datatype": NATIVE_DTYPE.get(dtype, dtype),
            "require": field_require,
        }}
    source_tests = indexed(single(root, OD, "tests"), "Test")
    must(len(source_tests) == ntests, "source Test census")
    test_names = {sid: f"source-{i}-test" for i, sid in enumerate(source_tests, 1)}
    tests = {}
    for tid, test in source_tests.items():
        expected_check = ("all" if dtype in IP_DATATYPES or filename == ENTITY_CASE
                          else "at least one")
        must(test.tag == tag(IND, "variable_test") and len(test) == 2 and
             test.get("check") == expected_check and
             test.get("check_existence") == "at_least_one_exists" and
             test.get("state_operator", "AND") == "AND" and
             set(test.attrib) <= {"id", "version", "comment", "check", "check_existence", "state_operator"},
             "OVAL Test semantics " + tid)
        object_child = single(test, IND, "object")
        state_child = single(test, IND, "state")
        must(set(object_child.attrib) == {"object_ref"} and
             set(state_child.attrib) == {"state_ref"} and
             object_child.get("object_ref") in objects and
             state_child.get("state_ref") in states, "Test Object/State links")
        tests[test_names[tid]] = {
            "test_title": test.get("comment") or test_names[tid],
            "capability": "variable.value",
            "variable": objects[object_child.get("object_ref")],
            "states": [states[state_child.get("state_ref")]],
            "reported_elements": "all", "require": (
                FIELD_REQUIRE if dtype in IP_DATATYPES or filename == ENTITY_CASE
                else TEST_REQUIRE),
        }

    referenced = []
    def expression(node):
        if node.tag == tag(OD, "criterion"):
            must(set(node.attrib) <= {"comment", "test_ref", "negate"} and
                 node.get("test_ref") in test_names and
                 node.get("negate", "false") in {"true", "false"},
                 "criterion reference/negation")
            referenced.append(node.get("test_ref"))
            expr = {"test": test_names[node.get("test_ref")]}
            return {"not": expr} if node.get("negate") == "true" else expr
        must(node.tag == tag(OD, "criteria") and
             node.get("operator", "AND") == "AND" and
             set(node.attrib) <= {"operator", "comment"} and
             len(node) >= 1, "nested AND Boolean tree")
        return {"and": [expression(n) for n in node]}
    evaluate = expression(single(definition, OD, "criteria"))
    must(set(referenced) == set(source_tests) and len(referenced) == ntests,
         "complete one-to-one Test reference closure")
    assessment = {
        "id": filename.removesuffix(".xml").replace("_", "-") + "-assessment",
        "version": int(definition.get("version")),
        "assessment_title": title, "mode": "automated",
        "class": "miscellaneous", "purpose": "assessment",
        "specification": {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"},
        "variables": variables, "tests": tests, "evaluate": evaluate,
    }
    return {"assessment": assessment}, {
        "source_revision": PIN, "source_file": "agnostic/" + filename,
        "original_definition_id": did, "original_xml_sha256": digest,
        "native_test_count": ntests, "native_variable_count": len(variables),
        "source_datatype": dtype, "scanner_parity": False,
    }
