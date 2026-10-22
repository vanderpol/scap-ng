#!/usr/bin/env python3
"""Original OVAL criteria/extend/ONE/XOR proof across nine source Definitions.

This is a narrowly source-pinned transformation, not an OVAL-wide converter.
Every regenerated OVAL Definition/Test/Variable is emitted from validated
native 0.4 Assessments; the source XML is used for independent comparison.
No scanner outcomes are asserted. Refs #248 #229 #232.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
FILE = "agnostic/oval-def_criteria.xml"
SHA = "2908b910c40b7e802eef47efe47eb557674bb286fbe1c0f03bbc442a44c76bea"
NUMBERS = (142, 357, 388, 404, 503, 560, 599, 903, 962)
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
IND = OD + "#independent"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
ORIGINAL = "oval:org.mitre.oval.test:"
NEW = "oval:scapng.04.criteria:"
BOOL_VAR = "criteria-boolean-source-variable"
SOURCE_TESTS = {"123": "true-variable-test", "966": "false-variable-test"}
NEW_TESTS = {"true-variable-test": NEW + "tst:1",
             "false-variable-test": NEW + "tst:2"}
SPECS = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
TEST_REQUIRE = "at_least_one_exists_and_all_match"
STATE_REQUIRE = "at_least_one_exists_and_all_match"
OPERATORS = {"AND": "and", "OR": "or", "ONE": "one", "XOR": "xor"}
INV_OPERATORS = {v: k for k, v in OPERATORS.items()}


def tag(namespace, name):
    return "{" + namespace + "}" + name


def require(ok, reason):
    if not ok:
        raise ValueError("pinned original OVAL criteria proof: " + reason)


def def_id(n):
    return ORIGINAL + "def:" + str(n)


def ass_id(n):
    return "original-criteria-" + str(n) + "-assessment"


def _only(parent, namespace, local):
    found = parent.findall(tag(namespace, local))
    require(len(found) == 1, "exactly one " + local)
    return found[0]


def _source_sections(raw):
    require(sha256(raw).hexdigest() == SHA, "original source SHA-256")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL Definitions namespace")
    defs = list(_only(root, OD, "definitions"))
    tests = list(_only(root, OD, "tests"))
    objects = list(_only(root, OD, "objects"))
    states = list(_only(root, OD, "states"))
    variables = list(_only(root, OD, "variables"))
    require(len(defs) == 9 and len(tests) == 2 and len(objects) == 1 and
            len(states) == 2 and len(variables) == 1,
            "pinned nine Definitions/two Tests/one Object/two States/one Variable")
    require({x.get("id") for x in defs} == {def_id(n) for n in NUMBERS},
            "exact original Definition identity set")
    require({x.get("id") for x in tests} == {
                ORIGINAL + "tst:" + n for n in SOURCE_TESTS},
            "exact original Test set")
    obj = objects[0]
    variable = variables[0]
    require(obj.tag == tag(IND, "variable_object") and
            variable.tag == tag(OD, "constant_variable") and
            variable.get("datatype") == "boolean" and
            _only(variable, OD, "value").text == "true" and
            _only(obj, IND, "var_ref").text == variable.get("id"),
            "one boolean constant Variable collected by variable Object")
    expected_states = {ORIGINAL + "ste:195": "true",
                       ORIGINAL + "ste:906": "false"}
    for state in states:
        value = _only(state, IND, "value")
        require(state.tag == tag(IND, "variable_state") and
                state.get("id") in expected_states and
                value.get("datatype") == "boolean" and
                value.text == expected_states[state.get("id")],
                "original boolean State semantics")
    expected_state_refs = {"123": ORIGINAL + "ste:195",
                           "966": ORIGINAL + "ste:906"}
    for test in tests:
        tid = test.get("id").rsplit(":", 1)[-1]
        require(test.tag == tag(IND, "variable_test") and
                test.get("check_existence") == "at_least_one_exists" and
                test.get("check") == "all" and
                _only(test, IND, "object").get("object_ref") == obj.get("id") and
                _only(test, IND, "state").get("state_ref") == expected_state_refs[tid],
                "source Test/State pairing and independent cardinalities")
    return defs, {t.get("id").rsplit(":", 1)[-1]: t for t in tests}


def _expr(node, references):
    name = node.tag.split("}")[-1]
    if name == "criteria":
        op = node.get("operator", "AND")
        require(op in OPERATORS and len(node) > 0,
                "OVAL AND/OR/ONE/XOR criteria operator and arity")
        entry = {OPERATORS[op]: [_expr(x, references) for x in node]}
    elif name == "criterion":
        ref = node.get("test_ref", "").rsplit(":", 1)[-1]
        require(ref in SOURCE_TESTS, "referenced source Test identity")
        entry = {"test": SOURCE_TESTS[ref]}
    elif name == "extend_definition":
        ref = node.get("definition_ref", "")
        require(ref in {def_id(n) for n in NUMBERS},
                "referenced original Definition identity")
        n = int(ref.rsplit(":", 1)[-1])
        alias = "criteria-" + str(n) + "-dependency"
        references[alias] = {"assessment": ass_id(n),
                             "expected_version": 1, "purpose": "assessment"}
        entry = {"assessment": alias}
    else:
        raise ValueError("unmapped OVAL criteria child: " + name)
    require(node.get("negate", "false") in ("true", "false"),
            "OVAL negate literal")
    return {"not": entry} if node.get("negate") == "true" else entry


def _test_native(source_test, match):
    return {
        "test_title": source_test.get("comment"),
        "capability": "variable.value", "variable": BOOL_VAR,
        "states": [{"value": {"equals": match, "datatype": "boolean",
                              "require": STATE_REQUIRE}}],
        "reported_elements": "all", "require": TEST_REQUIRE,
    }


def source_to_native(raw):
    definitions, tests = _source_sections(raw)
    docs = []
    for definition in definitions:
        n = int(definition.get("id").rsplit(":", 1)[-1])
        refs = {}
        evaluate = _expr(_only(definition, OD, "criteria"), refs)
        used = set()
        def walk(expr):
            if "test" in expr:
                used.add(expr["test"])
            for value in expr.values():
                if isinstance(value, list):
                    for child in value:
                        walk(child)
                elif isinstance(value, dict):
                    walk(value)
        walk(evaluate)
        meta = _only(definition, OD, "metadata")
        a = {
            "id": ass_id(n), "version": 1,
            "assessment_title": _only(meta, OD, "title").text,
            "mode": "automated", "class": "miscellaneous",
            "purpose": "assessment", "specification": SPECS, "tests": {},
        }
        if used:
            a["variables"] = {
                BOOL_VAR: {"kind": "constant", "datatype": "boolean",
                           "title": "Original OVAL boolean source true",
                           "expression": {"literal": ["true"]}}
            }
            a["tests"] = {
                name: _test_native(tests[key], "true" if key == "123" else "false")
                for key, name in SOURCE_TESTS.items() if name in used
            }
        if refs:
            a["dependencies"] = refs
        a["evaluate"] = evaluate
        docs.append({"assessment": a})
    require(len(docs) == 9, "nine explicit native Assessments")
    return docs


def _oval_expr(parent, expression, deps):
    if "not" in expression:
        return _oval_expr(parent, expression["not"], deps)._set_negate()
    if "test" in expression:
        name = expression["test"]
        require(name in NEW_TESTS, "native criterion Test")
        return _NegNode(ET.SubElement(parent, tag(OD, "criterion"),
                                      {"test_ref": NEW_TESTS[name]}))
    if "assessment" in expression:
        alias = expression["assessment"]
        require(alias in deps, "native Definition dependency alias")
        target = deps[alias]["assessment"]
        require(target in {ass_id(n) for n in NUMBERS},
                "native Definition dependency target")
        n = int(target.split("-")[2])
        return _NegNode(ET.SubElement(parent, tag(OD, "extend_definition"),
                                      {"definition_ref": NEW + "def:" + str(n)}))
    require(len(expression) == 1, "one native logical operator")
    op, args = next(iter(expression.items()))
    require(op in INV_OPERATORS and isinstance(args, list) and len(args) > 0,
            "OVAL-supported native logical operator")
    nested = ET.SubElement(parent, tag(OD, "criteria"),
                           {"operator": INV_OPERATORS[op]})
    for child in args:
        _oval_expr(nested, child, deps)
    return _NegNode(nested)


class _NegNode:
    def __init__(self, node):
        self.node = node

    def _set_negate(self):
        require(self.node.get("negate") is None, "single native negation")
        self.node.set("negate", "true")
        return self


def native_to_oval(docs):
    require(isinstance(docs, list) and len(docs) == 9, "nine native Assessments")
    docmap = {}
    shared_tests = {}
    for doc in docs:
        require(set(doc) == {"assessment"}, "Assessment root")
        a = doc["assessment"]
        require(a.get("id") in {ass_id(n) for n in NUMBERS} and
                a.get("id") not in docmap and
                a.get("specification") == SPECS and
                a.get("version") == 1 and
                a.get("mode") == "automated" and
                a.get("class") == "miscellaneous" and
                a.get("purpose") == "assessment", "native Assessment identity")
        require(set(a) <= {"id", "version", "assessment_title", "mode",
                           "class", "purpose", "specification", "variables",
                           "tests", "dependencies", "evaluate"},
                "reviewed source grammar only")
        deps = a.get("dependencies", {})
        for alias, dependency in deps.items():
            require(dependency == {"assessment": dependency.get("assessment"),
                                   "expected_version": 1,
                                   "purpose": "assessment"} and
                    alias.startswith("criteria-") and
                    dependency["assessment"] in {ass_id(n) for n in NUMBERS},
                    "native Assessment dependency contract")
        if a.get("tests"):
            variables = a.get("variables", {})
            require(set(variables) == {BOOL_VAR} and
                    variables[BOOL_VAR].get("kind") == "constant" and
                    variables[BOOL_VAR].get("datatype") == "boolean" and
                    variables[BOOL_VAR].get("expression") == {"literal": ["true"]},
                    "source native typed boolean Variable")
            for name, test in a["tests"].items():
                require(name in NEW_TESTS and
                        test.get("capability") == "variable.value" and
                        test.get("variable") == BOOL_VAR and
                        test.get("require") == TEST_REQUIRE and
                        test.get("reported_elements") == "all" and
                        isinstance(test.get("test_title"), str) and
                        len(test.get("states", [])) == 1,
                        "native Test result/existence contract")
                state = test["states"][0]
                require(state == {"value": {"equals": (
                            "true" if name == "true-variable-test" else "false"),
                            "datatype": "boolean", "require": STATE_REQUIRE}},
                        "independent OVAL boolean State constraint")
                prior = shared_tests.setdefault(name, test)
                require(prior == test, "shared Test identity consistency")
        else:
            require(not a.get("variables"), "no orphan Variable on extended Definition")
        docmap[a["id"]] = a
    require(set(docmap) == {ass_id(n) for n in NUMBERS} and
            set(shared_tests) == set(NEW_TESTS), "all nine native Definitions and both Tests")

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("ind-def", IND)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 original criteria proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    for n in NUMBERS:
        a = docmap[ass_id(n)]
        definition = ET.SubElement(defs, tag(OD, "definition"), {
            "id": NEW + "def:" + str(n), "version": "1", "class": "miscellaneous"})
        metadata = ET.SubElement(definition, tag(OD, "metadata"))
        ET.SubElement(metadata, tag(OD, "title")).text = a["assessment_title"]
        ET.SubElement(metadata, tag(OD, "description")).text = "OVAL criteria structure"
        temporary = ET.Element("temporary")
        wrapper = _oval_expr(temporary, a["evaluate"], a.get("dependencies", {})).node
        require(wrapper.tag == tag(OD, "criteria"), "root native evaluate is criteria")
        definition.append(wrapper)
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    obj = ET.SubElement(objects, tag(IND, "variable_object"), {
        "id": NEW + "obj:1", "version": "1"})
    ET.SubElement(obj, tag(IND, "var_ref")).text = NEW + "var:1"
    states = ET.SubElement(root, tag(OD, "states"))
    for name in ("true-variable-test", "false-variable-test"):
        t = shared_tests[name]
        ET.SubElement(tests, tag(IND, "variable_test"), {
            "id": NEW_TESTS[name], "version": "1", "comment": t["test_title"],
            "check_existence": "at_least_one_exists", "check": "all"})
        test_node = tests[-1]
        ET.SubElement(test_node, tag(IND, "object"), {"object_ref": NEW + "obj:1"})
        ET.SubElement(test_node, tag(IND, "state"), {
            "state_ref": NEW + ("ste:1" if name == "true-variable-test" else "ste:2")})
        state = ET.SubElement(states, tag(IND, "variable_state"), {
            "id": NEW + ("ste:1" if name == "true-variable-test" else "ste:2"),
            "version": "1"})
        ET.SubElement(state, tag(IND, "value"), {"datatype": "boolean"}).text = (
            t["states"][0]["value"]["equals"])
    variables = ET.SubElement(root, tag(OD, "variables"))
    var = ET.SubElement(variables, tag(OD, "constant_variable"), {
        "id": NEW + "var:1", "version": "1", "datatype": "boolean",
        "comment": "Original source constant boolean true"})
    ET.SubElement(var, tag(OD, "value")).text = "true"
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    docs = source_to_native(raw)
    validators = _schema_validators(schema_root)
    validate_docs({f"authoring/{doc['assessment']['id']}.json": doc
                   for doc in docs}, validators)
    for doc in docs:
        for test in doc["assessment"].get("tests", {}).values():
            errors = validate(materialize("variable.value"), "test", test)
            require(not errors, "native capability schema errors " + str(errors[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessments.json").write_text(json.dumps(docs, indent=2) + "\n")
    yml = "---\n".join(dump_hybrid(d) for d in docs)
    require(list(yaml.safe_load_all(yml)) == docs, "nine native YAML/JSON Assessment graphs")
    (out / "native-040.assessments.yaml").write_text(yml)
    oval = native_to_oval(docs)
    exported = out / "roundtrip-oval.xml"
    oval.write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "independent")
    require(xsd["status"] == "PASS", "OVAL 5.12.3 XSD " + str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    semantics = {}
    for n in NUMBERS:
        sem = compare(source, exported, source_root=def_id(n),
                      regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sem["equal"], "independent source-root semantics " + str(n))
        semantics[str(n)] = sem
    (out / "roundtrip-semantics.json").write_text(
        json.dumps(semantics, sort_keys=True, indent=2) + "\n")
    changed_source = raw.replace(b'operator="XOR"', b'operator="AND"', 1)
    require(changed_source != raw, "construct source XOR mutation")
    try:
        source_to_native(changed_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted altered original XOR source")
    altered = deepcopy(docs)
    altered[0]["assessment"]["evaluate"] = {"test": "true-variable-test"}
    try:
        native_to_oval(altered)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted missing original XOR criteria tree")
    for original, replacement, target in (("xor", "one", 142),
                                          ("one", "xor", 599)):
        changed = deepcopy(docs)
        candidate = next(x for x in changed
                         if x["assessment"]["id"] == ass_id(target))
        def swap_first(node):
            if not isinstance(node, dict):
                return False
            if original in node:
                node[replacement] = node.pop(original)
                return True
            for value in node.values():
                if isinstance(value, list):
                    for child in value:
                        if swap_first(child):
                            return True
                elif swap_first(value):
                    return True
            return False
        require(swap_first(candidate["assessment"]["evaluate"]),
                "construct distinct original ONE/XOR semantic mutation")
        wrong = out / ("mutated-" + original + "-to-" + replacement + ".xml")
        native_to_oval(changed).write(wrong, encoding="utf-8", xml_declaration=True)
        mismatch = compare(source, wrong, source_root=def_id(target),
                           regenerated_root=NEW + "def:" + str(target), root_only=True)
        require(mismatch["equal"] is False,
                "ONE and XOR are independently distinguishable under source graph")
    proof = {
        "source_revision": PIN, "source_file": FILE,
        "original_xml_sha256": SHA,
        "original_definition_ids": [def_id(n) for n in NUMBERS],
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_nine_root_semantic_graphs": "PASS",
        "source_mutation": "REJECTED", "native_expression_mutation": "REJECTED",
        "one_xor_semantic_swap": "DETECTED",
        "test_count": 2, "definition_count": 9, "scanner_parity": False,
    }
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, sort_keys=True, indent=2) + "\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--schema-root", type=Path, required=True)
    p.add_argument("--xsd-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(prove(a.source, a.schema_root, a.xsd_root, a.output), sort_keys=True))
