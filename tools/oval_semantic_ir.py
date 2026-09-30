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
import calendar
import datetime as dt
import decimal
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
    "recurse_direction", "max_depth", "behaviors", "action", "set_operator",
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
    "glob_to_regex",
    "merge",
    "regex_capture",
    "split",
    "substring",
    "time_difference",
    "unique",
}

REGEX_META = set("^$\\.[](){}*+?|")




OVAL_RESULTS = (
    "true",
    "false",
    "error",
    "unknown",
    "not_evaluated",
    "not_applicable",
)


def oval_negate_result(value):
    """Apply OVAL negation: only true/false are inverted."""
    if value not in OVAL_RESULTS:
        raise ValueError(f"unknown OVAL result {value}")
    if value=="true":
        return "false"
    if value=="false":
        return "true"
    return value


def oval_combine_results(operator, results):
    """Combine OVAL result values using the 5.12.3 OperatorEnumeration tables."""
    operator=operator.upper()
    values=list(results)
    if not values:
        raise ValueError("OVAL operator requires at least one result")
    if any(value not in OVAL_RESULTS for value in values):
        bad=[value for value in values if value not in OVAL_RESULTS]
        raise ValueError(f"unknown OVAL result values: {bad}")

    counts={value:values.count(value) for value in OVAL_RESULTS}
    t=counts["true"]
    f=counts["false"]
    e=counts["error"]
    u=counts["unknown"]
    ne=counts["not_evaluated"]
    na=counts["not_applicable"]

    if operator=="AND":
        if f:
            return "false"
        if e:
            return "error"
        if u:
            return "unknown"
        if ne:
            return "not_evaluated"
        if t:
            return "true"
        return "not_applicable"

    if operator=="OR":
        if t:
            return "true"
        if e:
            return "error"
        if u:
            return "unknown"
        if ne:
            return "not_evaluated"
        if f:
            return "false"
        return "not_applicable"

    if operator=="ONE":
        if t>=2:
            return "false"
        if t==0 and f:
            return "false"
        if e:
            return "error"
        if u:
            return "unknown"
        if ne:
            return "not_evaluated"
        if t==1:
            return "true"
        return "not_applicable"

    if operator=="XOR":
        if e:
            return "error"
        if u:
            return "unknown"
        if ne:
            return "not_evaluated"
        if t==0 and f==0 and na:
            return "not_applicable"
        return "true" if t%2 else "false"

    raise ValueError(f"unknown OVAL boolean operator {operator}")


OVAL_SET_FLAGS = (
    "error",
    "complete",
    "incomplete",
    "does_not_exist",
    "not_collected",
    "not_applicable",
)

# OVAL 5.12.3 set flag-combination tables. Rows are the second operand's
# flag; columns are the first operand's flag, matching the schema charts.
OVAL_SET_FLAG_TABLES = {
    "UNION": {
        "error":          ["error","error","error","error","error","error"],
        "complete":       ["error","complete","incomplete","complete","incomplete","complete"],
        "incomplete":     ["error","incomplete","incomplete","incomplete","incomplete","incomplete"],
        "does_not_exist": ["error","complete","incomplete","does_not_exist","incomplete","does_not_exist"],
        "not_collected":  ["error","incomplete","incomplete","incomplete","not_collected","not_collected"],
        "not_applicable": ["error","complete","incomplete","does_not_exist","not_collected","not_applicable"],
    },
    "INTERSECTION": {
        "error":          ["error","error","error","does_not_exist","error","error"],
        "complete":       ["error","complete","incomplete","does_not_exist","not_collected","complete"],
        "incomplete":     ["error","incomplete","incomplete","does_not_exist","not_collected","incomplete"],
        "does_not_exist": ["does_not_exist","does_not_exist","does_not_exist","does_not_exist","does_not_exist","does_not_exist"],
        "not_collected":  ["error","not_collected","not_collected","does_not_exist","not_collected","not_collected"],
        "not_applicable": ["error","complete","incomplete","does_not_exist","not_collected","not_applicable"],
    },
    "COMPLEMENT": {
        "error":          ["error","error","error","does_not_exist","error","error"],
        "complete":       ["error","complete","incomplete","does_not_exist","not_collected","error"],
        "incomplete":     ["error","error","error","does_not_exist","not_collected","error"],
        "does_not_exist": ["error","complete","incomplete","does_not_exist","not_collected","error"],
        "not_collected":  ["error","not_collected","not_collected","does_not_exist","not_collected","error"],
        "not_applicable": ["error","error","error","error","error","error"],
    },
}


