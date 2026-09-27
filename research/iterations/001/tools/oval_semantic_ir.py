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
import json
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
    mapping = {
        "definition_ref": "extend_definition",
        "test_ref": "criterion_test",
        "object_ref": "object_reference",
        "state_ref": "state_reference",
        "var_ref": "variable_reference",
    }
    if source in mapping:
        return mapping[source]
    if name == "object_reference" and source == "text":
        return "set_object_reference"
    if name == "filter" and source == "text":
        return "set_filter_state"
    return f"{name}:{source}"


def collect_refs(source_id: str, e, known_ids: set[str]):
    refs = set()
    unresolved = set()
    edges = []
    for n in e.iter():
        for attr_name, v in n.attrib.items():
            value = v.strip()
            attr = local(attr_name)
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
    }



def resolve_static_variables(by_id, kind_by_id, max_values: int = 4096):
    """Resolve variable expressions that are purely deterministic/static.

    OVAL variables are multi-valued. concat therefore computes the Cartesian
    product of child component value sets. Dynamic object-dependent and external
    variables are preserved as unresolved rather than guessed.
    """
    cache = {}
    resolving = set()

    def result(status, **kwargs):
        return {"status": status, **kwargs}

    def component_values(node):
        name = local(node.tag)

        if name == "literal_component":
            return result("exact_static", values=[text_value(node) or ""], operation=name)

        if name == "variable_component":
            ref = node.get("var_ref")
            if not ref:
                return result("unsupported", reason="variable_component_missing_var_ref", operation=name)
            resolved = variable_values(ref)
            return {
                **resolved,
                "operation": name,
                "variable_ref": ref,
            }

        if name == "concat":
            parts = []
            for child in node:
                child_result = component_values(child)
                if child_result["status"] != "exact_static":
                    return result(
                        child_result["status"],
                        reason=f"concat_child_not_static:{child_result.get('reason', child_result.get('operation'))}",
                        operation=name,
                    )
                parts.append(child_result["values"])

            values = [""]
            for child_values in parts:
                next_values = []
                for prefix in values:
                    for suffix in child_values:
                        next_values.append(prefix + suffix)
                        if len(next_values) > max_values:
                            return result(
                                "bounded",
                                reason=f"concat_value_expansion_exceeds_{max_values}",
                                operation=name,
                            )
                values = next_values
            return result("exact_static", values=values, operation=name)

        if name == "unique":
            children = list(node)
            if len(children) != 1:
                return result("unsupported", reason="unique_requires_one_component", operation=name)
            child_result = component_values(children[0])
            if child_result["status"] != "exact_static":
                return result(child_result["status"], reason=child_result.get("reason"), operation=name)
            # Preserve source order while removing duplicates.
            seen = set()
            values = []
            for value in child_result["values"]:
                if value not in seen:
                    seen.add(value)
                    values.append(value)
            return result("exact_static", values=values, operation=name)

        # These require collected object data, runtime/external values, or
        # function semantics not yet implemented in the prototype evaluator.
        if name == "object_component":
            return result(
                "dynamic_object_dependency",
                operation=name,
                object_ref=node.get("object_ref"),
                item_field=node.get("item_field"),
            )

        return result("unsupported_function", operation=name)

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
            resolved = result("exact_static", values=values, variable_type=kind)

        elif kind == "external_variable":
            resolved = result("external_input", variable_type=kind)

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
                resolved = {**comp, "variable_type": kind}

        else:
            resolved = result("unsupported_variable_type", variable_type=kind)

        resolving.remove(var_id)
        cache[var_id] = resolved
        return resolved

    for oid, kind in kind_by_id.items():
        if kind == "variable":
            variable_values(oid)

    return dict(sorted(cache.items()))


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


def parse(path: Path):
    data = path.read_bytes()
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
        },
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
    ap.add_argument("--fail-on-unresolved", action="store_true")
    args = ap.parse_args()

    ir = parse(args.input)
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
