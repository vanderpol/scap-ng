#!/usr/bin/env python3
"""Refs #245: source-backed single-consumer Variable authoring-view eligibility.

Read-only scope audit. Even eligible nodes are NOT automatically rewritten;
all native A Variables, statuses and source identities remain in the IR.
"""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from research_c_shared_engine import present_c_variable_steps, fingerprint
from v04_a_dataflow_index import index_assessment_dataflow

def _use_paths(node,path=()):
    if isinstance(node,dict):
        if set(node)=={"use"}:
            yield (node["use"],path+("use",))
        else:
            for key,value in node.items():
                yield from _use_paths(value,path+(key,))
    elif isinstance(node,list):
        for i,value in enumerate(node):
            yield from _use_paths(value,path+(i,))

def candidate_single_use_value_steps(assessment):
    view=present_c_variable_steps(assessment)
    graph=index_assessment_dataflow(assessment)
    steps={s["name"]:s for s in view["steps"]}
    to_alias={s["source_id"]:s["name"] for s in view["steps"]}
    consumers={name:[] for name in steps}
    for consumer_alias,step in steps.items():
        for target,path in _use_paths(step["derive"]):
            if target not in steps:
                raise ValueError("unresolved derived-value reference")
            consumers[target].append({"kind":"value","by":consumer_alias,"path":list(path),
                    "inside_acquisition":any(k in path for k in (
                        "object","collect","select","read_field"))})
    for edge in graph["edges"]:
        if edge["to_kind"]=="variable" and edge["from_kind"]!="variable":
            ident=edge["to_id"]
            if ident not in to_alias:
                raise ValueError("unresolved source Variable consumer")
            consumers[to_alias[ident]].append({"kind":edge["from_kind"],
                  "by":edge["from_id"],"path":deepcopy(edge["path"]),
                  "inside_acquisition":edge["from_kind"]=="object"})
    # Independently account for every A Variable-to-Variable reference site.
    actual=Counter((edge["from_id"],edge["to_id"]) for edge in graph["edges"]
                   if edge["from_kind"]=="variable" and edge["to_kind"]=="variable")
    in_c=Counter((steps[item["by"]]["source_id"],steps[alias]["source_id"])
                 for alias,refs in consumers.items() for item in refs
                 if item["kind"]=="value")
    if actual!=in_c:
        raise ValueError("C reference paths differ from A source dependency graph")
    summary=[]
    for step in view["steps"]:
        refs=consumers[step["name"]]
        # Value use inside a collector cannot be treated as a simple,
        # evaluation-only, nested transform even with one consumer.
        safe=(len(refs)==1 and refs[0]["kind"]=="value" and
              not refs[0]["inside_acquisition"])
        reason=("PURE_SINGLE_VALUE_CONSUMER" if safe else
                "REUSED_VALUE" if len(refs)>1 else
                "TEST_OR_SHARED_ACQUISITION" if refs and refs[0]["kind"]!="value" else
                "DYNAMIC_ACQUISITION_CONSUMER" if refs and refs[0]["inside_acquisition"] else
                "UNUSED_SOURCE_NODE")
        summary.append({"source_id":step["source_id"],"display_name":step["name"],
                        "source_title":step["title"],
                        "consumer_count":len(refs),"consumers":refs,
                        "presentation_grouping_candidate":safe,"reason":reason,
                        "native_source_node_must_remain":True})
    return {"stage":"C_RESEARCH_SINGLE_USE_VALUE_PRESENTATION_CENSUS",
            "source_assessment_id":assessment["id"],
            "source_variables_sha256":fingerprint(assessment["variables"]),
            "source_graph_sha256":fingerprint(graph),
            "named_variable_count":len(summary),
            "presentation_group_candidates":sum(c["presentation_grouping_candidate"]
                                               for c in summary),
            "candidates":summary,"actual_native_variables_removed":0,
            "automatic_inline_or_migration_authorized":False,
            "oval_runtime_parity_proven":False}
