#!/usr/bin/env python3
"""#245 C absence claim through already-implemented source WMI compatibility.

No new WMI collector, query optimizer, scanner, or approval of WMI in native
0.4-A supported mappings. Proven only with source-pinned converted 0.3
fixture and normalized offline Items.
"""
from __future__ import annotations

from copy import deepcopy

from research_b_source_wmi_lowering import lower_state_free_wmi_assessment
from research_b_wmi_query_snapshot import PROVIDER,VERSION
from research_c_common_evaluation import population_outcome
from research_c_shared_engine import fingerprint


def lower_c_wmi_absence(requirement,source):
    if not isinstance(requirement,dict) or set(requirement)!={"from","must"} or (
        requirement["must"]!="absent"
    ):
        raise ValueError("state-free WMI C check requires an explicit absent clause")
    f=requirement["from"]
    if not isinstance(f,dict) or set(f)!={PROVIDER} or (
        not isinstance(f[PROVIDER],dict) or
        set(f[PROVIDER])!={"namespace","query"}
    ):
        raise ValueError("WMI requires an original named namespace and query")
    backend=lower_state_free_wmi_assessment(source)
    if backend["provider"]!=PROVIDER or backend["using"]!=f[PROVIDER] or (
        backend["existence"]!="none_exist"
    ):
        raise ValueError("C WMI expression changes original collection/existence semantics")
    return {
        "kind":"c-research-wmi-source-compat-absence",
        "source_sha256":fingerprint(source["assessment"]),
        "compatibility":deepcopy(backend),
        "source_parity_verified":False,
        "scanner_executed":False,
    }


def evaluate_c_wmi_absence(plan,evidence):
    if plan.get("kind")!="c-research-wmi-source-compat-absence" or (
        plan.get("source_parity_verified") is not False
    ):
        raise ValueError("unknown C source-compatibility plan")
    backend=plan["compatibility"]
    if evidence is None:return "unknown"
    if not isinstance(evidence,dict) or evidence.get("provider")!=PROVIDER or (
        evidence.get("version")!=VERSION or
        evidence.get("using")!=backend["using"]
    ):
        return "error"
    status=evidence.get("status")
    mapping={"not collected":"not_collected","not applicable":"not_applicable",
             "complete":"complete","incomplete":"incomplete","error":"error"}
    if status not in mapping:return "error"
    items=evidence.get("items")
    if not isinstance(items,list):return "error"
    seen=set()
    identities=[]
    for item in items:
        if not isinstance(item,dict) or set(item)!={"id","fields"} or (
            type(item["id"]) is not str or not item["id"] or item["id"] in seen or
            not isinstance(item["fields"],dict) or not item["fields"]
        ):
            return "error"
        seen.add(item["id"])
        identities.append({"id":item["id"]})
    adapted={"capability":PROVIDER,"status":mapping[status],
             "items":identities,"does_not_exist":0,"error":0,"not_collected":0}
    return population_outcome(
        {"exists":"none_exist","items_match":"every","has_state":False},adapted)
