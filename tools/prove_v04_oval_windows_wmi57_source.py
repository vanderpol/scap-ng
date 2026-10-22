#!/usr/bin/env python3
"""Five pinned Windows wmi57 Definitions -> native 0.4 -> OVAL 5.12.3.

Exercises typed WMI record results, shared/duplicate source States, source
`none_exist` Tests without States and literal single/double-quoted WQL.
Original semantic graphs and XSD, not scanner execution parity.
Refs #248 #229 #232.
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
    OD, OC, WIN, SPECS, tag, require, one,
)

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
FILE = "windows/win-def_wmi57_object_test.xml"
SHA = "ac9a8bc062d9a261624eefc963da7cc3e190be96519da5369054d1bde8a52cdb"
OLD = "oval:org.mitre.oval.test:"
NEW = "oval:scapng.04.wmi57:"
SOURCES = (10, 20, 30, 70, 80)
CAPABILITY = "windows.wmi.query"
REQUIRE = {"at_least_one_exists": "at_least_one_exists_and_all_match",
           "none_exist": "none_exist"}
RESULT_REQUIRE = {"all": "at_least_one_exists_and_all_match",
                  "at least one": "at_least_one_exists_and_some_match"}
OP = {"equals": "equals", "greater than or equal": "greater_than_or_equal",
      "pattern match": "matches_regex"}
INVERSE_OP = {v: k for k, v in OP.items()}


def source_id(kind, number):
    return OLD + kind + ":" + str(number)


def assessment_id(number):
    return "original-windows-wmi57-" + str(number) + "-assessment"


def parse_source(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned WMI57 original XML SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "pinned WMI57 root namespace")
    ds = {x.get("id"): x for x in one(root, OD, "definitions")}
    ts = {x.get("id"): x for x in one(root, OD, "tests")}
    os = {x.get("id"): x for x in one(root, OD, "objects")}
    ss = {x.get("id"): x for x in one(root, OD, "states")}
    require(len(ds) == len(ts) == len(os) == len(SOURCES) and len(ss) == 2,
            "source five Definition/Test/Object records and two shared States")
    docs = []
    for n in SOURCES:
        d = ds[source_id("def", n)]
        t = ts[source_id("tst", n)]
        o = os[source_id("obj", n)]
        check_exist = t.get("check_existence")
        require(d.get("class") == "miscellaneous" and
                t.tag == tag(WIN, "wmi57_test") and
                t.get("check") == "all" and check_exist in REQUIRE and
                one(t, WIN, "object").get("object_ref") == o.get("id") and
                o.tag == tag(WIN, "wmi57_object") and
                len(o) == 2 and
                len(d.findall(tag(OD, "criteria"))) == 1,
                "complete original WMI57 Test/Object linkage")
        criterion = one(one(d, OD, "criteria"), OD, "criterion")
        require(criterion.get("test_ref") == t.get("id"),
                "WMI57 source Definition criterion Test reference")
        namespace = one(o, WIN, "namespace")
        query = one(o, WIN, "wql")
        require(namespace.get("operation", "equals") == "equals" and
                query.get("operation", "equals") == "equals" and
                namespace.get("var_ref") is None and query.get("var_ref") is None and
                isinstance(namespace.text, str) and isinstance(query.text, str),
                "literal WMI57 namespace and full WQL acquisition query")
        test = {
            "test_title": t.get("comment"), "capability": CAPABILITY,
            "object": {"capability": CAPABILITY, "namespace": namespace.text,
                       "query": query.text},
            "reported_elements": "all", "require": REQUIRE[check_exist],
        }
        if check_exist == "at_least_one_exists":
            require(len(t.findall(tag(WIN, "state"))) == 1,
                    "original tested WMI result State")
            ref = one(t, WIN, "state").get("state_ref")
            require(ref in ss, "source WMI57 result State reference")
            s = ss[ref]
            require(s.tag == tag(WIN, "wmi57_state") and len(s) == 3,
                    "original WMI57 State has namespace, WQL, result")
            fields = {}
            for original, mapped in (("namespace", "namespace"), ("wql", "query")):
                child = one(s, WIN, original)
                require(child.get("operation", "equals") == "equals" and
                        isinstance(child.text, str), "literal WMI State " + original)
                fields[mapped] = {"equals": child.text,
                                  "require": RESULT_REQUIRE["all"]}
            result = one(s, WIN, "result")
            require(result.get("datatype") == "record" and
                    result.get("entity_check", "all") in RESULT_REQUIRE and
                    len(result) > 0, "typed original WMI result record")
            record = {}
            for field in result:
                operation = field.get("operation", "equals")
                name = field.get("name")
                datatype = field.get("datatype", "string")
                require(field.tag == tag(OD, "field") and
                        operation in OP and name not in record and
                        datatype in ("int", "string") and field.text is not None,
                        "source typed WMI record member")
                value = int(field.text) if datatype == "int" else field.text
                record[name] = {OP[operation]: value,
                                "require": RESULT_REQUIRE["all"]}
            fields["result"] = {"record": {
                "require": RESULT_REQUIRE[result.get("entity_check", "all")],
                "fields": record}}
            # The canonical State grammar requires an explicit AND for these
            # three independently evaluated OVAL State entities.
            test["states"] = [{"and": [{key: fields[key]}
                                      for key in ("namespace", "query", "result")]}]
        else:
            require(not t.findall(tag(WIN, "state")),
                    "none_exist Test must omit original State")
        doc = {"assessment": {
            "id": assessment_id(n), "version": int(d.get("version")),
            "assessment_title": one(one(d, OD, "metadata"), OD, "title").text,
            "mode": "automated", "class": "miscellaneous",
            "purpose": "assessment", "specification": SPECS,
            "tests": {"wmi-query-test": test},
            "evaluate": {"test": "wmi-query-test"},
        }}
        docs.append(doc)
    return docs


def native_to_oval(docs):
    require(isinstance(docs, list) and len(docs) == len(SOURCES),
            "native five WMI57 Assessments")
    keyed = {}
    for doc in docs:
        require(set(doc) == {"assessment"}, "one native Assessment")
        a = doc["assessment"]
        require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                           "purpose", "specification", "tests", "evaluate"} and
                a["id"] in {assessment_id(n) for n in SOURCES} and
                a["version"] == 1 and a["mode"] == "automated" and
                a["class"] == "miscellaneous" and
                a["purpose"] == "assessment" and
                a["specification"] == SPECS and
                a["evaluate"] == {"test": "wmi-query-test"} and
                set(a["tests"]) == {"wmi-query-test"},
                "canonical WMI57 Assessment structure")
        n = int(a["id"].split("-")[3])
        require(n not in keyed, "unique native WMI57 Definition")
        t = a["tests"]["wmi-query-test"]
        require(t["capability"] == CAPABILITY and
                t.get("reported_elements") == "all" and
                t.get("require") == ("none_exist" if n in (70, 80) else
                                      "at_least_one_exists_and_all_match") and
                t["object"]["capability"] == CAPABILITY and
                set(t["object"]) == {"capability", "namespace", "query"} and
                isinstance(t["object"]["namespace"], str) and
                isinstance(t["object"]["query"], str),
                "native typed WMI query/existence")
        if n in (70, 80):
            require(set(t) == {"test_title", "capability", "object",
                               "reported_elements", "require"},
                    "none_exist needs no State")
        else:
            require(set(t) == {"test_title", "capability", "object", "states",
                               "reported_elements", "require"} and
                    isinstance(t["states"], list) and len(t["states"]) == 1,
                    "explicit WMI State for positive result")
            groups = t["states"][0]
            require(set(groups) == {"and"} and isinstance(groups["and"], list)
                    and len(groups["and"]) == 3 and
                    [list(x) for x in groups["and"]] ==
                    [["namespace"], ["query"], ["result"]],
                    "explicit WMI namespace/query/result State conjunction")
            s = {k: v for group in groups["and"] for k, v in group.items()}
            for key in ("namespace", "query"):
                require(set(s[key]) == {"equals", "require"} and
                        s[key]["require"] == RESULT_REQUIRE["all"] and
                        isinstance(s[key]["equals"], str),
                        "native WMI literal State " + key)
            record = s["result"]["record"]
            require(set(record) == {"require", "fields"} and
                    record["require"] == RESULT_REQUIRE["at least one"] and
                    isinstance(record["fields"], dict) and record["fields"],
                    "WMI typed result record parent cardinality")
            for f in record["fields"].values():
                op = set(f) - {"require"}
                require(len(op) == 1 and next(iter(op)) in INVERSE_OP and
                        f["require"] == RESULT_REQUIRE["all"] and
                        isinstance(f[next(iter(op))], (str, int)),
                        "WMI result record typed field compare")
        keyed[n] = a
    require(set(keyed) == set(SOURCES), "all five WMI57 Assessments")

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("win-def", WIN)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG 0.4 WMI57 source proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    tests = ET.SubElement(root, tag(OD, "tests"))
    objects = ET.SubElement(root, tag(OD, "objects"))
    states = ET.SubElement(root, tag(OD, "states"))
    for n in SOURCES:
        a = keyed[n]
        t = a["tests"]["wmi-query-test"]
        d = ET.SubElement(defs, tag(OD, "definition"), {
            "id": NEW + "def:" + str(n), "version": "1", "class": "miscellaneous"})
        m = ET.SubElement(d, tag(OD, "metadata"))
        ET.SubElement(m, tag(OD, "title")).text = a["assessment_title"]
        ET.SubElement(m, tag(OD, "description")).text = "WMI57 source graph proof"
        criteria = ET.SubElement(d, tag(OD, "criteria"))
        ET.SubElement(criteria, tag(OD, "criterion"), {
            "test_ref": NEW + "tst:" + str(n)})
        tt = ET.SubElement(tests, tag(WIN, "wmi57_test"), {
            "id": NEW + "tst:" + str(n), "version": "1",
            "comment": t["test_title"], "check": "all",
            "check_existence": "none_exist" if n in (70, 80)
                               else "at_least_one_exists"})
        ET.SubElement(tt, tag(WIN, "object"), {
            "object_ref": NEW + "obj:" + str(n)})
        if n not in (70, 80):
            ET.SubElement(tt, tag(WIN, "state"), {
                "state_ref": NEW + "ste:" + str(n)})
        obj = ET.SubElement(objects, tag(WIN, "wmi57_object"), {
            "id": NEW + "obj:" + str(n), "version": "1"})
        ET.SubElement(obj, tag(WIN, "namespace")).text = t["object"]["namespace"]
        ET.SubElement(obj, tag(WIN, "wql")).text = t["object"]["query"]
        if n not in (70, 80):
            s = {k: v for group in t["states"][0]["and"]
                 for k, v in group.items()}
            st = ET.SubElement(states, tag(WIN, "wmi57_state"), {
                "id": NEW + "ste:" + str(n), "version": "1"})
            ET.SubElement(st, tag(WIN, "namespace")).text = s["namespace"]["equals"]
            ET.SubElement(st, tag(WIN, "wql")).text = s["query"]["equals"]
            record = s["result"]["record"]
            re = ET.SubElement(st, tag(WIN, "result"), {
                "datatype": "record", "entity_check": "at least one"})
            for name, f in record["fields"].items():
                op = next(k for k in INVERSE_OP if k in f)
                value = f[op]
                attrs = {"name": name, "operation": INVERSE_OP[op]}
                if isinstance(value, int):
                    attrs["datatype"] = "int"
                ET.SubElement(re, tag(OD, "field"), attrs).text = str(value)
    return ET.ElementTree(root)


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    docs = parse_source(raw)
    validate_docs({f"authoring/{d['assessment']['id']}.json": d for d in docs},
                  _schema_validators(schema_root))
    generated = materialize(CAPABILITY)
    for doc in docs:
        test = doc["assessment"]["tests"]["wmi-query-test"]
        problems = validate(generated, "test", test)
        require(not problems, "generated WMI native capability schema " + str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessments.json").write_text(json.dumps(docs, indent=2) + "\n")
    native_yml = "---\n".join(dump_hybrid(doc) for doc in docs)
    require(list(yaml.safe_load_all(native_yml)) == docs,
            "five native WMI YAML/JSON graphs equal")
    (out / "native-040.assessments.yaml").write_text(native_yml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(docs).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "windows")
    require(xsd["status"] == "PASS", "OVAL Windows 5.12.3 XSD " +
            str(xsd.get("diagnostics", [])[:3]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sems = {}
    for n in SOURCES:
        sem = compare(source, exported, source_root=source_id("def", n),
                      regenerated_root=NEW + "def:" + str(n), root_only=True)
        require(sem["equal"], "original WMI57 source root graph " + str(n))
        sems[str(n)] = sem
    (out / "roundtrip-semantics.json").write_text(json.dumps(
        sems, indent=2, sort_keys=True) + "\n")
    wrong_original = raw.replace(b'filesystem!="NTFS"', b'filesystem="NTFS"', 1)
    require(wrong_original != raw, "original double-quoted WQL mutation")
    try:
        parse_source(wrong_original)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed original WMI WQL source")
    changed = deepcopy(docs)
    next(d for d in changed if d["assessment"]["id"] == assessment_id(20))[
        "assessment"]["tests"]["wmi-query-test"]["object"]["query"] += " AND Test=1"
    wrong = out / "mutated-native-wql.xml"
    native_to_oval(changed).write(wrong, encoding="utf-8", xml_declaration=True)
    sem = compare(source, wrong, source_root=source_id("def", 20),
                  regenerated_root=NEW + "def:20", root_only=True)
    require(not sem["equal"], "changed native WQL changes original graph")
    changed = deepcopy(docs)
    next(d for d in changed if d["assessment"]["id"] == assessment_id(70))[
        "assessment"]["tests"]["wmi-query-test"]["require"] = (
            "at_least_one_exists_and_all_match")
    try:
        native_to_oval(changed)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted changed OVAL none_exist requirement")
    proof = {
        "source_file": FILE, "source_revision": PIN,
        "original_xml_sha256": SHA,
        "original_definition_ids": [source_id("def", n) for n in SOURCES],
        "definition_count": 5, "original_test_count": 5,
        "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
        "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
        "original_five_root_semantic_graphs": "PASS",
        "none_exist_without_state": "PASS", "typed_record_result": "PASS",
        "source_wql_mutation": "REJECTED", "native_wql_mutation": "DETECTED",
        "native_none_exist_mutation": "REJECTED", "scanner_parity": False,
    }
    (out / "source-and-mapping-proof.json").write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n")
    return proof


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", required=True, type=Path)
    p.add_argument("--schema-root", required=True, type=Path)
    p.add_argument("--xsd-root", required=True, type=Path)
    p.add_argument("--output", required=True, type=Path)
    a = p.parse_args()
    print(json.dumps(prove(a.source, a.schema_root, a.xsd_root, a.output),
                     sort_keys=True))
