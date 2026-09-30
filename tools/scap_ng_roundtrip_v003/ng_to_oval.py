#!/usr/bin/env python3
"""Prototype SCAP-NG stress-fixture -> OVAL 5.12.3 reverse generator.

This is deliberately narrow. Unsupported constructs are fatal.
It is a conformance research tool, not a general SCAP-NG compiler.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import xml.etree.ElementTree as ET

OVAL_DEF = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
OVAL_COMMON = "http://oval.mitre.org/XMLSchema/oval-common-5"
NS = {
    "independent": "http://oval.mitre.org/XMLSchema/oval-definitions-5#independent",
    "linux": "http://oval.mitre.org/XMLSchema/oval-definitions-5#linux",
    "unix": "http://oval.mitre.org/XMLSchema/oval-definitions-5#unix",
}
ET.register_namespace("", OVAL_DEF)
ET.register_namespace("oval", OVAL_COMMON)
ET.register_namespace("ind", NS["independent"])
ET.register_namespace("linux", NS["linux"])
ET.register_namespace("unix", NS["unix"])

def q(ns, local):
    return f"{{{ns}}}{local}"

def die(msg):
    raise ValueError(msg)

def materialize_substitutions(value, substitutions):
    if isinstance(value, str):
        for token, replacement in substitutions.items():
            if isinstance(replacement, dict):
                replacement = replacement.get("value")
            if replacement is None:
                continue
            value = value.replace(token, str(replacement))
        return value
    if isinstance(value, list):
        return [materialize_substitutions(v, substitutions) for v in value]
    if isinstance(value, dict):
        return {k: materialize_substitutions(v, substitutions) for k, v in value.items()}
    return value

class Ids:
    def __init__(self, fixture):
        self.prefix = "oval:scap-ng.roundtrip"
        self.maps = {"def": {}, "tst": {}, "obj": {}, "ste": {}, "var": {}}
        self.next = {"def": 1, "tst": 1, "obj": 1, "ste": 1, "var": 1}
        self.fixture = fixture

    def get(self, kind, logical):
        m = self.maps[kind]
        if logical not in m:
            n = self.next[kind]
            self.next[kind] += 1
            m[logical] = f"{self.prefix}:{kind}:{n}"
        return m[logical]

def split_type(t):
    if "." not in t:
        die(f"unsupported typed node: {t}")
    family, name = t.split(".", 1)
    if family not in NS:
        die(f"unsupported OVAL family: {family}")
    return family, name

def attrs_for_entity(spec, ids):
    attrs = {}
    if isinstance(spec, dict):
        if "datatype" in spec:
            attrs["datatype"] = str(spec["datatype"])
        if "operation" in spec:
            attrs["operation"] = str(spec["operation"])
        if "entity_check" in spec:
            attrs["entity_check"] = str(spec["entity_check"])
        if "variable" in spec:
            attrs["var_ref"] = ids.get("var", spec["variable"])
            if "var_check" in spec:
                attrs["var_check"] = str(spec["var_check"])
    return attrs

def add_entity(parent, ns, name, spec, ids):
    if isinstance(spec, dict):
        el = ET.SubElement(parent, q(ns, name), attrs_for_entity(spec, ids))
        if "variable" in spec:
            if "value" in spec:
                die(f"{name}: variable and value both supplied")
        elif "value" in spec:
            el.text = str(spec["value"])
        else:
            die(f"{name}: selector/predicate missing value or variable")
    else:
        el = ET.SubElement(parent, q(ns, name))
        el.text = str(spec)

def emit_component(parent, comp, ids):
    if "literal" in comp:
        el = ET.SubElement(parent, q(OVAL_DEF, "literal_component"))
        el.text = str(comp["literal"])
    elif "variable" in comp:
        ET.SubElement(parent, q(OVAL_DEF, "variable_component"),
                      {"var_ref": ids.get("var", comp["variable"])})
    elif "object_component" in comp:
        oc = comp["object_component"]
        attrs = {
            "object_ref": ids.get("obj", oc["collection"]),
            "item_field": oc["item_field"],
        }
        if oc.get("record_field"):
            attrs["record_field"] = oc["record_field"]
        ET.SubElement(parent, q(OVAL_DEF, "object_component"), attrs)
    else:
        emit_expression(parent, comp, ids)

def emit_expression(parent, expr, ids):
    if "object_component" in expr:
        emit_component(parent, expr, ids)
    elif "variable" in expr and len(expr) == 1:
        emit_component(parent, expr, ids)
    elif "concat" in expr:
        el = ET.SubElement(parent, q(OVAL_DEF, "concat"))
        for comp in expr["concat"]:
            emit_component(el, comp, ids)
    elif "arithmetic" in expr:
        a = expr["arithmetic"]
        el = ET.SubElement(parent, q(OVAL_DEF, "arithmetic"),
                           {"arithmetic_operation": a["operation"]})
        for comp in a["components"]:
            emit_component(el, comp, ids)
    elif "count" in expr:
        el = ET.SubElement(parent, q(OVAL_DEF, "count"))
        value=expr["count"]
        for comp in (value if isinstance(value,list) else [value]):
            emit_component(el, comp, ids)
    elif "unique" in expr:
        el = ET.SubElement(parent, q(OVAL_DEF, "unique"))
        value=expr["unique"]
        for comp in (value if isinstance(value,list) else [value]):
            emit_component(el, comp, ids)
    elif "split" in expr:
        value=expr["split"]
        el = ET.SubElement(parent, q(OVAL_DEF, "split"), {"delimiter": value["delimiter"]})
        emit_component(el, value["component"], ids)
    else:
        die(f"unsupported expression: {expr}")

def build(data):
    sem = copy.deepcopy(data["ng_semantics"])
    raw_subs = data.get("fixture_substitutions", {})
    substitutions = {}
    for key, val in raw_subs.items():
        substitutions[key] = val if isinstance(val, str) else val.get("value")
    sem = materialize_substitutions(sem, substitutions)
    ids = Ids(data["id"])

    root = ET.Element(q(OVAL_DEF, "oval_definitions"))
    gen = ET.SubElement(root, q(OVAL_DEF, "generator"))
    ET.SubElement(gen, q(OVAL_COMMON, "product_name")).text = "SCAP-NG round-trip research generator"
    ET.SubElement(gen, q(OVAL_COMMON, "schema_version")).text = "5.12.3"
    ET.SubElement(gen, q(OVAL_COMMON, "timestamp")).text = "2026-09-29T00:00:00Z"

    checks = sem.get("checks", [])
    collections = sem.get("collections", [])
    states = sem.get("states", [])
    variables = sem.get("variables", [])

    if checks:
        defs = ET.SubElement(root, q(OVAL_DEF, "definitions"))
        d = ET.SubElement(defs, q(OVAL_DEF, "definition"), {
            "id": ids.get("def", data["id"]),
            "version": "1",
            "class": "compliance",
        })
        md = ET.SubElement(d, q(OVAL_DEF, "metadata"))
        ET.SubElement(md, q(OVAL_DEF, "title")).text = f"Round-trip fixture {data['id']}"
        ET.SubElement(md, q(OVAL_DEF, "description")).text = "Generated from SCAP-NG semantic stress fixture."
        def emit_criteria(parent, node):
            attrs={"operator": node.get("operator","AND")}
            if node.get("negate") is not None:
                attrs["negate"]=str(bool(node["negate"])).lower()
            if node.get("applicability_check") is not None:
                attrs["applicability_check"]=str(bool(node["applicability_check"])).lower()
            ce=ET.SubElement(parent, q(OVAL_DEF, "criteria"), attrs)
            children=node.get("children")
            if children is None:
                children=[{"check":cid} for cid in node.get("checks",[c["id"] for c in checks])]
            for child in children:
                if "check" in child:
                    cid=child["check"]
                    ca={"test_ref":ids.get("tst",cid),"comment":cid}
                    if child.get("negate") is not None:
                        ca["negate"]=str(bool(child["negate"])).lower()
                    if child.get("applicability_check") is not None:
                        ca["applicability_check"]=str(bool(child["applicability_check"])).lower()
                    ET.SubElement(ce,q(OVAL_DEF,"criterion"),ca)
                elif "operator" in child or "children" in child or "checks" in child:
                    emit_criteria(ce,child)
                else:
                    die(f"unsupported root criteria node: {child}")
            return ce

        emit_criteria(d,sem.get("root",{}))

        tests = ET.SubElement(root, q(OVAL_DEF, "tests"))
        for chk in checks:
            family, name = split_type(chk["type"])
            ns = NS[family]
            attrs = {
                "id": ids.get("tst", chk["id"]),
                "version": "1",
                "check_existence": chk["check_existence"],
                "check": chk["check"],
                "comment": chk["id"],
            }
            if "state_operator" in chk:
                attrs["state_operator"] = str(chk["state_operator"])
            t = ET.SubElement(tests, q(ns, name + "_test"), attrs)
            ET.SubElement(t, q(ns, "object"), {
                "object_ref": ids.get("obj", chk["collection"])
            })
            for sid in chk.get("states", []):
                ET.SubElement(t, q(ns, "state"), {
                    "state_ref": ids.get("ste", sid)
                })

    if collections:
        objects = ET.SubElement(root, q(OVAL_DEF, "objects"))
        for col in collections:
            family, name = split_type(col["type"])
            ns = NS[family]
            o = ET.SubElement(objects, q(ns, name + "_object"), {
                "id": ids.get("obj", col["id"]),
                "version": "1",
                "comment": col["id"],
            })
            if "set" in col:
                s = col["set"]
                se = ET.SubElement(o, q(OVAL_DEF, "set"), {"set_operator": s["operator"]})
                for ref in s["collections"]:
                    e = ET.SubElement(se, q(OVAL_DEF, "object_reference"))
                    e.text = ids.get("obj", ref)
                for f in s.get("filters", []):
                    fe = ET.SubElement(se, q(OVAL_DEF, "filter"), {"action": f.get("action", "exclude")})
                    fe.text = ids.get("ste", f["state"])
            else:
                if "behaviors" in col:
                    ET.SubElement(o, q(ns, "behaviors"),
                                  {k: str(v).lower() if isinstance(v, bool) else str(v)
                                   for k, v in col["behaviors"].items()})
                for field, spec in col.get("selectors", {}).items():
                    add_entity(o, ns, field, spec, ids)
                for f in col.get("filters", []):
                    fe = ET.SubElement(o, q(OVAL_DEF, "filter"), {"action": f.get("action", "exclude")})
                    fe.text = ids.get("ste", f["state"])

    if states:
        sts = ET.SubElement(root, q(OVAL_DEF, "states"))
        for state in states:
            family, name = split_type(state["type"])
            ns = NS[family]
            state_attrs = {
                "id": ids.get("ste", state["id"]),
                "version": "1",
                "comment": state["id"],
            }
            if "operator" in state:
                state_attrs["operator"] = str(state["operator"])
            se = ET.SubElement(sts, q(ns, name + "_state"), state_attrs)
            for field, spec in state.get("predicates", {}).items():
                add_entity(se, ns, field, spec, ids)

    if variables:
        vs = ET.SubElement(root, q(OVAL_DEF, "variables"))
        for var in variables:
            attrs = {
                "id": ids.get("var", var["id"]),
                "version": "1",
                "datatype": var["datatype"],
                "comment": var["id"],
            }
            kind = var["kind"]
            if kind == "constant":
                ve = ET.SubElement(vs, q(OVAL_DEF, "constant_variable"), attrs)
                for value in var["values"]:
                    ET.SubElement(ve, q(OVAL_DEF, "value")).text = str(value)
            elif kind == "local":
                ve = ET.SubElement(vs, q(OVAL_DEF, "local_variable"), attrs)
                emit_expression(ve, var["expression"], ids)
            else:
                die(f"unsupported variable kind: {kind}")

    return ET.ElementTree(root)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fixture", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    data = json.loads(args.fixture.read_text(encoding="utf-8"))
    tree = build(data)
    ET.indent(tree, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    main()