def oval_set_flag(operator, first_flag, second_flag):
    """Combine two collected-object flags exactly per OVAL 5.12.3."""
    operator=operator.upper()
    if operator not in OVAL_SET_FLAG_TABLES:
        raise ValueError(f"unknown OVAL set operator {operator}")
    if first_flag not in OVAL_SET_FLAGS or second_flag not in OVAL_SET_FLAGS:
        raise ValueError(f"unknown OVAL collection flag: {first_flag}, {second_flag}")
    column=OVAL_SET_FLAGS.index(first_flag)
    return OVAL_SET_FLAG_TABLES[operator][second_flag][column]


def oval_set_items(operator, operands):
    """Apply OVAL set membership semantics to already-collected unique items.

    Items may be any JSON-serializable values. OVAL set results are unique.
    COMPLEMENT is relative and therefore requires exactly two operands.
    """
    operator=operator.upper()

    def key(item):
        return json.dumps(item,sort_keys=True,separators=(",",":"),ensure_ascii=False)

    def unique(items):
        seen=set()
        out=[]
        for item in items:
            k=key(item)
            if k not in seen:
                seen.add(k)
                out.append(item)
        return out

    operands=[unique(list(x)) for x in operands]
    if not operands:
        raise ValueError("OVAL set requires at least one operand")
    if len(operands)==1:
        return operands[0]

    if operator=="UNION":
        return unique([item for operand in operands for item in operand])

    if operator=="INTERSECTION":
        common={key(item):item for item in operands[0]}
        for operand in operands[1:]:
            keys={key(item) for item in operand}
            common={k:v for k,v in common.items() if k in keys}
        return list(common.values())

    if operator=="COMPLEMENT":
        if len(operands)!=2:
            raise ValueError("OVAL COMPLEMENT requires exactly two operands")
        remove={key(item) for item in operands[1]}
        return [item for item in operands[0] if key(item) not in remove]

    raise ValueError(f"unknown OVAL set operator {operator}")


def oval_apply_filter(items, matches, action="exclude"):
    """Apply one OVAL filter to a collected item list.

    The matches sequence aligns one-for-one with items and indicates whether
    each item satisfies the referenced OVAL state. Default action is exclude.
    """
    if len(items)!=len(matches):
        raise ValueError("OVAL filter match vector must align with items")
    action=action.lower()
    if action not in {"include","exclude"}:
        raise ValueError(f"unknown OVAL filter action {action}")
    if action=="include":
        return [item for item,matched in zip(items,matches) if matched]
    return [item for item,matched in zip(items,matches) if not matched]


def oval_apply_filters(items, filters):
    """Apply OVAL filters sequentially before the enclosing set operator.

    Each filter is a pair of action and predicate. The predicate must return
    an explicit bool indicating whether the item matches the referenced state.
    Six-state/error outcomes are deliberately rejected here until collection
    flag propagation for failed filter-state evaluation is modeled exactly;
    they must never be coerced through host-language truthiness.
    """
    current=list(items)
    for action,predicate in filters:
        matches=[]
        for item in current:
            matched=predicate(item)
            if not isinstance(matched,bool):
                raise ValueError(
                    "OVAL filter predicate must return explicit bool; "
                    f"got {matched!r}"
                )
            matches.append(matched)
        current=oval_apply_filter(current,matches,action or "exclude")
    return current


def local(tag) -> str | None:
    if not isinstance(tag, str):
        return None
    return etree.QName(tag).localname


def ns(tag) -> str:
    if not isinstance(tag, str):
        return ""
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
        if not isinstance(n.tag, str):
            continue
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
        "operator": e.get("set_operator", "UNION"),
        "operator_explicit": "set_operator" in e.attrib,
        "children": [],
        "evaluation_semantics": {
            "unique_items": True,
            "filters_apply_before_set_operator": True,
            "filter_default_action": "exclude",
            "complement_is_relative": True,
        },
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
                "action": c.get("action", "exclude"),
                "action_explicit": "action" in c.attrib,
            })
        else:
            out["children"].append({
                "kind": "preserved",
                "xml": generic_node(c),
            })
    return out


