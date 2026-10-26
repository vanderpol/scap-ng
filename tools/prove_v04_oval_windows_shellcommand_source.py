#!/usr/bin/env python3
"""Six pinned original Windows shellcommand Tests -> native 0.4 -> OVAL.

Original PowerShell/cmd acquisition, explicit collection behavior defaults,
stdout/stderr/exit status, no-State existence, and two local Variable refs.
Original 5.12.3 XML/XSD/semantics, not scanner execution parity.
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

from prove_v04_oval_windows_cmdlet_source import (
    OD, OC, SPECS, tag, require, one,
)
from scap_ng_roundtrip_v003.compare_oval_semantics import compare
from test_generate_capability_schema_v04 import materialize, validate
from v04_canonical_source_ir import _schema_validators, validate_docs
from v04_flat_object_authoring import dump_hybrid
from validate_v04_oval_5123 import check

PIN = "e3538595c5083b9c34d937a81d319234df9bbfaa"
FILE = "windows/ind-def_shellcommand_windows_test.xml"
SHA = "64c460e9024d4053eb29695f0111e138363577f74ee3ac9c4b867c9689257e88"
OLD_DEF = "oval:navy.navwar.niwcatlantic.scc.windows:def:1"
OLD = "oval:navy.navwar.niwcatlantic.scc:"
NEW = "oval:scapng.04.shellwin:"
IND = OD + "#independent"
CAPABILITY = "independent.shellcommand"
ASSESSMENT_ID = "original-windows-shellcommand-six-tests-assessment"
NAMES = {
    1: "powershell-installed-os-test",
    2: "cmd-time-service-test",
    3: "powershell-directory-list-test",
    4: "variable-shell-command-test",
    5: "powershell-file-permissions-test",
    6: "cmd-standard-error-test",
}
VAR_NAMES = {4: "shell-source-variable", 5: "command-source-variable"}
OPS = {"equals": "equals", "greater than": "greater_than",
       "pattern match": "matches_regex"}
INVERSE_OPS = {v: k for k, v in OPS.items()}


def old_id(kind, number):
    return OLD + kind + ":" + str(number)


def _read_source_view(raw):
    require(sha256(raw).hexdigest() == SHA, "pinned original Windows shellcommand SHA")
    root = ET.fromstring(raw)
    require(root.tag == tag(OD, "oval_definitions"), "OVAL Definitions namespace")
    defs = {x.get("id"): x for x in one(root, OD, "definitions")}
    ts = {x.get("id"): x for x in one(root, OD, "tests")}
    os = {x.get("id"): x for x in one(root, OD, "objects")}
    ss = {x.get("id"): x for x in one(root, OD, "states")}
    vs = {x.get("id"): x for x in one(root, OD, "variables")}
    require(len(defs) == 1 and OLD_DEF in defs and
            len(ts) == len(os) == 6 and len(ss) == 3 and len(vs) == 2,
            "one source Definition, six Tests/Objects, three States, two locals")
    d = defs[OLD_DEF]
    criteria = one(d, OD, "criteria")
    require(d.get("class") == "compliance" and
            criteria.get("operator", "AND") == "AND" and len(criteria) == 6,
            "source six-Test AND criterion")
    refs = [x.get("test_ref") for x in criteria]
    require(refs == [old_id("tst", n) for n in NAMES],
            "pinned six original Test references in order")
    local_vars = {}
    for n, name in VAR_NAMES.items():
        v = vs[old_id("var", n)]
        lit = one(v, OD, "literal_component")
        require(v.tag == tag(OD, "local_variable") and
                v.get("datatype") == "string" and len(v) == 1 and
                isinstance(lit.text, str), "source original local literal Variable")
        local_vars[name] = {
            "kind": "local", "datatype": "string", "title": "Source local " + name,
            "expression": {"literal": [lit.text]},
        }
    tests = {}
    for n, name in NAMES.items():
        t = ts[old_id("tst", n)]
        o = os[old_id("obj", n)]
        require(t.tag == tag(IND, "shellcommand_test") and
                t.get("check_existence") == "at_least_one_exists" and
                t.get("check") == "all" and
                one(t, IND, "object").get("object_ref") == o.get("id") and
                o.tag == tag(IND, "shellcommand_object") and
                not o.findall(tag(OD, "set")),
                "original Windows shellcommand Test/Object pairing")
        object_fields = {"capability": CAPABILITY}
        for field in ("shell", "command", "pattern"):
            nodes = o.findall(tag(IND, field))
            require(len(nodes) <= 1 and (len(nodes) == 1 or field == "pattern"),
                    "source expected shell/command/optional stdout pattern")
            if not nodes:
                continue
            item = nodes[0]
            require(len(item) == 0, "scalar original shellcommand Object element")
            if item.get("var_ref"):
                ref = item.get("var_ref")
                require(ref in vs and (n, field) in ((4, "shell"), (4, "command")),
                        "pinned source shell/command Variable usage")
                number = int(ref.rsplit(":", 1)[-1])
                object_fields[field] = {"variable": VAR_NAMES[number]}
            else:
                require(not item.attrib and field != "shell" or
                        (not item.attrib and item.text in ("cmd", "powershell")),
                        "source literal shellcommand scalar/valid shell")
                object_fields[field] = item.text or ""
        object_fields["error_if_exit_status_not_0"] = False
        object_fields["error_if_stderr_exists"] = False
        test = {"test_title": t.get("comment"), "capability": CAPABILITY,
                "object": object_fields,
                "reported_elements": "all"}
        st_refs = t.findall(tag(IND, "state"))
        if n == 4:
            require(not st_refs, "source Test 4 is State-free")
            test["require"] = "at_least_one_exists"
        else:
            require(len(st_refs) == 1 and st_refs[0].get("state_ref") in ss,
                    "source shellcommand State reference")
            st = ss[st_refs[0].get("state_ref")]
            require(st.tag == tag(IND, "shellcommand_state"),
                    "shellcommand State capability")
            parts = []
            for field in st:
                label = field.tag.rsplit("}", 1)[-1]
                op = field.get("operation", "equals")
                typ = field.get("datatype", "string")
                require(label in ("stdout_line", "stderr_line", "exit_status") and
                        op in OPS and typ in ("int", "string") and
                        field.text is not None,
                        "original stdout/stderr/exit_status State entity")
                value = int(field.text) if typ == "int" else field.text
                parts.append({label: {OPS[op]: value,
                                      "require": "at_least_one_exists_and_all_match"}})
            require(parts, "source nonempty shellcommand State")
            test["states"] = [parts[0] if len(parts) == 1 else {"and": parts}]
            test["require"] = "at_least_one_exists_and_all_match"
        tests[name] = test
    return {"assessment": {
        "id": ASSESSMENT_ID, "version": int(d.get("version")),
        "assessment_title": one(one(d, OD, "metadata"), OD, "title").text,
        "mode": "automated", "class": "compliance", "purpose": "assessment",
        "specification": SPECS, "variables": local_vars,
        "tests": tests, "evaluate": {"and": [{"test": name} for name in NAMES.values()]},
    }}


def _export_source_view(doc):
    require(set(doc) == {"assessment"}, "native shellcommand Assessment")
    a = doc["assessment"]
    require(set(a) == {"id", "version", "assessment_title", "mode", "class",
                       "purpose", "specification", "variables", "tests", "evaluate"} and
            a["id"] == ASSESSMENT_ID and a["version"] == 1 and
            a["mode"] == "automated" and a["class"] == "compliance" and
            a["purpose"] == "assessment" and a["specification"] == SPECS and
            list(a["tests"]) == list(NAMES.values()) and
            a["evaluate"] == {"and": [{"test": name} for name in NAMES.values()]},
            "native six original shellcommand Tests/criteria")
    require(set(a["variables"]) == set(VAR_NAMES.values()),
            "two source local shellcommand Variables")
    for var in a["variables"].values():
        require(var.get("kind") == "local" and var.get("datatype") == "string" and
                set(var.get("expression", {})) == {"literal"} and
                isinstance(var["expression"]["literal"], list) and
                len(var["expression"]["literal"]) == 1 and
                isinstance(var["expression"]["literal"][0], str),
                "literal local Variable shell/command expression")

    ET.register_namespace("oval-def", OD)
    ET.register_namespace("oval", OC)
    ET.register_namespace("ind-def", IND)
    root = ET.Element(tag(OD, "oval_definitions"))
    generator = ET.SubElement(root, tag(OD, "generator"))
    ET.SubElement(generator, tag(OC, "product_name")).text = "SCAP-NG shellcommand proof"
    ET.SubElement(generator, tag(OC, "schema_version")).text = "5.12.3"
    ET.SubElement(generator, tag(OC, "timestamp")).text = "2026-10-22T00:00:00Z"
    defs = ET.SubElement(root, tag(OD, "definitions"))
    ts = ET.SubElement(root, tag(OD, "tests"))
    os = ET.SubElement(root, tag(OD, "objects"))
    ss = ET.SubElement(root, tag(OD, "states"))
    vs = ET.SubElement(root, tag(OD, "variables"))
    d = ET.SubElement(defs, tag(OD, "definition"), {
        "id": NEW + "def:1", "version": "1", "class": "compliance"})
    meta = ET.SubElement(d, tag(OD, "metadata"))
    ET.SubElement(meta, tag(OD, "title")).text = a["assessment_title"]
    ET.SubElement(meta, tag(OD, "description")).text = "Source shellcommand proof"
    criteria = ET.SubElement(d, tag(OD, "criteria"), {"operator": "AND"})
    for n, name in NAMES.items():
        t = a["tests"][name]
        require(t.get("capability") == CAPABILITY and
                t.get("reported_elements") == "all" and
                t.get("require") == ("at_least_one_exists" if n == 4 else
                                      "at_least_one_exists_and_all_match") and
                set(t["object"]) <= {"capability", "shell", "command", "pattern",
                                    "error_if_exit_status_not_0", "error_if_stderr_exists"} and
                t["object"].get("capability") == CAPABILITY and
                t["object"].get("error_if_exit_status_not_0") is False and
                t["object"].get("error_if_stderr_exists") is False,
                "typed flat native shellcommand and materialized behavior defaults")
        ET.SubElement(criteria, tag(OD, "criterion"), {
            "test_ref": NEW + "tst:" + str(n)})
        tt = ET.SubElement(ts, tag(IND, "shellcommand_test"), {
            "id": NEW + "tst:" + str(n), "version": "1",
            "comment": t["test_title"], "check": "all",
            "check_existence": "at_least_one_exists"})
        ET.SubElement(tt, tag(IND, "object"), {
            "object_ref": NEW + "obj:" + str(n)})
        if n != 4:
            ET.SubElement(tt, tag(IND, "state"), {
                "state_ref": NEW + "ste:" + str(n)})
        obj = ET.SubElement(os, tag(IND, "shellcommand_object"), {
            "id": NEW + "obj:" + str(n), "version": "1"})
        for field in ("shell", "command", "pattern"):
            if field not in t["object"]:
                require(field == "pattern", "missing shell or command")
                continue
            value = t["object"][field]
            attrib = {}
            if isinstance(value, dict):
                require(set(value) == {"variable"} and
                        value["variable"] in a["variables"] and
                        n == 4 and field in ("shell", "command"),
                        "source-approved local shellcommand Variable reference")
                idx = next(k for k, v in VAR_NAMES.items() if v == value["variable"])
                attrib["var_ref"] = NEW + "var:" + str(idx)
            else:
                require(isinstance(value, str), "literal shellcommand acquisition")
            entity = ET.SubElement(obj, tag(IND, field), attrib)
            if isinstance(value, str):
                entity.text = value
        if n != 4:
            state_expr = t["states"]
            require(isinstance(state_expr, list) and len(state_expr) == 1,
                    "one original shellcommand State per Test")
            condition = state_expr[0]
            parts = condition.get("and") if "and" in condition else [condition]
            require(parts and len(parts) <= 2, "State one/two source result fields")
            st = ET.SubElement(ss, tag(IND, "shellcommand_state"), {
                "id": NEW + "ste:" + str(n), "version": "1"})
            for part in parts:
                require(len(part) == 1, "one State entity per expression leaf")
                label, pred = next(iter(part.items()))
                op = set(pred) - {"require"}
                require(label in ("stdout_line", "stderr_line", "exit_status") and
                        len(op) == 1 and next(iter(op)) in INVERSE_OPS and
                        pred.get("require") == "at_least_one_exists_and_all_match",
                        "original shellcommand typed stdout/stderr/exit State")
                operator = next(iter(op))
                value = pred[operator]
                attrib = {"operation": INVERSE_OPS[operator]}
                if isinstance(value, int):
                    attrib["datatype"] = "int"
                else:
                    require(isinstance(value, str), "original shell result scalar")
                ET.SubElement(st, tag(IND, label), attrib).text = str(value)
        else:
            require("states" not in t, "source State-free Test 4")
    for n, name in VAR_NAMES.items():
        v = a["variables"][name]
        local = ET.SubElement(vs, tag(OD, "local_variable"), {
            "id": NEW + "var:" + str(n), "version": "1",
            "datatype": "string", "comment": v["title"]})
        ET.SubElement(local, tag(OD, "literal_component")).text = (
            v["expression"]["literal"][0])
    return ET.ElementTree(root)


def source_to_native(raw):
    from v04_source_proof_contract import current_document
    return current_document(_read_source_view(raw))


def native_to_oval(document):
    from v04_source_proof_contract import independent_export_view
    return _export_source_view(independent_export_view(document))


def prove(source, schema_root, xsd_root, output):
    source = Path(source)
    raw = source.read_bytes()
    doc = source_to_native(raw)
    validate_docs({"authoring/original-windows-shellcommand.json": doc},
                  _schema_validators(schema_root))
    schema = materialize(CAPABILITY)
    for test in doc["assessment"]["tests"].values():
        problems = validate(schema, "test", test)
        require(not problems, "generated independent.shellcommand schema " +
                str(problems[:2]))
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    (out / "original.xml").write_bytes(raw)
    (out / "native-040.assessment.json").write_text(json.dumps(doc, indent=2) + "\n")
    yml = dump_hybrid(doc)
    require(yaml.safe_load(yml) == doc, "native shellcommand YAML/JSON parity")
    (out / "native-040.assessment.yaml").write_text(yml)
    exported = out / "roundtrip-oval.xml"
    native_to_oval(doc).write(exported, encoding="utf-8", xml_declaration=True)
    xsd = check(xsd_root, exported, "independent")
    require(xsd["status"] == "PASS", "original 5.12.3 independent XML/XSD " +
            str(xsd.get("diagnostics", [])[:4]))
    (out / "roundtrip-xsd.json").write_text(json.dumps(xsd, indent=2) + "\n")
    sem = compare(source, exported, source_root=OLD_DEF,
                  regenerated_root=NEW + "def:1", root_only=True)
    require(sem["equal"], "all six source shellcommand Tests and Variable links")
    (out / "roundtrip-semantics.json").write_text(json.dumps(sem, indent=2) + "\n")
    wrong_source = raw.replace(b'<literal_component>netstat</literal_component>',
                               b'<literal_component>netstat -altered</literal_component>', 1)
    require(wrong_source != raw, "source Variable literal mutation")
    try:
        source_to_native(wrong_source)
    except ValueError:
        pass
    else:
        raise AssertionError("accepted mutated original shellcommand Variable")
    changed = deepcopy(doc)
    changed["assessment"]["tests"][NAMES[1]]["object"]["command"] += " -changed"
    wrong = out / "mutated-native-command.xml"
    native_to_oval(changed).write(wrong, encoding="utf-8", xml_declaration=True)
    altered = compare(source, wrong, source_root=OLD_DEF,
                      regenerated_root=NEW + "def:1", root_only=True)
    require(not altered["equal"], "mutated native PowerShell command detected")
    proof = {"source_file": FILE, "source_revision": PIN,
             "original_xml_sha256": SHA, "original_definition_id": OLD_DEF,
             "original_test_count": 6, "original_local_variable_count": 2,
             "native_assessment_schema": "PASS", "native_capability_schema": "PASS",
             "yaml_json_graph_equivalence": "PASS", "oval_5123_xsd": "PASS",
             "original_root_semantic_graph": "PASS",
             "state_free_test": "PASS", "stdout_stderr_exit": "PASS",
             "materialized_false_collector_defaults": "PASS",
             "source_local_variable_mutation": "REJECTED",
             "native_command_mutation": "DETECTED", "scanner_parity": False}
    from v04_source_proof_contract import compile_proofs
    proof["current_compilation"] = compile_proofs([doc], out / "compiled")
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
