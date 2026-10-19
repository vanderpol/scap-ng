#!/usr/bin/env python3
"""Refs #245: native 0.4-A Test pieces from source-INDEPENDENT C Windows YAML.

This is a bounded C frontend research compiler, using version-local
0.4.0 capability mappings and the base A test/state schema. It DOES NOT
execute Windows collectors, validate original XML, prove evaluation
semantics or establish the final 0.4-C grammar. No source 0.3 Assessment
document is consumed.
"""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import json

from research_c_require_language import _mapping
from research_c_windows_shared_observations import (
    _source_logic, CHECKS, OBSERVATIONS, ROLE_VALUES, TRUSTEE_PREDICATES
)

ROOT=Path(__file__).resolve().parents[1]
SCHEMA=ROOT/"schema/v0.4.0/assessment-language.schema.json"
PAIRED_ALL="at_least_one_exists_and_all_match"
PAIRED_ANY="at_least_one_exists_and_some_match"
CAPABILITIES={"windows.userright","windows.wmi.query"}
FIELD_OPS={"case_insensitive_equals","pattern_match"}
STAGE="C_RESEARCH_WINDOWS_SHARED_NATIVE_A_TESTS_NOT_SCANNER"

# This backend recognizes ONLY the real SV-253495 source family, not general
# authored WMI/user-right rules. A new query is a valid *new* authored check
# elsewhere, but it must not silently retain these exact source Object/Test IDs.
PINNED_OBSERVATION_FROM = {
    "system_role": {"windows.wmi.query": {
        "namespace": r"root\cimv2",
        "query": "SELECT DomainRole FROM win32_computersystem",
    }},
    "denied_remote_logon_trustees": {"windows.userright": {
        "userright": "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME",
    }},
}
PINNED_REQUIRE = {
    "one_of": [
        {"every": [{"check": "domain_joined_non_dc"},
                   {"check": "deny_local_accounts"},
                   {"check": "deny_guests"},
                   {"check": "deny_domain_admins"},
                   {"check": "deny_enterprise_admins"}]},
        {"every": [{"check": "standalone"}, {"check": "deny_guests"}]},
        {"check": "deny_everyone"},
    ],
}