# Scoped known OVAL 5.12.3 effective defaults. This is intentionally not a
# generic XML-schema default resolver: inherited platform behavior types still
# require a separate complete-schema audit.
KNOWN_ATTRIBUTE_DEFAULTS = {
    "test": {
        "check_existence": ("at_least_one_exists", "xsd_default"),
        "state_operator": ("AND", "xsd_default"),
    },
    "state": {"operator": ("AND", "xsd_default")},
    "state_entity": {
        "check_existence": ("at_least_one_exists", "xsd_default"),
        "entity_check": ("all", "xsd_default"),
    },
}


def effective_attributes(e, scope):
    """Report effective known values and their origin without changing raw XML.

    The output is supplementary IR metadata, not a replacement for the
    original attributes. Unknown/platform-specific defaults remain unresolved.
    The var_check omission rule is documented implicit behavior (not an XSD
    default) and applies only when the state entity references a variable.
    """
    if scope not in KNOWN_ATTRIBUTE_DEFAULTS:
        raise ValueError(f"unknown default resolution scope: {scope}")
    defaults = dict(KNOWN_ATTRIBUTE_DEFAULTS[scope])
    if scope == "state_entity" and e.get("var_ref") is not None:
        defaults["var_check"] = ("all", "documented_implicit")
    result = {}
    for name, (default_value, provenance) in defaults.items():
        explicit = name in e.attrib
        result[name] = {
            "value": e.get(name) if explicit else default_value,
            "origin": "explicit" if explicit else provenance,
        }
    return result


