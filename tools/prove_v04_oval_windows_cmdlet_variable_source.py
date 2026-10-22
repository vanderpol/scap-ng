#!/usr/bin/env python3
"""Three original OVAL Windows cmdlet record-field Variable Definitions.

This source-pinned companion to the variable-free cmdlet proof covers literal
local Variables in PowerShell parameter and select record fields. It retains
typed structured records and the source variable-reference dependency; the
independent exporter reconstructs OVAL local_variable/literal_component.
It is not scanner execution parity. Refs #248 #229 #232.
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
from prove_v04_oval_windows_cmdlet_source import (
    FILE, SHA, PIN, OD, WIN, OC, XSI, ORIGINAL, SOURCES as LITERAL_SOURCES,
    SPECS, REQUIRE, INVERSE, OPERATORS, INVERSE_OPS, tag, require, one,
    original_def, assessment_id, original_id,
)

NEW = "oval:scapng.04.cmdletvar:"
SOURCES = {
    1222: ("1222", "1222", "222", "powershell-variable-parameter-test"),
    1223: ("1223", "1223", "222", "powershell-variable-selection-test"),
    1224: ("1224", "1224", "22081201", "deviceguard-variable-parameters-test"),
}
VARS = {
    "1222": "childitem-path-source-variable",
    "1223": "childitem-properties-source-variable",
    "12241": "deviceguard-classname-source-variable",
    "12242": "deviceguard-namespace-source-variable",
}
VAR_IDS = {name: NEW + "var:" + number for number, name in VARS.items()}


def source_to_native(raw):
    require(sha256(raw).hexdigest() == SHA, "original cmdlet source file SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL Definitions root")
    defs = {x.get("id"): x for x in one(root, OD, "definitions")}
    tests = {x.get("id"): x for x in one(root, OD, "tests")}
    objects = {x.get("id"): x for x in one(root, OD, "objects")}
    states = {x.get("id"): x for x in one(root, OD, "states")}
    original_vars = {x.get("id"): x for x in one(root, OD, "variables")}
    require(len(defs) == len(tests) == len(objects) == 6 and
            len(states) == 3 and len(original_vars) == 4,
            "complete original six cmdlet and four local Variable inventory")
    original_values = {}
    for number, name in VARS.items():
        var = original_vars[original_id("var", number)]
        literal = one(var, OD, "literal_component")
        require(var.tag == tag(OD, "local_variable") and
                var.get("datatype") == "string" and len(var) == 1 and
                isinstance(literal.text, str),
                "exact original local literal Variable " + number)
        original_values[name] = literal.text

    docs = []
    for n, (tid, oid, sid, name) in SOURCES.items():
        definition = defs[original_def(n)]
        test = tests[original_id("tst", tid)]
        obj = objects[original_id("obj", oid)]
        state = states[original_id("ste", sid)]
        require(definition.get("class") == "compliance" and
                test.tag == tag(WIN, "cmdlet_test") and
                test.get("check_existence") == "at_least_one_exists" and
                test.get("check") in REQUIRE and
                one(test, WIN, "object").get("object_ref") == obj.get("id") and
                one(test, WIN, "state").get("state_ref") == state.get("id") and
                obj.tag == tag(WIN, "cmdlet_object") and
                state.tag == tag(WIN, "cmdlet_state"),
                "original cmdlet Variable Test/State pairing")
        collection = {}
        for field in ("module_name", "module_id", "module_version", "verb", "noun"):
            src = one(obj, WIN, field)
            require(src.get("var_ref") is None and
                    src.get("operation", "equals") == "equals",
                    "source cmdlet module/verb/noun literals")
            collection[field] = (None if src.get(tag(XSI, "nil")) == "true"
                                 else src.text)
        variable_names = set()
        for key in ("parameters", "select"):
            source_record = one(obj, WIN, key)
            require(source_record.get("datatype") == "record" and
                    len(source_record) > 0, "source cmdlet record " + key)
            fields = {}
            for field in source_record:
                require(field.tag == tag(OD, "field") and
                        field.get("name") not in fields and
                        field.get("operation", "equals") == "equals",
                        "source record field identity/equals")
                if field.get("var_ref"):
                    vref = field.get("var_ref")
                    number = vref.rsplit(":", 1)[-1]
                    require(vref in original_vars and number in VARS and
                            field.text is None,
                            "source record references pinned local Variable")
                    varname = VARS[number]
                    variable_names.add(varname)
                    fields[field.get("name")] = {
                        "equals": {"variable": varname},
                        "selection_match": "all", "value_match": "all"}
                else:
                    require(isinstance(field.text, str), "literal record field text")
                    fields[field.get("name")] = {
                        "equals": field.text, "selection_match": "all"}
            collection[key] = {"fields": fields}
        require(len(obj) == 7 and variable_names,
                "source Object has record-field Variable references")
        value = one(state, WIN, "value")
        require(value.get("datatype") == "record" and len(state) == 1 and
                value.get("entity_check", "all") in REQUIRE,
                "source State value is structured record")
        fields = {}
        for field in value:
            require(field.tag == tag(OD, "field") and
                    field.get("operation", "equals") in OPERATORS and
                    field.get("name") not in fields and
                    isinstance(field.text, str),
                    "original record State compare field")
            fields[field.get("name")] = {
                OPERATORS[field.get("operation", "equals")]: field.text,
                "require": REQUIRE["all"],
            }
        criteria = one(definition, OD, "criteria")
        criterion = one(criteria, OD, "criterion")
        require(len(criteria) == 1 and
                criteria.get("operator", "AND") == "AND" and
                criterion.get("test_ref") == test.get("id"),
                "one source cmdlet criterion")
        evaluate = {"test": name}
        if criteria.get("negate", "false") == "true" or (
                criterion.get("negate", "false") == "true"):
            evaluate = {"not": evaluate}
        native_vars = {
            vname: {"kind": "local", "datatype": "string",
                    "title": "Source local literal " + vname,
                    "expression": {"literal": [original_values[vname]]}}
            for vname in sorted(variable_names)
        }
        doc = {"assessment": {
            "id": assessment_id(n), "version": int(definition.get("version")),
            "assessment_title": one(one(definition, OD, "metadata"), OD, "title").text,
            "mode": "automated", "class": "compliance",
            "purpose": "assessment", "specification": SPECS,
            "variables": native_vars,
            "tests": {name: {
                "test_title": test.get("comment"),
                "capability": "windows.cmdlet",
                "object": {"capability": "windows.cmdlet", **collection},
                "states": [{"value": {"record": {
                    "require": REQUIRE[value.get("entity_check", "all")],
                    "fields": fields}}}],
                "reported_elements": "all", "require": REQUIRE[test.get("check")],
            }},
            "evaluate": evaluate,
        }}
        docs.append(doc)
    require(len(docs) == 3, "all three original cmdlet Variable Definitions")
    require(set().union(*(set(d["assessment"]["variables"]) for d in docs)) ==
            set(VARS.values()), "all four original local Variables represented")
    return docs


def native_to_oval(docs):
    require(isinstance(docs, list) and len(docs) == 3,
            "three native record Variable cmdlet Assessments")
    bynum = {}
    all_vars = {}
    for doc in docs:
        require(set(doc) == {"assessment"}, "native Assessment root")
        a = doc["assessment"]
        require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                           "purpose", "specification", "variables", "tests", "evaluate"} and
                a["id"] in {assessment_id(n) for n in SOURCES} and
                a["mode"] == "automated" and
                a["class"] == "compliance" and a["purpose"] == "assessment" and
                a["specification"] == SPECS,
                "native cmdlet Variable Assessment identity")
        n = int(a["id"].split("-")[3])
        require(n not in bynum and a["version"] in (1, 3),
                "unique variable-driven source Definition")
        name = SOURCES[n][3]
        require(set(a["tests"]) == {name} and
                a["evaluate"] in ({"test": name}, {"not": {"test": name}}),
                "one original cmdlet Variable Test in expression")
        t = a["tests"][name]
        require(set(t) == {"test_title", "capability", "object", "states",
                           "reported_elements", "require"} and
                t["capability"] == "windows.cmdlet" and
                t["require"] in INVERSE and t["reported_elements"] == "all" and
                isinstance(t["test_title"], str),
                "native cmdlet Variable Test semantics")
        coll = t["object"]
        require(set(coll) == {"capability", "module_name", "module_id",
                              "module_version", "verb", "noun", "parameters", "select"} and
                coll["capability"] == "windows.cmdlet" and
                all(coll[key] is None or isinstance(coll[key], str)
                    for key in ("module_name", "module_id", "module_version")) and
                all(isinstance(coll[key], str) for key in ("verb", "noun")),
                "flat typed cmdlet collector contract")
        used_vars = set()
        for key in ("parameters", "select"):
            require(set(coll[key]) == {"fields"} and
                    len(coll[key]["fields"]) > 0,
                    "structured cmdlet Object record " + key)
            for field in coll[key]["fields"].values():
                require(field.get("selection_match") == "all",
                        "record Object field selection cardinality")
                if isinstance(field.get("equals"), dict):
                    require(set(field) == {"equals", "selection_match", "value_match"} and
                            set(field["equals"]) == {"variable"} and
                            field["value_match"] == "all" and
                            field["equals"]["variable"] in VARS.values(),
                            "local Variable record field binding")
                    used_vars.add(field["equals"]["variable"])
                else:
                    require(set(field) == {"equals", "selection_match"} and
                            isinstance(field["equals"], str),
                            "literal structured cmdlet field")
        require(set(a["variables"]) == used_vars and used_vars,
                "native source record Variables all used")
        for varname, var in a["variables"].items():
            require(var.get("kind") == "local" and
                    var.get("datatype") == "string" and
                    set(var) == {"kind", "datatype", "title", "expression"} and
                    isinstance(var.get("title"), str) and
                    set(var["expression"]) == {"literal"} and
                    isinstance(var["expression"]["literal"], list) and
                    len(var["expression"]["literal"]) == 1 and
                    isinstance(var["expression"]["literal"][0], str),
                    "original local Variable expression and literal")
            prior = all_vars.setdefault(varname, var)
            require(prior == var, "shared local Variable consistency")
        state = t["states"]
        require(len(state) == 1 and set(state[0]) == {"value"} and
                set(state[0]["value"]) == {"record"},
                "one structured cmdlet State record")
        record = state[0]["value"]["record"]
        require(set(record) == {"require", "fields"} and
                record["require"] in INVERSE and record["fields"],
                "record parent requirement")
        for field in record["fields"].values():
            op = set(field) - {"require"}
            require(len(op) == 1 and next(iter(op)) in INVERSE_OPS and
                    field.get("require") == REQUIRE["all"] and
                    isinstance(field[next(iter(op))], str),
                    "record State field comparison and cardinality")
        bynum[n] = a
    require(set(bynum) == set(SOURCES) and
            set(all_vars) == set(VARS.values()),
            "three original Definitions and four distinct local Variables")

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("win-def", WIN)
    ET.register_namespace("xsi", XSI)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 cmdlet local Variable proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    states = ET.SubElement(root, tag(OD, "states"))
    variables = ET.SubElement(root, tag(OD, "variables"))
    for n in SOURCES:
        a = bynum[n]
        name = SOURCES[n][3]
        t = a["tests"][name]
        definition = ET.SubElement(defs, tag(OD, "definition"), {
            "id": NEW + "def:" + str(n), "version": str(a["version"]),
            "class": "compliance"})
        meta = ET.SubElement(definition, tag(OD, "metadata"))
        ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
        ET.SubElement(meta, tag(OD, "description")).text = "Cmdlet record local Variable proof"
        criteria = ET.SubElement(definition, tag(OD, "criteria"), {
            "operator": "AND",
            **({"negate": "true"} if "not" in a["evaluate"] else {})})
        ET.SubElement(criteria, tag(OD, "criterion"), {"test_ref": NEW + "tst:" + str(n)})
        test = ET.SubElement(tests, tag(WIN, "cmdlet_test"), {
            "id": NEW + "tst:" + str(n), "version": "1", "comment": t["test_title"],
            "check_existence": "at_least_one_exists", "check": INVERSE[t["require"]]})
        ET.SubElement(test, tag(WIN, "object"), {"object_ref": NEW + "obj:" + str(n)})
        ET.SubElement(test, tag(WIN, "state"), {"state_ref": NEW + "ste:" + str(n)})
        obj = ET.SubElement(objects, tag(WIN, "cmdlet_object"), {
            "id": NEW + "obj:" + str(n), "version": "1"})
        coll = t["object"]
        for key in ("module_name", "module_id", "module_version", "verb", "noun"):
            attrs = {"datatype": "version"} if key == "module_version" else {}
            if coll[key] is None:
                attrs[tag(XSI, "nil")] = "true"
            element = ET.SubElement(obj, tag(WIN, key), attrs)
            if coll[key] is not None:
                element.text = coll[key]
        for key in ("parameters", "select"):
            record = ET.SubElement(obj, tag(WIN, key), {"datatype": "record"})
            for label, field in coll[key]["fields"].items():
                attrs = {"name": label}
                if isinstance(field["equals"], dict):
                    attrs["var_ref"] = VAR_IDS[field["equals"]["variable"]]
                element = ET.SubElement(record, tag(OD, "field"), attrs)
                if isinstance(field["equals"], str):
                    element.text = field["equals"]
        s = ET.SubElement(states, tag(WIN, "cmdlet_state"), {
            "id": NEW + "ste:" + str(n), "version": "1"})
        record = t["states"][0]["value"]["record"]
        attrs = {"datatype": "record"}
        if record["require"] != REQUIRE["all"]:
            attrs["entity_check"] = INVERSE[record["require"]]
        value = ET.SubElement(s, tag(WIN, "value"), attrs)
        for label, field in record["fields"].items():
            op = next(key for key in INVERSE_OPS if key in field)
            ET.SubElement(value, tag(OD, "field"), {
                "name": label, "operation": INVERSE_OPS[op]}).text = field[op]
    for name, var in all_vars.items():
        element = ET.SubElement(variables, tag(OD, "local_variable"), {
            "id": VAR_IDS[name], "version": "1", "datatype": "string",
            "comment": var["title"]})
        ET.SubElement(element, tag(OD, "literal_component")).text = (
            var["expression"]["literal"][0])
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    docs = source_to_native(raw)
    validate_docs({f"authoring/{x['assessment']['id']}.json": x for x in docs},
                  _schema_validators(schema_root))
    generated = materialize("windows.cmdlet")
    for doc in docs:
        test = next(iter(doc["assessment"]["tests"].values()))
        errors = validate(generated, "test", test)
        require(not errors, "native cmdlet record Variable schema " + str(errors[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessments.json").write_text(json.dumps(docs, indent=2) + "\n")
    yml = "---\n".join(dump_hybrid(doc) for doc in docs)
    require(list(yaml.safe_load_all(yml)) == docs, "three native YAML/JSON graphs")
    (out / "native-040.assessments.yaml").write_text(yml)
    regenerated = native_to_oval(docs)
    exported = out / "roundtrip-oval.xml"
    regenerated.write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "windows")
    require(xsd["status"] == "PASS", "original OVAL 5.12.3 Windows XSD " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    semantics = {}
    for n in SOURCES:
        sem = compare(source, exported, source_root=original_def(n),
                      regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sem["equal"], "original cmdlet local Variable root " + str(n))
        semantics[str(n)] = sem
    (out / "roundtrip-semantics.json").write_text(
        json.dumps(semantics, indent=2, sort_keys=True) + "\n")
    altered_source = raw.replace(b'var_ref="oval:navy.navwar.niwcatlantic.scc.test:var:1222"',
                                 b'var_ref="oval:navy.navwar.niwcatlantic.scc.test:var:1223"', 1)
    require(altered_source != raw, "construct original Variable ref mutation")
    try:
        source_to_native(altered_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed original record Variable")
    changed = deepcopy(docs)
    first = next(x for x in changed if x["assessment"]["id"] == assessment_id(1222))
    key = VARS["1222"]
    first["assessment"]["variables"][key]["expression"]["literal"][0] += "-altered"
    wrong = out / "mutated-local-variable.xml"
    native_to_oval(changed).write(wrong, encoding="utf-8", xml_declaration=True)
    sem = compare(source, wrong, source_root=original_def(1222),
                  regenerated_root=NEW + "def:1222", root_only=True)
    require(not sem["equal"], "local Variable literal mutation changes source graph")
    proof = {
        "source_revision": PIN, "source_file": FILE, "original_xml_sha256": SHA,
        "original_definition_ids": [original_def(n) for n in SOURCES],
        "definition_count": 3, "original_test_count": 3, "local_variable_count": 4,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_three_root_semantic_graphs": "PASS",
        "source_variable_reference_mutation": "REJECTED",
        "native_local_literal_mutation": "DETECTED",
        "record_variable_links_preserved": "PASS", "scanner_parity": False,
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
