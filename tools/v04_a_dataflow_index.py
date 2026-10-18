#!/usr/bin/env python3
"""#240: static source-dataflow index for validated 0.4-A base authoring.

This is a dependency/source-location auditor, NOT a runnable collection plan.
Tests, named Variables and shared Objects retain distinct identities.
Set/Filter/for_each sites remain ordered AST locations; no filter pushdown,
foreach Test expansion, Variable value evaluation or status decisions occur.
"""
from __future__ import annotations

from hashlib import sha256

from v04_a_authoring_graph_index import canonical_json


def _walk(value, prefix):
    """Walk parsed source without collapsing repeated collection/filter sites."""
    stack = [(prefix, value)]
    while stack:
        path, node = stack.pop()
        if isinstance(node, dict):
            yield path, node
            stack.extend((path + [key], child) for key, child in
                         reversed(sorted(node.items())))
        elif isinstance(node, list):
            stack.extend((path + [i], child) for i, child in
                         reversed(list(enumerate(node))))


def _graph_order(dependency_map):
    """Deterministic, dependency-first structural order; no execution claim."""
    # Iterative DFS avoids recursion limits on maliciously deep source graphs.
    color = {}
    result = []
    for initial in sorted(dependency_map):
        if color.get(initial) == 2:
            continue
        stack = [(initial, False)]
        while stack:
            key, completed = stack.pop()
            if completed:
                color[key] = 2
                result.append(key)
                continue
            if color.get(key) == 2:
                continue
            if color.get(key) == 1:
                raise ValueError(f"cyclic source dataflow dependency through {key!r}")
            color[key] = 1
            stack.append((key, True))
            for target in sorted(set(dependency_map[key]), reverse=True):
                stack.append((target, False))
    return [{"kind": kind, "id": identity} for kind, identity in result]


def index_assessment_dataflow(assessment):
    """Preserve named source nodes, explicit dependency edges and lexical sites.

    All inputs must first pass version-local base and capability schemas.
    Identifiers are resolved only within this Assessment. Nested inline Objects
    are retained by their absolute source paths, not invented named nodes.
    """
    if not isinstance(assessment, dict):
        raise ValueError("Assessment must be a mapping")
    table = {"object": assessment.get("shared_objects") or {},
             "variable": assessment.get("variables") or {},
             "test": assessment.get("tests") or {}}
    for kind, declarations in table.items():
        if not isinstance(declarations, dict):
            raise ValueError(f"{kind} declarations must be mappings")
    nodes, edges, sites = [], [], []
    dependency_map = {}

    for kind in ("object", "variable", "test"):
        for identity, definition in sorted(table[kind].items()):
            if not isinstance(identity, str) or not identity:
                raise ValueError(f"empty {kind} source identity")
            if not isinstance(definition, dict):
                raise ValueError(f"invalid {kind} source definition: {identity}")
            base = {"object": "shared_objects", "variable": "variables",
                    "test": "tests"}[kind]
            origin = [base, identity]
            nodes.append({"kind": kind, "id": identity, "path": origin,
                          "source_sha256": sha256(canonical_json(definition)).hexdigest()})
            if kind != "test":
                dependency_map[(kind, identity)] = []
            for path, value in _walk(definition, origin):
                # An Object reference is an acquisition dependency; a Variable
                # reference is a value dependency. Neither is a truth edge.
                for field, target_kind, role in (
                    ("variable", "variable", "variable_value"),
                    ("object", "object", "object_acquisition"),
                ):
                    if isinstance(value.get(field), str):
                        target = value[field]
                        if target not in table[target_kind]:
                            raise ValueError(
                                f"{kind} {identity} at {path + [field]}: "
                                f"unresolved {target_kind} {target!r}")
                        edges.append({"from_kind": kind, "from_id": identity,
                                      "to_kind": target_kind, "to_id": target,
                                      "role": role, "path": path + [field]})
                        if kind != "test":
                            dependency_map[(kind, identity)].append((target_kind, target))
                if "for_each" in value:
                    item = value["for_each"]
                    if not (isinstance(item, dict) and
                            isinstance(item.get("item"), str) and item["item"] and
                            isinstance(item.get("in"), str) and item["in"]):
                        raise ValueError(f"{kind} {identity}: invalid for_each source")
                    target = item["in"]
                    if target not in table["object"]:
                        raise ValueError(
                            f"{kind} {identity}: unresolved for_each Object {target!r}")
                    edges.append({"from_kind": kind, "from_id": identity,
                                  "to_kind": "object", "to_id": target,
                                  "role": "for_each_source", "path": path + ["for_each", "in"]})
                    if kind != "test":
                        dependency_map[(kind, identity)].append(("object", target))
                    sites.append({"kind": "for_each", "path": path + ["for_each"],
                                  "source_sha256": sha256(canonical_json(item)).hexdigest()})
                if "set" in value and isinstance(value["set"], dict):
                    sites.append({"kind": "set", "path": path + ["set"],
                                  "source_sha256": sha256(canonical_json(value["set"])).hexdigest()})
                if "filters" in value and isinstance(value["filters"], list):
                    for index, flt in enumerate(value["filters"]):
                        if not isinstance(flt, dict) or set(flt) not in ({"include"}, {"exclude"}):
                            raise ValueError(
                                f"{kind} {identity}: Filter action missing or ambiguous at "
                                f"{path + ['filters', index]}")
                        sites.append({"kind": "filter", "path": path + ["filters", index],
                                      "source_sha256": sha256(canonical_json(flt)).hexdigest()})
                if "select" in value and isinstance(value["select"], dict):
                    for field, selector in sorted(value["select"].items()):
                        if isinstance(selector, dict) and isinstance(selector.get("from"), str):
                            sites.append({"kind": "projection", "path": path + ["select", field, "from"],
                                          "source_sha256": sha256(canonical_json(selector)).hexdigest()})

    # Only named Objects and Variables participate in the source-dataflow DAG;
    # a Test consumes data but never becomes an acquisition/Variable provider.
    order = _graph_order(dependency_map)
    edges.sort(key=lambda e: (e["from_kind"], e["from_id"],
                              canonical_json(e["path"]), e["role"], e["to_id"]))
    sites.sort(key=lambda s: (canonical_json(s["path"]), s["kind"]))
    return {
        "status": "SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE",
        "nodes": nodes,
        "edges": edges,
        "sites": sites,
        "dependency_first_source_order": order,
        "edge_count": len(edges),
        "unverified": [
            "collector execution and source Item identity",
            "for_each lexical alias typing, nesting and runtime correlation",
            "Set operand Item membership/filter outcomes and status",
            "Variable evaluation, source completeness and six-state outcomes",
        ],
    }