def semantic_child(e, *, context=None):
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
    if context == "state_entity" and n != "notes":
        out["effective_attributes"] = effective_attributes(e, "state_entity")
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
        "effective_attributes": effective_attributes(e, "test"),
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
        "effective_attributes": effective_attributes(e, "state"),
        "entities": [semantic_child(c, context="state_entity") for c in e if isinstance(c.tag, str)],
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

    def canonical_item(item):
        return json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def unique_items(items):
        seen = set()
        out = []
        for item in items:
            key = canonical_item(item)
            if key not in seen:
                seen.add(key)
                out.append(item)
        return out

    def synthetic_set_items(set_element):
        refs_or_sets = []
        filters = []
        for child in set_element:
            name = local(child.tag)
            if name == "object_reference":
                refs_or_sets.append(("object", text_value(child)))
            elif name == "set":
                refs_or_sets.append(("set", child))
            elif name == "filter":
                filters.append(child)

        if filters:
            return result(
                "dynamic_object_dependency",
                reason="synthetic_set_filter_evaluation_not_implemented",
                operation="set",
            )

        operands = []
        for kind, value in refs_or_sets:
            resolved = (
                synthetic_object_items(value)
                if kind == "object"
                else synthetic_set_items(value)
            )
            if resolved["status"] != "exact_static":
                return resolved
            operands.append(resolved["items"])

        if not operands:
            return result("unsupported", reason="set_has_no_operands", operation="set")

        operator = set_element.get("set_operator", "UNION")
        if operator == "UNION":
            items = unique_items([item for operand in operands for item in operand])
        elif operator == "INTERSECTION":
            common = {canonical_item(x): x for x in operands[0]}
            for operand in operands[1:]:
                keys = {canonical_item(x) for x in operand}
                common = {k: v for k, v in common.items() if k in keys}
            items = list(common.values())
        elif operator == "COMPLEMENT":
            if len(operands) != 2:
                return result(
                    "unsupported",
                    reason=f"complement_requires_two_operands:{len(operands)}",
                    operation="set",
                )
            remove = {canonical_item(x) for x in operands[1]}
            items = [x for x in operands[0] if canonical_item(x) not in remove]
        else:
            return result(
                "unsupported",
                reason=f"unknown_set_operator:{operator}",
                operation="set",
            )
        return {"status": "exact_static", "items": unique_items(items), "operation": "set"}

    def synthetic_object_items(object_ref):
        element = by_id.get(object_ref)
        if element is None or kind_by_id.get(object_ref) != "object":
            return result(
                "dynamic_object_dependency",
                reason=f"object_component_unknown_object:{object_ref}",
                operation="object_component",
            )

        object_type = local(element.tag)
        if object_type != "variable_object":
            return result(
                "dynamic_object_dependency",
                reason=f"object_component_requires_collection:{object_type}",
                operation="object_component",
                object_ref=object_ref,
            )

        children = [c for c in element if isinstance(c.tag, str)]
        set_children = [c for c in children if local(c.tag) == "set"]
        if set_children:
            if len(set_children) != 1:
                return result(
                    "unsupported",
                    reason=f"variable_object_set_count:{len(set_children)}",
                    operation="object_component",
                )
            return synthetic_set_items(set_children[0])

        var_refs = [text_value(c) for c in children if local(c.tag) == "var_ref"]
        if len(var_refs) != 1 or not var_refs[0]:
            return result(
                "dynamic_object_dependency",
                reason=f"variable_object_var_ref_count:{len(var_refs)}",
                operation="object_component",
                object_ref=object_ref,
            )
        resolved = variable_values(var_refs[0])
        if resolved["status"] != "exact_static":
            return result(
                resolved["status"],
                reason=f"variable_object_variable_not_static:{var_refs[0]}",
                operation="object_component",
                object_ref=object_ref,
                blocked_by=resolved,
            )
        return {
            "status": "exact_static",
            "items": [{"value": list(resolved.get("values", []))}],
            "operation": "variable_object",
            "object_ref": object_ref,
        }

    def natural_sort_key(value):
        parts = pyre.split(r"([0-9]+)", str(value))
        return tuple(
            (0, int(part)) if part.isdigit() else (1, part)
            for part in parts
            if part != ""
        )

    def oval_regex_escape_literal(ch):
        return "\\" + ch if ch in REGEX_META else ch

    def oval_glob_to_regex(pattern, noescape=False):
        """Convert an OVAL glob pattern to its Perl-style regex representation.

        This follows the OVAL 5.12.3 glob_to_regex contract rather than
        Python fnmatch semantics: '*' and '?' never cross '/', each path
        segment excludes leading '.', brace/tilde expansion is not performed,
        and backslash escaping is controlled by glob_noescape.
        """
        if pattern == "":
            return "^$"

        out = ["^"]
        segment_start = True
        i = 0
        while i < len(pattern):
            if segment_start:
                out.append(r"(?=[^\.])")
                segment_start = False

            ch = pattern[i]
            if ch == "/":
                out.append("/")
                segment_start = True
                i += 1
                continue

            if ch == "\\" and not noescape:
                if i + 1 >= len(pattern):
                    raise ValueError("trailing escape in glob")
                out.append(oval_regex_escape_literal(pattern[i + 1]))
                i += 2
                continue

            if ch == "\\" and noescape:
                out.append(r"\\")
                i += 1
                continue

            if ch == "*":
                out.append(r"[^/]*")
                i += 1
                continue

            if ch == "?":
                out.append(r"[^/]")
                i += 1
                continue

            if ch == "[":
                if pattern.startswith("[[:", i):
                    end = pattern.find(":]]", i + 3)
                    if end < 0:
                        raise ValueError("unterminated POSIX character class")
                    out.append(pattern[i:end + 3])
                    i = end + 3
                    continue
                end = pattern.find("]", i + 1)
                if end < 0:
                    raise ValueError("unterminated character class")
                out.append(pattern[i:end + 1])
                i = end + 1
                continue

            out.append(oval_regex_escape_literal(ch))
            i += 1

        out.append("$")
        return "".join(out)

    def parse_oval_datetime(value, format_name):
        text = str(value).strip()

        if format_name == "seconds_since_epoch":
            return int(text, 10)

        if format_name == "win_filetime":
            # OVAL test content represents Windows FILETIME as hexadecimal
            # 100-nanosecond intervals since 1601-01-01 UTC.
            ticks = int(text, 16)
            return ticks // 10_000_000 - 11_644_473_600

        formats = {
            "year_month_day": (
                "%Y%m%d",
                "%Y%m%dT%H%M%S",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
            ),
            "month_day_year": (
                "%m/%d/%Y %H:%M:%S",
                "%m/%d/%Y",
                "%m-%d-%Y %H:%M:%S",
                "%m-%d-%Y",
                "%B, %d %Y %H:%M:%S",
                "%B, %d %Y",
                "%b, %d %Y %H:%M:%S",
                "%b, %d %Y",
            ),
            "day_month_year": (
                "%d/%m/%Y %H:%M:%S",
                "%d/%m/%Y",
                "%d-%m-%Y %H:%M:%S",
                "%d-%m-%Y",
            ),
        }
        if format_name not in formats:
            raise ValueError(f"unsupported OVAL date-time format {format_name}")

        for pattern in formats[format_name]:
            try:
                parsed = dt.datetime.strptime(text, pattern)
                return calendar.timegm(parsed.timetuple())
            except ValueError:
                pass
        raise ValueError(f"value {text!r} does not match {format_name}")

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
            object_ref = node.get("object_ref")
            item_field = node.get("item_field")
            record_field = node.get("record_field")
            if record_field:
                return result(
                    "dynamic_object_dependency",
                    reason="synthetic_record_field_collection_not_implemented",
                    operation=name,
                    object_ref=object_ref,
                    item_field=item_field,
                    record_field=record_field,
                )
            collected = synthetic_object_items(object_ref)
            if collected["status"] != "exact_static":
                return {
                    **collected,
                    "operation": name,
                    "object_ref": object_ref,
                    "item_field": item_field,
                    "record_field": record_field,
                }
            values = []
            for item in collected["items"]:
                if item_field not in item:
                    return result(
                        "static_evaluation_error",
                        reason=f"object_component_item_field_missing:{item_field}",
                        operation=name,
                        object_ref=object_ref,
                    )
                field = item[item_field]
                values.extend(field if isinstance(field, list) else [field])
            return bounded(values, name)

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

        if name == "time_difference":
            children = [c for c in node if isinstance(c.tag, str)]
            if len(children) not in {1, 2}:
                return result(
                    "unsupported",
                    reason=f"time_difference_component_count:{len(children)}",
                    operation=name,
                )

            child_results = [component_values(child) for child in children]
            if any(child["status"] != "exact_static" for child in child_results):
                first = next(child for child in child_results if child["status"] != "exact_static")
                return result(
                    first["status"],
                    reason=f"time_difference_child_not_static:{first.get('reason', first.get('operation'))}",
                    operation=name,
                    blocked_by=first,
                )

            if len(children) == 1:
                return result(
                    "runtime_time_dependency",
                    reason="time_difference_single_component_uses_current_utc_time",
                    operation=name,
                    format_2=node.get("format_2", "year_month_day"),
                    values=child_results[0]["values"],
                )

            format_1 = node.get("format_1", "year_month_day")
            format_2 = node.get("format_2", "year_month_day")
            values = []
            try:
                for left, right in itertools.product(
                    child_results[0]["values"], child_results[1]["values"]
                ):
                    values.append(str(
                        parse_oval_datetime(left, format_1)
                        - parse_oval_datetime(right, format_2)
                    ))
            except (ValueError, OverflowError) as exc:
                return result(
                    "static_evaluation_error",
                    reason=f"time_difference_invalid_value:{exc}",
                    operation=name,
                )
            return bounded(values, name)

        if name == "glob_to_regex":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            noescape = node.get("glob_noescape", "false").lower() == "true"
            values = []
            try:
                for value in child["values"]:
                    values.append(oval_glob_to_regex(str(value), noescape=noescape))
            except ValueError as exc:
                return result(
                    "static_evaluation_error",
                    reason=f"glob_to_regex_invalid_pattern:{exc}",
                    operation=name,
                )
            return bounded(values, name)

        if name == "regex_capture":
            child = one_child_values(node, name)
            if child["status"] != "exact_static":
                return child
            pattern = node.get("pattern", "")
            try:
                rx = pyre.compile(pattern)
            except pyre.error as exc:
                return result(
                    "static_evaluation_error",
                    reason=f"regex_capture_invalid_pattern:{exc}",
                    operation=name,
                )
            values = []
            for value in child["values"]:
                match = rx.search(str(value))
                if match is None or rx.groups == 0:
                    values.append("")
                else:
                    values.append(match.group(1) or "")
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
                values = sorted(values, key=natural_sort_key)
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
                "".join("\\" + ch if ch in REGEX_META else ch for ch in str(value))
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
                    texts = [str(x) for x in combo]
                    has_float = any(any(ch in text.lower() for ch in ".e") for text in texts)
                    numeric = [decimal.Decimal(text) for text in texts]
                    if op == "add":
                        value = sum(numeric, decimal.Decimal(0))
                    elif op == "multiply":
                        value = decimal.Decimal(1)
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

                    if not has_float and value == value.to_integral_value():
                        rendered = str(int(value))
                    else:
                        rendered = format(value, "f")
                        if "." in rendered:
                            rendered = rendered.rstrip("0").rstrip(".")
                        if rendered in {"", "-0"}:
                            rendered = "0"
                    values.append(rendered)
                except (decimal.InvalidOperation, decimal.DivisionByZero, ValueError, ZeroDivisionError):
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
            plan_mode = {
                "dynamic_object_dependency": "target_dependent",
                "runtime_time_dependency": "runtime_dependent",
            }.get(status, "unresolved")
            plan.update({
                "mode": plan_mode,
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
        if not isinstance(e.tag, str):
            continue
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
        if not isinstance(section.tag, str):
            continue
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
