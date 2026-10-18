#!/usr/bin/env python3
"""#229: independent reference execution of accepted 0.4-A expression source.

Deliberately reads the *original source tree*, never the postorder plan.
Uses separately pinned OVAL 5.12.3 result tables rather than the plan's
six-state combiner; provided leaves are synthetic, NOT Test/Item collection.
"""
from __future__ import annotations
from oval_result_truth_tables import aggregate_operator

OP = {"all": "AND", "any": "OR", "one": "ONE", "odd": "XOR"}
OUTCOMES = frozenset(("true", "false", "error", "unknown",
                      "not_evaluated", "not_applicable"))


def source_expected_outcome(tree, tests, dependencies, *, max_depth=512):
    if not isinstance(tests, dict) or not isinstance(dependencies, dict):
        raise ValueError("source reference requires explicit leaf maps")

    def evaluate(node, depth):
        if depth > max_depth:
            raise ValueError("reference expression depth exceeded")
        if not isinstance(node, dict) or not node:
            raise ValueError("invalid reference expression")
        if set(node) == {"test"}:
            value = tests[node["test"]]
        elif set(node) == {"assessment"}:
            value = dependencies[node["assessment"]]
        elif set(node) == {"not_applicable"}:
            reason = node["not_applicable"].get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise ValueError("missing authored not_applicable reason")
            value = "not_applicable"
        elif set(node) == {"not"}:
            child = evaluate(node["not"], depth + 1)
            value = {"true": "false", "false": "true"}.get(child, child)
        elif len(node) == 1 and next(iter(node)) in OP:
            kind, children = next(iter(node.items()))
            if not isinstance(children, list) or not children:
                raise ValueError("empty reference expression operator")
            outcomes = [evaluate(child, depth + 1).replace("_", " ")
                        for child in children]
            value = aggregate_operator(OP[kind], outcomes).replace(" ", "_")
        else:
            raise ValueError("unapproved expression in independent source oracle")
        if value not in OUTCOMES:
            raise ValueError("invalid reference six-state outcome")
        return value

    return evaluate(tree, 0)
