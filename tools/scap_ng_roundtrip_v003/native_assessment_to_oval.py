#!/usr/bin/env python3
"""Regenerate OVAL 5.12.3 from one native SCAP-NG v003 assessment.

This is a semantic round-trip research emitter. It deliberately generates new
OVAL IDs; comparison must be ID-independent. Unsupported native shapes are fatal.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
OC = "http://oval.mitre.org/XMLSchema/oval-common-5"
XSI = "http://www.w3.org/2001/XMLSchema-instance"

ET.register_namespace("", OD)
ET.register_namespace("oval", OC)
ET.register_namespace("xsi", XSI)

def q(ns, name):
    return f"{{{ns}}}{name}"

def family_ns(family: str) -> str:
    return OD + "#" + family

def split_capability(capability: str):
    if not capability or "." not in capability:
        raise ValueError(f"invalid capability {capability!r}")
    return capability.split(".", 1)

def scalar(value):
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)

def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

class Ids:
    def __init__(self):
        self.maps = {k: {} for k in ("def", "tst", "obj", "ste", "var")}
        self.next = {k: 1 for k in self.maps}

    def get(self, kind, key):
        token = canon(key) if not isinstance(key, str) else key
        if token not in self.maps[kind]:
            n = self.next[kind]
            self.next[kind] += 1
            self.maps[kind][token] = f"oval:scap-ng.native.roundtrip:{kind}:{n}"
        return self.maps[kind][token]

class Builder:
    def __init__(self, document):
        self.doc = document
        self.assessment = document.get("assessment", document)
        self.ids = Ids()
        self.root = ET.Element(q(OD, "oval_definitions"))
        gen = ET.SubElement(self.root, q(OD, "generator"))
        ET.SubElement(gen, q(OC, "product_name")).text = "SCAP-NG native round-trip generator"
        ET.SubElement(gen, q(OC, "schema_version")).text = "5.12.3"
        ET.SubElement(gen, q(OC, "timestamp")).text = "2026-09-29T00:00:00Z"
        self.defs = ET.SubElement(self.root, q(OD, "definitions"))
        self.tests = ET.SubElement(self.root, q(OD, "tests"))
        self.objects = ET.SubElement(self.root, q(OD, "objects"))
        self.states = ET.SubElement(self.root, q(OD, "states"))
        self.variables = ET.SubElement(self.root, q(OD, "variables"))
        self.emitted_objects = set()
        self.emitted_states = set()
        self.emitted_variables = set()
        self.check_to_test = {}

    def emit_record_fields(self, parent, fields):
        for item in fields:
            attrs = {"name": scalar(item["name"])}
            for source, target in (
                ("operation", "operation"),
                ("datatype", "datatype"),
                ("variable_check", "var_check"),
                ("entity_check", "entity_check"),
                ("mask", "mask"),
            ):
                if item.get(source) is not None:
                    attrs[target] = scalar(item[source])
            field = ET.SubElement(parent, q(OD, "field"), attrs)
            value = item.get("value")
            if isinstance(value, dict) and set(value) == {"variable"}:
                field.set("var_ref", self.emit_variable(value["variable"]))
            elif value is not None:
                field.text = scalar(value)

    def emit_entity_payload(self, el, value):
        if isinstance(value, dict) and set(value) == {"record"}:
            self.emit_record_fields(el, value["record"])
        elif isinstance(value, dict) and set(value) == {"variable"}:
            el.set("var_ref", self.emit_variable(value["variable"]))
        elif value is not None:
            el.text = scalar(value)

    def emit_value_entity(self, parent, ns, field, spec):
        attrs = {}
        value = spec
        nil = False
        if isinstance(spec, dict) and "value" in spec:
            value = spec.get("value")
            if spec.get("operation") is not None:
                attrs["operation"] = scalar(spec["operation"])
            if spec.get("variable_check") is not None:
                attrs["var_check"] = scalar(spec["variable_check"])
            if spec.get("entity_check") is not None:
                attrs["entity_check"] = scalar(spec["entity_check"])
            if spec.get("datatype") is not None:
                attrs["datatype"] = scalar(spec["datatype"])
            if spec.get("mask") is not None:
                attrs["mask"] = scalar(spec["mask"])
            if spec.get("nil") is not None:
                nil = bool(spec["nil"])
                attrs[q(XSI, "nil")] = scalar(nil)
        el = ET.SubElement(parent, q(ns, field), attrs)
        if nil:
            return el
        if isinstance(value, dict) and set(value) == {"variable"}:
            variable_id = self.emit_variable(value["variable"])
            if field == "var_ref":
                el.text = variable_id
            else:
                el.set("var_ref", variable_id)
        else:
            self.emit_entity_payload(el, value)
        return el

    def emit_state(self, capability, expr, title=None):
        family, name = split_capability(capability)
        key = {"capability": capability, "expr": expr, "title": title}
        sid = self.ids.get("ste", key)
        if sid in self.emitted_states:
            return sid
        self.emitted_states.add(sid)
        ns = family_ns(family)

        if isinstance(expr, dict) and set(expr) == {"all"}:
            operator = "AND"
            predicates = expr["all"]
        elif isinstance(expr, dict) and set(expr) == {"any"}:
            operator = "OR"
            predicates = expr["any"]
        else:
            operator = "AND"
            predicates = [expr]

        if any(not (isinstance(p, dict) and "field" in p) for p in predicates):
            raise ValueError(f"nested state boolean requires test-level grouping: {expr!r}")

        attrs = {"id": sid, "version": "1", "operator": operator}
        if title:
            attrs["comment"] = str(title)
        state = ET.SubElement(self.states, q(ns, name + "_state"), attrs)
        for pred in predicates:
            attrs = {"operation": str(pred.get("operation") or "equals")}
            if pred.get("entity_check") is not None:
                attrs["entity_check"] = scalar(pred["entity_check"])
            if pred.get("entity_existence") is not None:
                attrs["check_existence"] = scalar(pred["entity_existence"])
            if pred.get("variable_check") is not None:
                attrs["var_check"] = scalar(pred["variable_check"])
            if pred.get("datatype") is not None:
                attrs["datatype"] = scalar(pred["datatype"])
            if pred.get("mask") is not None:
                attrs["mask"] = scalar(pred["mask"])
            nil = bool(pred.get("nil", False))
            if pred.get("nil") is not None:
                attrs[q(XSI, "nil")] = scalar(nil)
            el = ET.SubElement(state, q(ns, pred["field"]), attrs)
            if not nil:
                self.emit_entity_payload(el, pred.get("value"))
        return sid

    def split_test_states(self, expr):
        if expr is None:
            return "AND", []
        if isinstance(expr, dict) and set(expr) in ({"all"}, {"any"}):
            key = next(iter(expr))
            terms = expr[key]
            if any(isinstance(x, dict) and ("all" in x or "any" in x) for x in terms):
                return ("AND" if key == "all" else "OR"), terms
        return "AND", [expr]

    def emit_filter(self, parent, capability, item):
        state_capability = item.get("capability") or capability
        sid = self.emit_state(state_capability, item.get("match"), item.get("state_title"))
        f = ET.SubElement(parent, q(OD, "filter"), {"action": item.get("action") or "exclude"})
        f.text = sid

    def emit_set(self, parent, set_expr, capability):
        attrs = {"set_operator": str(set_expr.get("operator") or "union").upper()}
        node = ET.SubElement(parent, q(OD, "set"), attrs)
        for member in set_expr.get("members", []):
            if "collect" in member:
                ref = ET.SubElement(node, q(OD, "object_reference"))
                ref.text = self.emit_object(member["collect"])
            elif "set" in member:
                self.emit_set(node, member["set"], capability)
            else:
                raise ValueError(f"unsupported set member {member!r}")
        for item in set_expr.get("filters", []):
            self.emit_filter(node, capability, item)

    def emit_object(self, collection):
        oid = self.ids.get("obj", collection)
        if oid in self.emitted_objects:
            return oid
        self.emitted_objects.add(oid)
        capability = collection.get("capability")
        family, name = split_capability(capability)
        ns = family_ns(family)
        attrs = {"id": oid, "version": "1"}
        if collection.get("object_title"):
            attrs["comment"] = str(collection["object_title"])
        obj = ET.SubElement(self.objects, q(ns, name + "_object"), attrs)

        if collection.get("behaviors"):
            ET.SubElement(obj, q(ns, "behaviors"), {
                str(k): scalar(v) for k, v in collection["behaviors"].items()
            })

        if collection.get("set") is not None:
            self.emit_set(obj, collection["set"], capability)
        else:
            for field, spec in collection.get("select", {}).items():
                self.emit_value_entity(obj, ns, field, spec)
            for item in collection.get("filters", []):
                self.emit_filter(obj, capability, item)
        return oid

    def emit_component(self, parent, expr):
        if not isinstance(expr, dict) or len(expr) != 1:
            raise ValueError(f"invalid expression component {expr!r}")
        name, value = next(iter(expr.items()))

        if name == "literal":
            attrs = {}
            literal = value
            if isinstance(value, dict):
                literal = value.get("value")
                if value.get("datatype") is not None:
                    attrs["datatype"] = scalar(value["datatype"])
            el = ET.SubElement(parent, q(OD, "literal_component"), attrs)
            if literal is not None:
                el.text = scalar(literal)
            return
        if name == "variable":
            ET.SubElement(parent, q(OD, "variable_component"), {
                "var_ref": self.emit_variable(value)
            })
            return
        if name == "object_values":
            attrs = {
                "object_ref": self.emit_object(value["collect"]),
                "item_field": value["field"],
            }
            if value.get("record_field"):
                attrs["record_field"] = value["record_field"]
            ET.SubElement(parent, q(OD, "object_component"), attrs)
            return
        if name in ("concat", "count", "unique"):
            el = ET.SubElement(parent, q(OD, name))
            values = value if isinstance(value, list) else [value]
            for item in values:
                self.emit_component(el, item)
            return
        if name == "arithmetic":
            el = ET.SubElement(parent, q(OD, "arithmetic"), {
                "arithmetic_operation": str(value["operation"])
            })
            for item in value.get("operands", []):
                self.emit_component(el, item)
            return
        if name in ("begin", "end"):
            el = ET.SubElement(parent, q(OD, name), {"character": scalar(value["character"])})
            self.emit_component(el, value["value"])
            return
        if name == "split":
            el = ET.SubElement(parent, q(OD, "split"), {"delimiter": scalar(value["delimiter"])})
            self.emit_component(el, value["value"])
            return
        if name == "substring":
            el = ET.SubElement(parent, q(OD, "substring"), {
                "substring_start": scalar(value["start"]),
                "substring_length": scalar(value["length"]),
            })
            self.emit_component(el, value["value"])
            return
        if name == "regex_capture":
            attrs = {}
            if value.get("pattern") is not None:
                attrs["pattern"] = scalar(value["pattern"])
            el = ET.SubElement(parent, q(OD, "regex_capture"), attrs)
            self.emit_component(el, value["value"])
            return
        if name == "escape_regex":
            el = ET.SubElement(parent, q(OD, "escape_regex"))
            self.emit_component(el, value)
            return
        if name == "glob_to_regex":
            el = ET.SubElement(parent, q(OD, "glob_to_regex"), {
                "glob_noescape": scalar(bool(value.get("noescape", False)))
            })
            self.emit_component(el, value["value"])
            return
        if name == "time_difference":
            attrs = {}
            if value.get("format_1") is not None:
                attrs["format_1"] = scalar(value["format_1"])
            if value.get("format_2") is not None:
                attrs["format_2"] = scalar(value["format_2"])
            el = ET.SubElement(parent, q(OD, "time_difference"), attrs)
            for item in value.get("values", []):
                self.emit_component(el, item)
            return
        if name == "merge":
            attrs = {
                "delimiter": scalar(value.get("delimiter", "")),
                "sort": scalar(value.get("sort", "document")),
                "order": scalar(value.get("order", "ascending")),
            }
            el = ET.SubElement(parent, q(OD, "merge"), attrs)
            values = value.get("values", [])
            values = values if isinstance(values, list) else [values]
            for item in values:
                self.emit_component(el, item)
            return
        raise ValueError(f"unsupported native expression {name}")

    def emit_variable(self, native_id):
        vid = self.ids.get("var", native_id)
        if vid in self.emitted_variables:
            return vid
        entry = self.assessment.get("variables", {}).get(native_id)
        if entry is None:
            raise ValueError(f"native variable not found: {native_id}")
        self.emitted_variables.add(vid)
        attrs = {
            "id": vid,
            "version": "1",
            "datatype": entry.get("datatype") or "string",
        }
        if entry.get("title"):
            attrs["comment"] = str(entry["title"])
        kind = entry.get("kind")
        if kind == "external":
            ve = ET.SubElement(self.variables, q(OD, "external_variable"), attrs)
            validation = (entry.get("input") or {}).get("validation") or {}
            for alternative in validation.get("alternatives", []):
                if "literal" in alternative:
                    pv = ET.SubElement(
                        ve,
                        q(OD, "possible_value"),
                        {"hint": str(alternative.get("hint") or "")},
                    )
                    if alternative.get("literal") is not None:
                        pv.text = scalar(alternative.get("literal"))
                elif "restriction_group" in alternative:
                    group = alternative["restriction_group"]
                    pr = ET.SubElement(
                        ve,
                        q(OD, "possible_restriction"),
                        {
                            "operator": str(group.get("operator") or "AND").upper(),
                            "hint": str(group.get("hint") or ""),
                        },
                    )
                    for condition in group.get("conditions", []):
                        restriction = ET.SubElement(
                            pr,
                            q(OD, "restriction"),
                            {"operation": str(condition.get("operation"))},
                        )
                        if condition.get("value") is not None:
                            restriction.text = scalar(condition.get("value"))
                else:
                    raise ValueError(
                        f"unsupported external-variable validation alternative: {alternative!r}"
                    )
        elif kind == "constant":
            ve = ET.SubElement(self.variables, q(OD, "constant_variable"), attrs)
            expression = entry.get("expression", {})
            if set(expression) != {"literal"}:
                raise ValueError(f"constant variable lacks literal expression: {native_id}")
            values = expression["literal"]
            if isinstance(values, dict):
                values = values.get("value")
            values = values if isinstance(values, list) else [values]
            for item in values:
                child = ET.SubElement(ve, q(OD, "value"))
                if item is not None:
                    child.text = scalar(item)
        elif kind == "local":
            ve = ET.SubElement(self.variables, q(OD, "local_variable"), attrs)
            self.emit_component(ve, entry["expression"])
        else:
            raise ValueError(f"unsupported native variable kind {kind!r}: {native_id}")
        return vid

    def emit_check(self, check_id):
        if check_id in self.check_to_test:
            return self.check_to_test[check_id]
        check = self.assessment["checks"][check_id]

        if check.get("result") == "unknown":
            capability = check.get("capability") or "independent.unknown"
            family, name = split_capability(capability)
            tid = self.ids.get("tst", check_id)
            ET.SubElement(self.tests, q(family_ns(family), name + "_test"), {
                "id": tid,
                "version": "1",
                "check_existence": "at_least_one_exists",
                "check": "at least one",
                "comment": check.get("test_title") or check_id,
            })
            self.check_to_test[check_id] = tid
            return tid

        collection = check["collect"]
        capability = check.get("capability") or collection["capability"]
        family, name = split_capability(capability)
        ns = family_ns(family)
        tid = self.ids.get("tst", check_id)
        assertion = check.get("assert", {})
        attrs = {
            "id": tid,
            "version": "1",
            "check_existence": assertion.get("existence") or "at_least_one_exists",
            "check": assertion.get("check") or "all",
            "comment": check.get("test_title") or check_id,
        }

        explicit_states = assertion.get("states")
        if explicit_states:
            state_operator = (assertion.get("state_operator") or "AND").upper()
            attrs["state_operator"] = state_operator
            state_items = [
                (
                    item.get("state"),
                    item.get("state_title"),
                    item.get("capability") or capability,
                )
                for item in explicit_states
            ]
        else:
            state_operator, state_exprs = self.split_test_states(assertion.get("state"))
            if len(state_exprs) > 1:
                attrs["state_operator"] = state_operator
            state_items = [
                (
                    expr,
                    assertion.get("state_title"),
                    assertion.get("state_capability") or capability,
                )
                for expr in state_exprs
            ]

        test = ET.SubElement(self.tests, q(ns, name + "_test"), attrs)
        ET.SubElement(test, q(ns, "object"), {"object_ref": self.emit_object(collection)})
        for expr, title, state_capability in state_items:
            sid = self.emit_state(state_capability, expr, title)
            ET.SubElement(test, q(ns, "state"), {"state_ref": sid})
        self.check_to_test[check_id] = tid
        return tid

    def unwrap_flags(self, expr):
        negate = False
        applicability = False
        while isinstance(expr, dict) and len(expr) == 1:
            if "not" in expr:
                negate = not negate
                expr = expr["not"]
                continue
            if "applicability_check" in expr:
                applicability = True
                expr = expr["applicability_check"]
                continue
            break
        return expr, negate, applicability

    def emit_logic_node(self, parent, expr, force_criteria=False):
        expr, negate, applicability = self.unwrap_flags(expr)
        if isinstance(expr, dict) and set(expr) == {"check"} and not force_criteria:
            attrs = {
                "test_ref": self.emit_check(expr["check"]),
                "comment": str(expr["check"]),
            }
            if negate:
                attrs["negate"] = "true"
            if applicability:
                attrs["applicability_check"] = "true"
            ET.SubElement(parent, q(OD, "criterion"), attrs)
            return

        op_map = {"all": "AND", "any": "OR", "one": "ONE", "xor": "XOR"}
        if isinstance(expr, dict) and len(expr) == 1 and next(iter(expr)) in op_map:
            key = next(iter(expr))
            terms = expr[key]
            attrs = {"operator": op_map[key]}
        else:
            terms = [expr]
            attrs = {"operator": "AND"}
        if negate:
            attrs["negate"] = "true"
        if applicability:
            attrs["applicability_check"] = "true"
        node = ET.SubElement(parent, q(OD, "criteria"), attrs)
        for term in terms:
            self.emit_logic_node(node, term)

    def build(self):
        a = self.assessment
        did = self.ids.get("def", a.get("id") or "assessment")
        attrs = {
            "id": did,
            "version": scalar(a.get("version") if a.get("version") is not None else 1),
            "class": a.get("class") or "miscellaneous",
        }
        if a.get("deprecated"):
            attrs["deprecated"] = "true"
        d = ET.SubElement(self.defs, q(OD, "definition"), attrs)
        md = ET.SubElement(d, q(OD, "metadata"))
        ET.SubElement(md, q(OD, "title")).text = a.get("assessment_title") or a.get("id") or "SCAP-NG assessment"
        ET.SubElement(md, q(OD, "description")).text = "Regenerated from native SCAP-NG assessment semantics."
        self.emit_logic_node(d, a["evaluate"], force_criteria=True)

        # Remove empty optional sections after all lazy emission is complete.
        for section in (self.tests, self.objects, self.states, self.variables):
            if len(section) == 0:
                self.root.remove(section)
        return ET.ElementTree(self.root), did

def build(document):
    builder = Builder(document)
    return builder.build()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("assessment", type=Path)
    ap.add_argument("-o", "--output", type=Path, required=True)
    ap.add_argument("--root-id-output", type=Path)
    args = ap.parse_args()
    document = json.loads(args.assessment.read_text(encoding="utf-8"))
    tree, root_id = build(document)
    ET.indent(tree, space="  ")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tree.write(args.output, encoding="utf-8", xml_declaration=True)
    if args.root_id_output:
        args.root_id_output.write_text(root_id + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
