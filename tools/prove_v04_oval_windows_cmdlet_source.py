#!/usr/bin/env python3
"""Three original Windows cmdlet Definitions -> native 0.4 -> OVAL 5.12.3.

Scoped to source-pinned variable-free Tests 222, 22081201 and 999. Their
structured Object parameter/select records and State value records are not
flattened. The other three source Definitions use Variables and remain
unproven. Source semantics, not observed scanner behavior. Refs #248 #229 #232.
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
FILE = "windows/win-def_cmdlet_test.xml"
SHA = "cd2240c929bbd1171461035e7fd8b4336fd505ce1687c1f178af7a800fb50c33"
OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
WIN = OD + "#windows"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
ORIGINAL = "oval:navy.navwar.niwcatlantic.scc.test:"
NEW = "oval:scapng.04.cmdlet:"
SPECS = {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}
SOURCES = {
    222: ("222", "222", "222", "powershell-childitem-test"),
    220812: ("22081201", "22081200", "22081201",
             "deviceguard-security-services-test"),
    999: ("999", "999", "22081200", "deviceguard-property-selection-test"),
}
REQUIRE = {"all": "at_least_one_exists_and_all_match",
           "only one": "at_least_one_exists_and_only_one_matches"}
INVERSE = {v: k for k, v in REQUIRE.items()}
OPERATORS = {"case insensitive equals": "case_insensitive_equals",
             "pattern match": "matches_regex"}
INVERSE_OPS = {v: k for k, v in OPERATORS.items()}


def tag(namespace, name):
    return "{" + namespace + "}" + name


def require(ok, reason):
    if not ok:
        raise ValueError("pinned original Windows cmdlet source: " + reason)


def one(parent, namespace, local):
    found = parent.findall(tag(namespace, local))
    require(len(found) == 1, "one source " + local)
    return found[0]


def original_def(n):
    return ORIGINAL + "def:" + str(n)


def assessment_id(n):
    return "original-windows-cmdlet-" + str(n) + "-assessment"


def original_id(kind, number):
    return ORIGINAL + kind + ":" + number


def _read_source_view(raw):
    require(sha256(raw).hexdigest() == SHA, "original source XML SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL XML namespace")
    defmap = {x.get("id"): x for x in one(root, OD, "definitions")}
    testmap = {x.get("id"): x for x in one(root, OD, "tests")}
    objmap = {x.get("id"): x for x in one(root, OD, "objects")}
    statemap = {x.get("id"): x for x in one(root, OD, "states")}
    require(len(defmap) == 6 and len(testmap) == 6 and len(objmap) == 6 and
            len(statemap) == 3, "original source full six-Definition graph")
    docs = []
    for n, (test_number, object_number, state_number, test_name) in SOURCES.items():
        definition = defmap[original_def(n)]
        test = testmap[original_id("tst", test_number)]
        obj = objmap[original_id("obj", object_number)]
        state = statemap[original_id("ste", state_number)]
        require(definition.get("class") == "compliance" and
                test.tag == tag(WIN, "cmdlet_test") and
                test.get("check_existence") == "at_least_one_exists" and
                test.get("check") in REQUIRE and
                one(test, WIN, "object").get("object_ref") == obj.get("id") and
                one(test, WIN, "state").get("state_ref") == state.get("id") and
                obj.tag == tag(WIN, "cmdlet_object") and
                state.tag == tag(WIN, "cmdlet_state"),
                "source original cmdlet Test/Object/State graph " + str(n))
        collection = {}
        for field in ("module_name", "module_id", "module_version", "verb", "noun"):
            element = one(obj, WIN, field)
            require(set(element.attrib) <= {"operation", "datatype", tag(XSI, "nil")}
                    and element.get("operation", "equals") == "equals" and
                    element.get("var_ref") is None,
                    "literal nonvariable cmdlet field " + field)
            if element.get(tag(XSI, "nil")) == "true":
                require(element.text is None, "OVAL xsi:nil cannot have text")
                collection[field] = None
            else:
                collection[field] = element.text
                require(isinstance(element.text, str), "literal cmdlet field")
        for record_name in ("parameters", "select"):
            record = one(obj, WIN, record_name)
            require(record.get("datatype") == "record" and len(record) > 0,
                    "source structured Object record " + record_name)
            fields = {}
            for field in record:
                require(field.tag == tag(OD, "field") and
                        field.get("name") not in fields and
                        field.get("var_ref") is None and
                        field.get("operation", "equals") == "equals" and
                        isinstance(field.text, str),
                        "source literal record selection field")
                fields[field.get("name")] = {
                    "equals": field.text, "selection_match": "all"}
            collection[record_name] = {"fields": fields}
        require(len(obj) == 7, "seven independent cmdlet collector parameters")
        observed = one(state, WIN, "value")
        require(observed.get("datatype") == "record" and len(state) == 1 and
                observed.get("entity_check", "all") in REQUIRE,
                "original State is a typed record with explicit parent entity check")
        fields = {}
        for field in observed:
            require(field.tag == tag(OD, "field") and
                    field.get("name") not in fields and
                    field.get("operation", "equals") in OPERATORS and
                    isinstance(field.text, str) and
                    field.get("var_ref") is None,
                    "source record State field comparison")
            fields[field.get("name")] = {
                OPERATORS[field.get("operation", "equals")]: field.text,
                "require": REQUIRE["all"],
            }
        criteria = one(definition, OD, "criteria")
        criterion = one(criteria, OD, "criterion")
        require(len(criteria) == 1 and
                criteria.get("operator", "AND") == "AND" and
                criterion.get("test_ref") == test.get("id"),
                "original single cmdlet Test criterion")
        expression = {"test": test_name}
        if criteria.get("negate", "false") == "true" or (
                criterion.get("negate", "false") == "true"):
            require(not (criteria.get("negate") == "true" and
                         criterion.get("negate") == "true"),
                    "single source Boolean negation")
            expression = {"not": expression}
        title = one(one(definition, OD, "metadata"), OD, "title").text
        doc = {"assessment": {
            "id": assessment_id(n), "version": int(definition.get("version")),
            "assessment_title": title, "mode": "automated",
            "class": "compliance", "purpose": "assessment",
            "specification": SPECS,
            "tests": {test_name: {
                "test_title": test.get("comment"), "capability": "windows.cmdlet",
                "object": {"capability": "windows.cmdlet", **collection},
                "states": [{"value": {"record": {
                    "require": REQUIRE[observed.get("entity_check", "all")],
                    "fields": fields}}}],
                "reported_elements": "all", "require": REQUIRE[test.get("check")],
            }},
            "evaluate": expression,
        }}
        docs.append(doc)
    require(len(docs) == 3, "three fully scoped variable-free original cmdlet Tests")
    return docs


def _export_source_view(docs):
    require(isinstance(docs, list) and len(docs) == 3,
            "three native cmdlet Assessments")
    docs_by_num = {}
    for doc in docs:
        require(set(doc) == {"assessment"}, "native Assessment root")
        a = doc["assessment"]
        require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                           "purpose", "specification", "tests", "evaluate"} and
                a.get("id") in {assessment_id(n) for n in SOURCES} and
                a.get("mode") == "automated" and
                a.get("class") == "compliance" and
                a.get("purpose") == "assessment" and
                a.get("specification") == SPECS,
                "native exact source Assessment identity")
        n = int(a["id"].split("-")[3])
        require(n not in docs_by_num and a["version"] in (1, 3),
                "unique source Definition version")
        docmap = SOURCES[n]
        name = docmap[3]
        require(set(a["tests"]) == {name} and
                a["evaluate"] in ({"test": name}, {"not": {"test": name}}),
                "native single-Test evaluation graph")
        t = a["tests"][name]
        require(set(t) == {"test_title", "capability", "object", "states",
                           "reported_elements", "require"} and
                t["capability"] == "windows.cmdlet" and
                isinstance(t["test_title"], str) and
                t["reported_elements"] == "all" and
                t["require"] in INVERSE and
                isinstance(t["states"], list) and len(t["states"]) == 1,
                "native independent Test result/existence")
        coll = t["object"]
        require(set(coll) == {"capability", "module_name", "module_id",
                              "module_version", "verb", "noun", "parameters", "select"} and
                coll["capability"] == "windows.cmdlet" and
                all(coll[x] is None or isinstance(coll[x], str)
                    for x in ("module_name", "module_id", "module_version")) and
                all(isinstance(coll[x], str) for x in ("verb", "noun")),
                "structured cmdlet Object fields")
        for key in ("parameters", "select"):
            require(set(coll[key]) == {"fields"} and
                    len(coll[key]["fields"]) > 0, "one original record Object " + key)
            for field in coll[key]["fields"].values():
                require(set(field) == {"equals", "selection_match"} and
                        field["selection_match"] == "all" and
                        isinstance(field["equals"], str),
                        "record field literal and selection cardinality")
        record = t["states"][0].get("value", {}).get("record", {})
        require(set(t["states"][0]) == {"value"} and
                set(t["states"][0]["value"]) == {"record"} and
                set(record) == {"require", "fields"} and
                record["require"] in INVERSE and
                isinstance(record["fields"], dict) and len(record["fields"]) > 0,
                "native record State matching scope")
        for field in record["fields"].values():
            require(set(field) == {"require", *set(INVERSE_OPS) & set(field)} and
                    field["require"] == REQUIRE["all"] and
                    sum(k in field for k in INVERSE_OPS) == 1,
                    "one reviewed record State field comparison")
        docs_by_num[n] = a
    require(set(docs_by_num) == set(SOURCES), "all three native source Definitions")

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("win-def", WIN)
    ET.register_namespace("xsi", XSI)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 original Windows cmdlet proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    states = ET.SubElement(root, tag(OD, "states"))
    for n in SOURCES:
        a = docs_by_num[n]
        name = SOURCES[n][3]
        t = a["tests"][name]
        definition = ET.SubElement(defs, tag(OD, "definition"), {
            "id": NEW + "def:" + str(n), "version": str(a["version"]),
            "class": "compliance"})
        metadata = ET.SubElement(definition, tag(OD, "metadata"))
        ET.SubElement(metadata, tag(OD, "title")).text = a["assessment_title"]
        ET.SubElement(metadata, tag(OD, "description")).text = "PowerShell cmdlet record proof"
        root_expr = a["evaluate"]
        criteria = ET.SubElement(definition, tag(OD, "criteria"), {
            "operator": "AND",
            **({"negate": "true"} if "not" in root_expr else {})})
        ET.SubElement(criteria, tag(OD, "criterion"), {
            "test_ref": NEW + "tst:" + str(n)})
        test = ET.SubElement(tests, tag(WIN, "cmdlet_test"), {
            "id": NEW + "tst:" + str(n), "version": "1", "comment": t["test_title"],
            "check_existence": "at_least_one_exists", "check": INVERSE[t["require"]]})
        ET.SubElement(test, tag(WIN, "object"), {
            "object_ref": NEW + "obj:" + str(n)})
        ET.SubElement(test, tag(WIN, "state"), {
            "state_ref": NEW + "ste:" + str(n)})
        obj = ET.SubElement(objects, tag(WIN, "cmdlet_object"), {
            "id": NEW + "obj:" + str(n), "version": "1"})
        coll = t["object"]
        for key in ("module_name", "module_id", "module_version", "verb", "noun"):
            props = {"datatype": "version"} if key == "module_version" else {}
            if coll[key] is None:
                props[tag(XSI, "nil")] = "true"
            node = ET.SubElement(obj, tag(WIN, key), props)
            if coll[key] is not None:
                node.text = coll[key]
        for key in ("parameters", "select"):
            record = ET.SubElement(obj, tag(WIN, key), {"datatype": "record"})
            for label, item in coll[key]["fields"].items():
                ET.SubElement(record, tag(OD, "field"), {"name": label}).text = item["equals"]
        state = ET.SubElement(states, tag(WIN, "cmdlet_state"), {
            "id": NEW + "ste:" + str(n), "version": "1"})
        native_record = t["states"][0]["value"]["record"]
        attrs = {"datatype": "record"}
        if native_record["require"] != REQUIRE["all"]:
            attrs["entity_check"] = INVERSE[native_record["require"]]
        value = ET.SubElement(state, tag(WIN, "value"), attrs)
        for label, field in native_record["fields"].items():
            op = next(k for k in INVERSE_OPS if k in field)
            ET.SubElement(value, tag(OD, "field"), {
                "name": label, "operation": INVERSE_OPS[op]}).text = field[op]
    return ET.ElementTree(root)


def source_to_native(raw):
    from v04_source_proof_contract import current_document
    source = _read_source_view(raw)
    return [current_document(doc) for doc in source]


def native_to_oval(document):
    from v04_source_proof_contract import independent_export_view
    return _export_source_view([independent_export_view(doc) for doc in document])


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
        require(not errors, "native cmdlet capability schema " + str(errors[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessments.json").write_text(json.dumps(docs, indent=2) + "\n")
    yml = "---\n".join(dump_hybrid(doc) for doc in docs)
    require(list(yaml.safe_load_all(yml)) == docs, "three YAML/JSON Assessment graphs")
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
        require(sem["equal"], "original structured cmdlet Definition " + str(n))
        semantics[str(n)] = sem
    (out / "roundtrip-semantics.json").write_text(
        json.dumps(semantics, sort_keys=True, indent=2) + "\n")
    altered_source = raw.replace(b'check="only one"', b'check="all"', 1)
    require(altered_source != raw, "construct original only-one mutation")
    try:
        source_to_native(altered_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted altered source only-one result")
    mutated = deepcopy(docs)
    test = next(iter(mutated[0]["assessment"]["tests"].values()))
    test["require"]["items_satisfying"] = "every"
    wrong = out / "mutated-only-one-to-all.xml"
    native_to_oval(mutated).write(wrong, encoding="utf-8", xml_declaration=True)
    sem = compare(source, wrong, source_root=original_def(222),
                  regenerated_root=NEW + "def:222", root_only=True)
    require(not sem["equal"], "source only-one differs from all")
    for n in SOURCES:
        a = next(doc for doc in docs if doc["assessment"]["id"] == assessment_id(n))
        coll = next(iter(a["assessment"]["tests"].values()))["object"]
        require(set(coll["parameters"]) == {"fields"} and
                set(coll["select"]) == {"fields"},
                "source record Object fields never flattened into strings")
    proof = {
        "source_revision": PIN, "source_file": FILE, "original_xml_sha256": SHA,
        "original_definition_ids": [original_def(n) for n in SOURCES],
        "definition_count": 3, "original_test_count": 3,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_three_root_semantic_graphs": "PASS",
        "source_only_one_mutation": "REJECTED",
        "native_only_one_to_all": "DETECTED",
        "record_structure_preserved": "PASS", "scanner_parity": False,
    }
    from v04_source_proof_contract import compile_proofs
    proof["current_compilation"] = compile_proofs(docs, out / "compiled")
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
