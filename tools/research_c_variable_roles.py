#!/usr/bin/env python3
"""#245 Evidence-backed roles for OVAL-compatible Variables in 0.4-C.

Separate VALUE ORIGIN from VALUE USE. In particular, a runtime-derived value
can parameterize subsequent observation collection and also be compared by a
Test; such values cannot automatically be split into two independent variables.
Organization-approved policy data is NOT a local OVAL derived Variable.

This is a lossless, read-only census of the A-compatible dataflow graph. It
does not propose, execute or authorize a new parser/scanner construct.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy

from v04_a_dataflow_index import index_assessment_dataflow
from research_c_shared_engine import fingerprint

KNOWN_KINDS=frozenset(("local","constant","external"))
KNOWN_USE_ROLES=frozenset((
    "acquisition_parameter",
    "population_filter",
    "assertion_expected_value",
    "value_transformation",
    "other_object_dependency",
    "other_test_dependency",
))

def _context(edge):
    path=edge["path"]
    if "filters" in path:
        return "population_filter"
    if "collect" in path or "select" in path or "for_each" in path:
        return "acquisition_parameter"
    if "states" in path or "state" in path or "predicate" in path:
        return "assertion_expected_value"
    if edge["from_kind"]=="variable":
        return "value_transformation"
    if edge["from_kind"]=="object":
        return "other_object_dependency"
    if edge["from_kind"]=="test":
        return "other_test_dependency"
    raise ValueError("unexpected source Variable consumer: "+str(edge))

def audit_value_roles(assessment):
    if not isinstance(assessment,dict) or assessment.get("mode")!="automated":
        raise ValueError("automated A-compatible Assessment required")
    variables=assessment.get("variables") or {}
    if not isinstance(variables,dict):
        raise ValueError("named source Variables mapping required")
    graph=index_assessment_dataflow(assessment)
    edges={name:[] for name in variables}
    for edge in graph["edges"]:
        if edge["to_kind"]!="variable":
            continue
        name=edge["to_id"]
        if name not in edges:
            raise ValueError("unknown incoming Variable identity")
        edges[name].append({"consumer_kind":edge["from_kind"],
                            "consumer_id":edge["from_id"],
                            "role":_context(edge),
                            "path":deepcopy(edge["path"])})
    rows=[]
    summary=Counter()
    for name,var in sorted(variables.items()):
        kind=var.get("kind")
        if kind not in KNOWN_KINDS:
            raise ValueError("unknown source Variable origin; do not guess")
        incoming=edges[name]
        roles=sorted(set(edge["role"] for edge in incoming))
        if any(x not in KNOWN_USE_ROLES for x in roles):
            raise ValueError("unknown source Variable consumer context")
        origin={"local":"system_derived","constant":"publisher_literal",
                "external":"external_oval_value_not_automatically_organizational_policy"}[kind]
        scope=("reused_across_uses" if len(incoming)>1 else
               "one_use" if incoming else "no_direct_named_use")
        summary["origin_"+origin]+=1
        for role in roles:
            summary["used_"+role]+=1
        if "acquisition_parameter" in roles and (
            "assertion_expected_value" in roles or
            "population_filter" in roles):
            summary["mixed_acquisition_and_evaluation"]+=1
        rows.append({
            "source_variable_id":name,
            "source_title":var.get("title",var.get("variable_title")),
            "origin":origin,
            "datatype":var.get("datatype"),
            "consumer_roles":roles,"direct_consumer_count":len(incoming),
            "source_consumers":incoming,"reuse_scope":scope,
            "can_auto_remove_or_duplicate":False,
        })
    return {"stage":"C_RESEARCH_VARIABLE_ORIGIN_USE_SEPARATION_NOT_NEW_LANGUAGE",
            "source_assessment_id":assessment["id"],
            "source_variables_sha256":fingerprint(variables),
            "source_dataflow_sha256":fingerprint(graph),
            "variable_count":len(rows),
            "role_summary":dict(sorted(summary.items())),
            "roles":rows,
            "source_unchanged":True,
            "scanner_executed":False,
            "C_language_decision_made":False,
            "source_semantic_parity_proven":False}
