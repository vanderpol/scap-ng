#!/usr/bin/env python3
"""Parse standalone OVAL Definitions into a faithful semantic intermediate representation.

The IR models OVAL core evaluation logic explicitly and preserves all
platform-specific XML nodes losslessly. It does not guess policy intent or
pretend that an unimplemented native SCAP-NG capability mapping already exists.

Supported structural semantics include:
  * definition metadata and criteria AND/OR/negation;
  * criterion test references and extend_definition references;
  * test check/check_existence/state_operator semantics;
  * fixed-point object/state/variable dependency graph, including variable_component,
    object_component, var_ref, set object_reference, and filter-induced dependencies;
  * object set/filter structure;
  * entity comparison attributes (operation, datatype, var_ref, var_check,
    entity_check, mask);
  * constant/external/local variables and component/function trees;
  * generic preservation of all remaining elements/attributes/text;
  * complete OVAL ID reference graph and unresolved-reference accounting.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re as pyre
from pathlib import Path
import re
import sys

from lxml import etree

OVAL_ID_RE = re.compile(r"^oval:[A-Za-z0-9_.-]+:(?:def|tst|obj|ste|var):[A-Za-z0-9_.-]+$")
SECTION_KIND = {
    "definitions": "definition",
    "tests": "test",
    "objects": "object",
    "states": "state",
    "variables": "variable",
}
CORE_ATTRS = {
    "operator", "negate", "check", "check_existence", "state_operator",
    "operation", "datatype", "var_ref", "var_check", "entity_check", "mask",
    "recurse_direction", "max_depth", "behaviors",
}

OVAL_COMPONENT_OPERATIONS = {
    "object_component",
    "variable_component",
    "literal_component",
    "arithmetic",
    "begin",
    "concat",
    "count",
    "end",
    "escape_regex",
    "glob_to_regex",
    "merge",
    "regex_capture",
    "split",
    "substring",
    "time_difference",
    "unique",
}

STATIC_EVALUATOR_OPERATIONS = {
    "literal_component",
    "variable_component",
    "arithmetic",
    "begin",
    "concat",
    "count",
    "end",
    "escape_regex",
    "merge",
    "split",
    "substring",
    "unique",
}

REGEX_META = set("^$\\.[](){}*+?|")


def local(tag: str) -> str:
    return etree.QName(tag).localname


def ns(tag: str) -> str:
    return etree.QName(tag).namespace or ""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def text_value(e):
    if e.text is None:
        return None
    value = e.text.strip()
    return value if value else None


def generic_node(e):
    out = {
        "name": local(e.tag),
        "namespace": ns(e.tag),
    }
    if e.attrib:
        out["attributes"] = {
            etree.QName(k).localname: v for k, v in sorted(e.attrib.items())
        }
    value = text_value(e)
    if value is not None:
        out["text"] = value
    children = [generic_node(c) for c in e if isinstance(c.tag, str)]
    if children:
        out["children"] = children
    return out


def criteria_node(e):
    name = local(e.tag)
    if name == "criteria":
        return {
            "kind": "boolean",
            "operator": e.get("operator", "AND"),
            "negate": e.get("negate", "false") == "true",
            "comment": e.get("comment"),
            "children": [
                criteria_node(c)
                for c in e
                if local(c.tag) in {"criteria", "criterion", "extend_definition"}
            ],
        }
    if name == "criterion":
        return {
            "kind": "test_ref",
            "test_ref": e.get("test_ref"),
            "negate": e.get("negate", "false") == "true",
            "comment": e.get("comment"),
        }
    if name == "extend_definition":
        return {
            "kind": "definition_ref",
            "definition_ref": e.get("definition_ref"),
            "negate": e.get("negate", "false") == "true",
            "comment": e.get("comment"),
        }
    return {"kind": "unknown_criteria_node", "xml": generic_node(e)}


def dependency_kind(node, source: str) -> str:
    name = local(node.tag)
    if source == "definition_ref":
        return "extend_definition"
    if source == "test_ref":
        return "criterion_test"
    if source == "object_ref":
        return "object_component" if name == "object_component" else "test_object"
    if source == "state_ref":
        return "test_state" if name == "state" else "state_reference"
    if source == "var_ref":
        return "variable_reference"
    if name == "object_reference" and source == "text":
        return "set_object_reference"
    if name == "filter" and source == "text":
        return "set_filter_state"
    if name == "var_ref" and source == "text":
        return "variable_reference"
    return f"{name}:{source}"


def collect_refs(source_id: str, e, known_ids: set[str]):
    refs = set()
    unresolved = set()
    edges = []
    for n in e.iter():
        for attr_name, v in n.attrib.items():
            value = v.strip()
            attr = local(attr_name)
            if attr == "id":
                continue
            if value in known_ids:
                refs.add(value)
                edges.append({
                    "from": source_id,
                    "to": value,
                    "kind": dependency_kind(n, attr),
                    "element": local(n.tag),
                    "attribute": attr,
                })
            elif OVAL_ID_RE.match(value):
                unresolved.add(value)
                edges.append({
                    "from": source_id,
                    "to": value,
                    "kind": dependency_kind(n, attr),
                    "element": local(n.tag),
                    "attribute": attr,
                    "resolved": False,
                })
        if n.text:
            value = n.text.strip()
            if value in known_ids:
                refs.add(value)
                edges.append({
                    "from": source_id,
                    "to": value,
                    "kind": dependency_kind(n, "text"),
                    "element": local(n.tag),
                    "attribute": None,
                })
            elif OVAL_ID_RE.match(value):
                unresolved.add(value)
                edges.append({
                    "from": source_id,
                    "to": value,
                    "kind": dependency_kind(n, "text"),
                    "element": local(n.tag),
                    "attribute": None,
                    "resolved": False,
                })
    dedup = {}
    for edge in edges:
        key = (edge["from"], edge["to"], edge["kind"], edge["element"], edge["attribute"])
        dedup[key] = edge
    return refs, unresolved, sorted(
        dedup.values(),
        key=lambda x: (x["from"], x["to"], x["kind"], x["element"], x.get("attribute") or "")
    )


def set_node(e):
    out = {
        "kind": "set",
        "operator": e.get("set_operator", e.get("operator", "UNION")),
        "children": [],
    }
    for c in e:
        n = local(c.tag)
        if n == "set":
            out["children"].append(set_node(c))
        elif n == "object_reference":
            out["children"].append({
                "kind": "object_ref",
                "object_ref": text_value(c),
            })
        elif n == "filter":
            out["children"].append({
                "kind": "filter",
                "state_ref": text_value(c),
                "action": c.get("action", "include"),
            })
        else:
            out["children"].append({
                "kind": "preserved",
                "xml": generic_node(c),
            })
    return out


def semantic_child(e):
    n = local(e.tag)
    if n == "set":
        return set_node(e)

    out = {
        "kind": "element",
        "name": n,
        "namespace": ns(e.tag),
    }
    attrs = {etree.QName(k).localname: v for k, v in e.attrib.items()}
    if attrs:
        out["attributes"] = attrs
    val = text_value(e)
    if val is not None:
        out["value"] = val

    children = [semantic_child(c) for c in e if isinstance(c.tag, str)]
    if children:
        out["children"] = children
    return out


def parse_definition(e):
    metadata = None
    criteria = None
    for c in e:
        n = local(c.tag)
        if n == "metadata":
            metadata = generic_node(c)
        elif n == "criteria":
            criteria = criteria_node(c)
    return {
        "id": e.get("id"),
        "version": e.get("version"),
        "class": e.get("class"),
        "deprecated": e.get("deprecated"),
        "metadata": metadata,
        "criteria": criteria,
    }


def parse_test(e):
    objects = []
    states = []
    other = []
    for c in e:
        n = local(c.tag)
        if n == "object":
            objects.append({
                "object_ref": c.get("object_ref"),
                "attributes": {etree.QName(k).localname: v for k, v in c.attrib.items()},
            })
        elif n == "state":
            states.append({
                "state_ref": c.get("state_ref"),
                "attributes": {etree.QName(k).localname: v for k, v in c.attrib.items()},
            })
        else:
            other.append(semantic_child(c))
    return {
        "id": e.get("id"),
        "type": local(e.tag),
        "namespace": ns(e.tag),
        "version": e.get("version"),
        "comment": e.get("comment"),
        "check": e.get("check", "all"),
        "check_existence": e.get("check_existence", "at_least_one_exists"),
        "state_operator": e.get("state_operator", "AND"),
        "objects": objects,
        "states": states,
        "other": other,
    }


def parse_object(e):
    children = [semantic_child(c) for c in e if isinstance(c.tag, str)]
    return {
        "id": e.get("id"),
        "type": local(e.tag),
        "namespace": ns(e.tag),
        "version": e.get("version"),
        "comment": e.get("comment"),
        "children": children,
    }


def parse_state(e):
    return {
        "id": e.get("id"),
        "type": local(e.tag),
        "namespace": ns(e.tag),
        "version": e.get("version"),
        "comment": e.get("comment"),
        "operator": e.get("operator", "AND"),
        "entities": [semantic_child(c) for c in e if isinstance(c.tag, str)],
    }



def variable_expression(node):
    """Return an explicit semantic AST for every OVAL ComponentGroup operation."""
    name = local(node.tag)
    attrs = {etree.QName(k).localname: v for k, v in node.attrib.items()}

    if name == "literal_component":
        return {
            "op": "literal_component",
            "datatype": attrs.get("datatype", "string"),
            "value": text_value(node) or "",
        }

    if name == "variable_component":
        return {
            "op": "variable_component",
            "variable_ref": attrs.get("var_ref"),
        }

    if name == "object_component":
        return {
            "op": "object_component",
            "object_ref": attrs.get("object_ref"),
            "item_field": attrs.get("item_field"),
            "record_field": attrs.get("record_field"),
        }

    if name in OVAL_COMPONENT_OPERATIONS:
        return {
            "op": name,
            "attributes": attrs,
            "args": [
                variable_expression(child)
                for child in node
                if isinstance(child.tag, str)
            ],
        }

    return {
        "op": "preserved_unknown_component",
        "name": name,
        "namespace": ns(node.tag),
        "xml": generic_node(node),
    }


def variable_ast(e):
    kind = local(e.tag)
    base = {
        "id": e.get("id"),
        "type": kind,
        "datatype": e.get("datatype"),
    }

    if kind == "constant_variable":
        base["values"] = [
            {
                "value": text_value(child) or "",
                "datatype": child.get("datatype") or e.get("datatype"),
            }
            for child in e
            if local(child.tag) == "value"
        ]
        return base

    if kind == "external_variable":
        base["input"] = {
            "kind": "external",
            "datatype": e.get("datatype"),
        }
        return base

    if kind == "local_variable":
        components = [child for child in e if isinstance(child.tag, str)]
        base["expression"] = (
            variable_expression(components[0])
            if len(components) == 1
            else {
                "op": "invalid_component_count",
                "count": len(components),
                "components": [generic_node(c) for c in components],
            }
        )
        return base

    base["preserved"] = generic_node(e)
    return base


def parse_variable(e):
    kind = local(e.tag)
    body = [semantic_child(c) for c in e if isinstance(c.tag, str)]
    return {
        "id": e.get("id"),
        "type": kind,
        "namespace": ns(e.tag),
        "version": e.get("version"),
        "comment": e.get("comment"),
        "datatype": e.get("datatype"),
        "body": body,
        "semantic_ast": variable_ast(e),
    }



def resolve_static_variables(by_id, kind_by_id, max_values: int = 4096):
    """Resolve variable expressions only when their values are target-independent.

    Dynamic object components and external inputs remain explicit dependencies.
    Function evaluation is bounded to prevent authoring content from exploding
    the converter's memory. Exact-static status is used only for operations
    implemented directly from the OVAL 5.12.3 schema semantics.
    """
    cache = {}
    resolving = set()

    def result(status, **kwargs):
        return {"status": status, **kwargs}

    def bounded(values, operation):
        if len(values) > max_values:
            return result(
                "bounded",
                reason=f"{operation}_value_expansion_exceeds_{max_values}",
                operation=operation,
            )
        return result("exact_static", values=values, operation=operation)

    def one_child_values(node, operation):
        children = [c for c in node if isinstance(c.tag, str)]
        if len(children) != 1:
            return result(
                "unsupported",
                reason=f"{operation}_requires_one_component",
                operation=operation,
            )
        child = component_values(children[0])
        if child["status"] != "exact_static":
            return result(
                child["status"],
                reason=f"{operation}_child_not_static:{child.get('reason', child.get('operation'))}",
                operation=operation,
                blocked_by=child,
            )
        return child

    def all_children_static(node, operation, minimum=1):
        children = [c for c in node if isinstance(c.tag, str)]
        if len(children) < minimum:
            return result(
                "unsupported",
                reason=f"{operation}_requires_at_least_{minimum}_components",
                operation=operation,
            )
        out = []
        for child_node in children:
            child = component_values(child_node)
            if child["status"] != "exact_static":
                return result(
                    child["status"],
                    reason=f"{operation}_child_not_static:{child.get('reason', child.get('operation'))}",
                    operation=operation,
                    blocked_by=child,
                )
            out.append(child["values"])
        return result("exact_static", values=out, operation=operation)

    def component_values(node):
        name = local(node.tag)

        if name == "literal_component":
            return result(
                "exact_static",
                values=[text_value(node) or ""],
                operation=name,
                datatype=node.get("datatype", "string"),
            )

        if name == "variable_component":
            ref = node.get("var_ref")
            if not ref:
                return result(
                    "unsupported",
                    reason="variable_component_missing_var_ref",
                    operation=name,
                )
            resolved = variable_values(ref)
            return {
                **resolved,
                "operation": name,
                "variable_ref": ref,
            }

        if name == "object_component":
            return result(
                "dynamic_object_dependency",
                operation=name,
                object_ref=node.get("object_ref"),
                item_field=node.get("item_field"),
                record_field=node.get("record_field"),
            )

        if name == "concat":
            children = all_children_static(node, name, minimum=2)
            if children["status"] != "exact_static":
                return children
            values = [""]
            for child_values in children["values"]:
                values = [
                    prefix + str(suffix)
                    for prefix, suffix in itertools.product(values, child_values)
                ]
                if len(values) > max_values:
                    return bounded(values, name)
            return bounded(values, name)

        if name == "unique":
            children = all_children_static(node, name, minimum=1)
            if children["status"] != "exact_static":
                return children
            seen = set()
            values = []
            for child_values in children["values"]:
                for value in child_values:
                    string_value = str(value)
                    if string_value not in seen:
                        seen.add(string_value)
                        values.append(string_value)
            return bounded(values, name)

        if name == "merge":
            children = all_children_static(node, name, minimum=1)
            if children["status"] != "exact_static":
                return children

            values = [
                str(value)
                for child_values in children["values"]
                for value in child_values
            ]
            sort_mode = node.get("sort", "document")
            order = node.get("order", "ascending")
            delimiter = node.get("delimiter", "")

            if sort_mode == "document":
                pass
            elif sort_mode == "lexical":
                values = sorted(values)
            elif sort_mode == "numeric":
                try:
                    values = sorted(
                        values,
                        key=lambda value: float(value)
                        if any(ch in value.lower() for ch in ".e")
                        else int(value),
                    )
                except ValueError:
                    return result(
                        "static_evaluation_error",
                        reason="merge_numeric_sort_non_numeric_value",
                        operation=name,
                    )
            elif sort_mode == "natural":
                return result(
                    "modeled_not_static_evaluated",
                    reason="merge_natural_sort_requires_reviewed_cross-runtime_definition",
                    operation=name,
                )
            else:
                return result(
                    "unsupported",
                    reason=f"unknown_merge_sort:{sort_mode}",
                    operation=name,
                )

            if sort_mode != "document":
                if order == "descending":
                    values.reverse()
                elif order != "ascending":
                    return result(
                        "unsupported",
                        reason=f"unknown_merge_order:{order}",
                        operation=name,
                    )

            return result(
                "exact_static",
                values=[delimiter.join(values)],
                operation=name,
                datatype="string",
            )

        if name == "count":
            children = all_children_static(node, name, minimum=1)
            if children["status"] != "exact_static":
                return children
            count = sum(len(values) for values in children["values"])
            return result("exact_static", values=[str(count)], operation=name, datatype="int")

        if name == "split":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            delimiter = node.get("delimiter")
            if delimiter is None:
                return result("unsupported", reason="split_missing_delimiter", operation=name)
            values = []
            for value in child["values"]:
                values.extend(str(value).split(delimiter))
                if len(values) > max_values:
                    return bounded(values, name)
            return bounded(values, name)

        if name == "substring":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            try:
                start = int(node.get("substring_start"))
                length = int(node.get("substring_length"))
            except (TypeError, ValueError):
                return result("unsupported", reason="invalid_substring_attributes", operation=name)

            values = []
            for value in child["values"]:
                s = str(value)
                index = max(start, 1) - 1
                if index >= len(s):
                    return result(
                        "static_evaluation_error",
                        reason="substring_start_beyond_input_length",
                        operation=name,
                        input=s,
                        substring_start=start,
                    )
                values.append(s[index:] if length < 0 or length > len(s) else s[index:index + length])
            return bounded(values, name)

        if name == "begin":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            prefix = node.get("character")
            if prefix is None:
                return result("unsupported", reason="begin_missing_character", operation=name)
            values = [
                str(value) if str(value).startswith(prefix) else prefix + str(value)
                for value in child["values"]
            ]
            return bounded(values, name)

        if name == "end":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            suffix = node.get("character")
            if suffix is None:
                return result("unsupported", reason="end_missing_character", operation=name)
            values = [
                str(value) if str(value).endswith(suffix) else str(value) + suffix
                for value in child["values"]
            ]
            return bounded(values, name)

        if name == "escape_regex":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            values = [
                "".join("\\\\" + ch if ch in REGEX_META else ch for ch in str(value))
                for value in child["values"]
            ]
            return bounded(values, name)

        if name == "arithmetic":
            children = all_children_static(node, name, minimum=2)
            if children["status"] != "exact_static":
                return children
            op = node.get("arithmetic_operation")
            if op not in {"add", "multiply", "divide", "subtract"}:
                return result("unsupported", reason=f"unknown_arithmetic_operation:{op}", operation=name)

            values = []
            for combo in itertools.product(*children["values"]):
                try:
                    numeric = [float(x) if any(ch in str(x).lower() for ch in ".e") else int(x) for x in combo]
                    if op == "add":
                        value = sum(numeric)
                    elif op == "multiply":
                        value = 1
                        for x in numeric:
                            value *= x
                    elif op == "subtract":
                        value = numeric[0]
                        for x in numeric[1:]:
                            value -= x
                    else:
                        value = numeric[0]
                        for x in numeric[1:]:
                            value /= x
                    if isinstance(value, float) and value.is_integer() and all(isinstance(x, int) for x in numeric):
                        value = int(value)
                    values.append(str(value))
                except (ValueError, ZeroDivisionError):
                    return result(
                        "static_evaluation_error",
                        reason="arithmetic_input_or_operation_error",
                        operation=name,
                        inputs=[str(x) for x in combo],
                    )
                if len(values) > max_values:
                    return bounded(values, name)
            return bounded(values, name)

        # These operations are fully represented in semantic_ast but are not
        # claimed as exact-static by this prototype evaluator yet.
        if name in {"regex_capture", "glob_to_regex", "time_difference"}:
            child_ops = [
                component_values(c)
                for c in node
                if isinstance(c.tag, str)
            ]
            if any(c["status"] == "dynamic_object_dependency" for c in child_ops):
                return result(
                    "dynamic_object_dependency",
                    operation=name,
                    blocked_by=[c for c in child_ops if c["status"] != "exact_static"],
                )
            return result(
                "modeled_not_static_evaluated",
                operation=name,
                reason="function_semantics_explicit_in_ast_but_static_evaluator_not_enabled",
            )

        return result(
            "unsupported_function",
            operation=name,
            reason="component_operation_not_in_oval_5_12_3_model",
        )

    def variable_values(var_id):
        if var_id in cache:
            return cache[var_id]
        if var_id in resolving:
            return result("cycle", reason=f"variable_cycle:{var_id}")
        element = by_id.get(var_id)
        if element is None or kind_by_id.get(var_id) != "variable":
            return result("missing", reason=f"unknown_variable:{var_id}")

        resolving.add(var_id)
        kind = local(element.tag)

        if kind == "constant_variable":
            values = [
                text_value(child) or ""
                for child in element
                if local(child.tag) == "value"
            ]
            resolved = result(
                "exact_static",
                values=values,
                variable_type=kind,
                datatype=element.get("datatype"),
            )

        elif kind == "external_variable":
            resolved = result(
                "external_input",
                variable_type=kind,
                datatype=element.get("datatype"),
            )

        elif kind == "local_variable":
            components = [child for child in element if isinstance(child.tag, str)]
            if len(components) != 1:
                resolved = result(
                    "unsupported",
                    reason=f"local_variable_component_count:{len(components)}",
                    variable_type=kind,
                )
            else:
                comp = component_values(components[0])
                resolved = {
                    **comp,
                    "variable_type": kind,
                    "datatype": element.get("datatype"),
                }

        else:
            resolved = result(
                "unsupported_variable_type",
                variable_type=kind,
            )

        resolving.remove(var_id)
        cache[var_id] = resolved
        return resolved

    for oid, kind in kind_by_id.items():
        if kind == "variable":
            variable_values(oid)

    return dict(sorted(cache.items()))


def build_variable_evaluation_plans(variables, variable_resolution):
    """Build deterministic evaluation plans for every OVAL variable.

    The plan does not reinterpret OVAL semantics. It makes the already-parsed
    expression graph explicit as an execution dependency contract for later
    native lowering: static variables carry exact values, external variables
    carry typed inputs, and target-dependent local variables carry their full
    expression AST plus recursively referenced object/variable dependencies.
    """

    def expression_dependencies(node, out):
        if not isinstance(node, dict):
            return
        op = node.get("op")
        if op:
            out["operations"].add(op)
        obj = node.get("object_ref")
        if obj:
            out["objects"].add(obj)
        var = node.get("variable_ref")
        if var:
            out["variables"].add(var)
        for arg in node.get("args", []):
            expression_dependencies(arg, out)

    plans = {}
    for variable in variables:
        var_id = variable.get("id")
        ast = variable.get("semantic_ast", {})
        resolved = variable_resolution.get(var_id, {})
        status = resolved.get("status", "unknown")
        plan = {
            "variable_id": var_id,
            "variable_type": variable.get("type"),
            "datatype": variable.get("datatype"),
            "resolution_status": status,
        }

        if status == "exact_static":
            plan.update({
                "mode": "static",
                "values": resolved.get("values", []),
            })
        elif status == "external_input":
            plan.update({
                "mode": "external_input",
                "input": ast.get("input", {
                    "kind": "external",
                    "datatype": variable.get("datatype"),
                }),
            })
        elif variable.get("type") == "local_variable" and "expression" in ast:
            deps = {"objects": set(), "variables": set(), "operations": set()}
            expression_dependencies(ast["expression"], deps)
            plan.update({
                "mode": "target_dependent" if status == "dynamic_object_dependency" else "unresolved",
                "expression": ast["expression"],
                "dependencies": {
                    "objects": sorted(deps["objects"]),
                    "variables": sorted(deps["variables"]),
                    "operations": sorted(deps["operations"]),
                },
            })
            if resolved.get("reason"):
                plan["reason"] = resolved["reason"]
            if resolved.get("blocked_by") is not None:
                plan["blocked_by"] = resolved["blocked_by"]
        else:
            plan["mode"] = "unresolved"
            if resolved:
                plan["resolution"] = resolved

        plans[var_id] = plan

    return dict(sorted(plans.items()))


def feature_inventory(root):
    elements = {}
    attributes = {}
    namespaces = {}
    for e in root.iter():
        n = local(e.tag)
        elements[n] = elements.get(n, 0) + 1
        uri = ns(e.tag)
        namespaces[uri] = namespaces.get(uri, 0) + 1
        for k, v in e.attrib.items():
            a = etree.QName(k).localname
            if a in CORE_ATTRS:
                attributes.setdefault(a, {})
                attributes[a][v] = attributes[a].get(v, 0) + 1
    return {
        "elements": dict(sorted(elements.items())),
        "attributes": {k: dict(sorted(v.items())) for k, v in sorted(attributes.items())},
        "namespaces": dict(sorted(namespaces.items())),
    }


def parse(path: Path, provenance_path: Path | None = None):
    data = path.read_bytes()
    provenance = (
        json.loads(provenance_path.read_text(encoding="utf-8"))
        if provenance_path is not None else None
    )
    root = etree.fromstring(data)
    if local(root.tag) != "oval_definitions":
        raise ValueError(f"{path}: root is {local(root.tag)}, expected oval_definitions")

    section_elements = {}
    by_id = {}
    kind_by_id = {}
    for section in root:
        sn = local(section.tag)
        if sn not in SECTION_KIND:
            continue
        section_elements[sn] = section
        for item in section:
            oid = item.get("id")
            if not oid:
                continue
            if oid in by_id:
                raise ValueError(f"{path}: duplicate OVAL id {oid}")
            by_id[oid] = item
            kind_by_id[oid] = SECTION_KIND[sn]

    known = set(by_id)
    graph = {}
    dependency_edges = []
    unresolved = set()
    for oid, element in by_id.items():
        refs, missing, edges = collect_refs(oid, element, known)
        graph[oid] = sorted(refs)
        dependency_edges.extend(edges)
        unresolved |= missing

    edge_targets = {e["to"] for e in dependency_edges if e.get("resolved", True)}
    missing_edge_targets = sorted(edge_targets - known)
    unresolved |= set(missing_edge_targets)

    definitions = []
    tests = []
    objects = []
    states = []
    variables = []
    for oid, e in by_id.items():
        kind = kind_by_id[oid]
        if kind == "definition":
            definitions.append(parse_definition(e))
        elif kind == "test":
            tests.append(parse_test(e))
        elif kind == "object":
            objects.append(parse_object(e))
        elif kind == "state":
            states.append(parse_state(e))
        elif kind == "variable":
            variables.append(parse_variable(e))

    generator = next((generic_node(x) for x in root if local(x.tag) == "generator"), None)

    semantic = {
        "ir_version": "0.1-prototype",
        "source": {
            "path": path.as_posix(),
            "sha256": sha256(data),
            "bytes": len(data),
            "provenance_path": provenance_path.as_posix() if provenance_path else None,
        },
        "xccdf_context": (
            {
                "rule_id": provenance.get("xccdf_rule_id"),
                "title": provenance.get("xccdf_title"),
                "component": provenance.get("xccdf_component"),
                "checks": provenance.get("checks", []),
                "check_exports": provenance.get("check_exports", []),
                "published_source": provenance.get("source"),
            }
            if provenance else None
        ),
        "parser_contract": {
            "core_logic_model": "explicit",
            "platform_specific_nodes": "losslessly_preserved",
            "policy_intent_inference": "forbidden",
            "ambiguous_native_mapping": "requires_review",
            "static_variable_evaluation": "conservative_exact_only",
        },
        "generator": generator,
        "definitions": definitions,
        "tests": tests,
        "objects": objects,
        "states": states,
        "variables": variables,
        "variable_resolution": resolve_static_variables(by_id, kind_by_id),
        "variable_function_model": {
            "known_operations": sorted(OVAL_COMPONENT_OPERATIONS),
            "static_evaluator_operations": sorted(STATIC_EVALUATOR_OPERATIONS),
            "all_component_operations_have_explicit_ast": True,
        },
        "reference_graph": graph,
        "dependency_edges": dependency_edges,
        "dependency_integrity": {
            "all_resolved_edge_targets_present": not missing_edge_targets,
            "missing_edge_targets": missing_edge_targets,
            "edge_count": len(dependency_edges),
        },
        "unresolved_references": sorted(unresolved),
        "features": feature_inventory(root),
        "native_translation": {
            "status": "requires_review",
            "note": (
                "Structural OVAL semantics are represented. Native SCAP-NG "
                "capability mappings are a separate reviewed translation layer."
            ),
        },
    }

    semantic["variable_evaluation_plans"] = build_variable_evaluation_plans(
        semantic["variables"], semantic["variable_resolution"]
    )

    if provenance:
        exports_by_name = {}
        for export in provenance.get("check_exports", []):
            name = export.get("export_name")
            if name:
                exports_by_name.setdefault(name, []).append(export)
        for variable in semantic["variables"]:
            if variable.get("type") != "external_variable":
                continue
            bindings = exports_by_name.get(variable.get("id"), [])
            variable["semantic_ast"].setdefault("input", {})["xccdf_check_exports"] = bindings
            resolved = semantic.get("variable_resolution", {}).get(variable.get("id"))
            if resolved is not None and bindings:
                resolved["xccdf_check_exports"] = bindings

    digest_basis = dict(semantic)
    digest_basis["source"] = {
        "sha256": semantic["source"]["sha256"],
    }
    digest_basis.pop("native_translation", None)
    canonical = json.dumps(
        digest_basis, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    semantic["semantic_ir_sha256"] = sha256(canonical)
    return semantic


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--provenance", type=Path)
    ap.add_argument("--fail-on-unresolved", action="store_true")
    args = ap.parse_args()

    ir = parse(args.input, args.provenance)
    text = json.dumps(ir, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")

    if args.fail_on_unresolved and ir["unresolved_references"]:
        for ref in ir["unresolved_references"]:
            print(f"ERROR: unresolved OVAL reference {ref}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