def compile_native_c_windows(view):
    """Compile *the C authored view itself*, not a pinned original source."""
    if not isinstance(view,dict) or set(view)!={"observations","checks","require"}:
        raise ValueError("C document must have observations, checks and require")
    obs=view["observations"]
    checks=view["checks"]
    if not isinstance(obs,dict) or set(obs)!=set(OBSERVATIONS) or (
        not isinstance(checks,dict) or set(checks)!=set(CHECKS)
    ):
        raise ValueError("unsupported source-independent C Windows composition")
    objects={}
    obs_references={}
    for name, observation in obs.items():
        if not isinstance(observation,dict) or set(observation)!={"source_object","from"}:
            raise ValueError("each observation requires a source ID and from")
        source_id=observation["source_object"]
        frm=observation["from"]
        if type(source_id) is not str or source_id!=OBSERVATIONS[name] or (
            not isinstance(frm,dict) or len(frm)!=1
        ):
            raise ValueError("unknown shared source identity")
        cap, selectors=next(iter(frm.items()))
        if frm != PINNED_OBSERVATION_FROM[name]:
            raise ValueError("pinned Windows source acquisition changed; use a new C assessment for a new query")
        if cap not in CAPABILITIES or not isinstance(selectors,dict):
            raise ValueError("unrecognized native collection capability")
        native=_mapping(cap)
        if cap=="windows.userright":
            alternatives=native["object_selector_alternatives"]
            if not any(set(selectors)==set(a) for a in alternatives) or (
                selectors["userright"] not in native["selector_value_enums"]["userright"]
            ):
                raise ValueError("invalid pinned user-right source selector")
            obj={"capability":cap,
                 "select":{"userright":{"equals":selectors["userright"]}}}
        else:
            params=native["collection_parameters"]
            if set(selectors)!=set(params) or any(
                not isinstance(selectors[k],str) or not selectors[k] or
                len(selectors[k])>4096 for k in params
            ):
                raise ValueError("pinned WMI collection parameters required")
            obj={"capability":cap,"collect":deepcopy(selectors)}
        if source_id in objects:
            raise ValueError("duplicate original source Object ID")
        objects[source_id]=obj
        obs_references[name]={"source_object":source_id,"capability":cap}

    tests={}
    display_checks={}
    for alias, details in checks.items():
        if not isinstance(details,dict) or set(details)!={"observation","source_test","must"}:
            raise ValueError("C checks require explicit observation and Item/State assertions")
        reference=details["observation"]
        test_id=details["source_test"]
        if type(reference) is not str or reference not in obs_references or (
            type(test_id) is not str or not test_id or test_id in tests or
            test_id != CHECKS[alias]
        ):
            raise ValueError("unknown/duplicate source Test or observation")
        source=obs_references[reference]
        must=details["must"]
        if not isinstance(must,dict):
            raise ValueError("C expected Item/State predicates")
        if source["capability"]=="windows.userright":
            if set(must)!={"items","same_item_field","field_values","predicate"} or (
                must["items"]!="any_item" or must["same_item_field"]!="trustee_name" or
                must["field_values"]!=PAIRED_ALL or
                not isinstance(must["predicate"],dict) or
                len(must["predicate"])!=1
            ):
                raise ValueError("unverified user-right field/Item cardinality")
            op,value=next(iter(must["predicate"].items()))
            if op not in FIELD_OPS or type(value) is not str or not value:
                raise ValueError("unsupported original operation/type")
            if reference != "denied_remote_logon_trustees" or (
                alias not in TRUSTEE_PREDICATES or
                (op,value) != TRUSTEE_PREDICATES[alias]
            ):
                raise ValueError("pinned source Trustee predicate or observation changed")
            field="trustee_name"
            native=_mapping("windows.userright")
            if field not in native["state_field_map"].values() or (
                "string" not in native["field_datatypes"][field]
            ):
                raise ValueError("pinned A userright mapping lacks Trustee field")
            aop="matches_regex" if op=="pattern_match" else op
            states=[{field:{"require":PAIRED_ALL,aop:value}}]
            item_require=PAIRED_ANY
            states_match=None
            caveats=["OVAL regex dialect and source case-flag behavior not independently executed"] if op=="pattern_match" else []
        else:
            if set(must)!={"items","record","record_requirement","field",
                          "field_requirement","any_record_state_every_value_equals"} or (
                must["items"]!="every_item" or must["record"]!="result" or
                must["record_requirement"]!=PAIRED_ALL or
                must["field"]!="domainrole" or must["field_requirement"]!=PAIRED_ALL or
                not isinstance(must["any_record_state_every_value_equals"],list) or
                len(must["any_record_state_every_value_equals"])!=2 or
                any(type(x) is not str or not x for x in
                    must["any_record_state_every_value_equals"])
            ):
                raise ValueError("unsupported nested WMI record and Item quantifiers")
            if reference != "system_role" or (
                alias not in ROLE_VALUES or
                must["any_record_state_every_value_equals"] != ROLE_VALUES[alias]
            ):
                raise ValueError("pinned DomainRole source values or observation changed")
            native=_mapping("windows.wmi.query")
            if "result" not in native["record_state_fields"] or (
                native["field_datatypes"]["result"]!=["record"]
            ):
                raise ValueError("pinned WMI record capability differs")
            states=[{"result":{"record":{
                "require":PAIRED_ALL,
                "fields":{"domainrole":{"require":PAIRED_ALL,"equals":value}},
            }}} for value in must["any_record_state_every_value_equals"]]
            item_require=PAIRED_ALL
            states_match="any"
            caveats=["WMI multi-valued record-field semantics and collection parity unverified"]

        test={"capability":source["capability"],"object":source["source_object"],
              "require":item_require,"states":states,"reported_elements":"all"}
        if states_match is not None:test["states_match"]=states_match
        tests[test_id]=test
        display_checks[alias]={"test_id":test_id,"observation":reference,
                               "source_capability":source["capability"],
                               "original_source_parity_verified":False,
                               "caveats":caveats}
    if view["require"] != PINNED_REQUIRE:
        raise ValueError("pinned source AND/OR branches changed")
    expression=_source_logic(view["require"])
    def references(node):
        if isinstance(node,dict):
            if set(node)=={"test"}:return [node["test"]]
            if len(node)==1:return [v for branch in next(iter(node.values())) for v in references(branch)]
        raise ValueError("unsupported expression")
    used=references(expression)
    if set(used)!=set(tests):
        raise ValueError("unreferenced check cannot be silently dropped")
    if len(used)!=len(set(used))+1 or used.count(CHECKS["deny_guests"])!=2:
        # This exact source pattern intentionally reuses the same Guest Test in
        # two branches. Reuse is a *Test truth* reference, not two collections.
        raise ValueError("source Test reuse or logic shape changed")
    return {
        "stage":STAGE,"native_specification":"0.4.0",
        "source_document_required":False,
        "shared_objects":objects,"tests":tests,"evaluate":expression,
        "checks":display_checks,
        "runtime_collectors_implemented":False,
        "original_source_parity_verified":False,
        "scan_result_authoritative":False,
    }
