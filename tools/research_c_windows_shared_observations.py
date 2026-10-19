#!/usr/bin/env python3
"""Refs #245: source-pinned *read-only* C view of complex Windows SV-253495.

Two source Objects supply seven Tests with an OR of two AND branches and an
alternative Test. 0.3 source structural reconstruction and supplied-result
logic only: NO Windows collection, rewritten record evaluator, approval of
new YAML grammar, source semantic upgrade, or scanner parity.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json

SOURCE_ASSESSMENT_ID = "SV-253495.automated"
VIEW_VERSION = "C_WINDOWS_SHARED_OBSERVATION_RESEARCH_V1"
OBSERVATIONS = {
    "system_role": "windows-wmi57-object",
    "denied_remote_logon_trustees": "windows-userright-object",
}
CHECKS = {
    "domain_joined_non_dc": "system-non-dc-domain-joined-windows-server-or-workstation-test",
    "standalone": "system-standalone-windows-server-or-workstation-test",
    "deny_local_accounts": "deny-log-on-through-remote-desktop-services-local-account-test",
    "deny_guests": "deny-log-on-through-remote-desktop-services-guests-test",
    "deny_domain_admins": "deny-log-on-through-remote-desktop-services-domain-admins-test",
    "deny_enterprise_admins": "deny-log-on-through-remote-desktop-services-enterprise-admins-test",
    "deny_everyone": "deny-log-on-through-remote-desktop-services-everyone-test",
}
REVERSE_CHECKS = {source: alias for alias, source in CHECKS.items()}
SOURCE_OPERATORS = {"all": "every", "any": "one_of", "one": "exactly_one", "odd": "odd_count"}
# Narrow proof only. Never silently bless another source version as equivalent.
ROLE_VALUES = {
    "domain_joined_non_dc": ["1", "3"],
    "standalone": ["0", "2"],
}
TRUSTEE_PREDICATES = {
    "deny_local_accounts": ("pattern_match", r"^(?i)(NT Authority\\)?Local account$"),
    "deny_guests": ("case_insensitive_equals", "Guests"),
    "deny_domain_admins": ("pattern_match", r"^(?i)(.+\\)?Domain Admins$"),
    "deny_enterprise_admins": ("pattern_match", r"^(?i)(.+\\)?Enterprise Admins$"),
    "deny_everyone": ("case_insensitive_equals", "Everyone"),
}


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False).encode("utf-8")).hexdigest()


def _assessment(doc):
    if isinstance(doc, dict) and set(doc) == {"assessment"}:
        doc = doc["assessment"]
    if not isinstance(doc, dict) or doc.get("id") != SOURCE_ASSESSMENT_ID or (
        doc.get("specification", {}).get("version") != "0.3.0"
    ):
        raise ValueError("pinned 0.3 source Assessment SV-253495 required")
    if set(doc.get("tests", {})) != set(CHECKS.values()) or (
        set(doc.get("shared_objects", {})) != set(OBSERVATIONS.values()) or
        (doc.get("variables") or {}) or doc.get("mode") != "automated"
    ):
        raise ValueError("source Tests, Objects or Variables differ")
    return doc


def _require_state(test, reference):
    if not isinstance(test, dict) or test.get("object") != reference or (
        test.get("capability") not in ("windows.wmi.query", "windows.userright")
    ) or test.get("existence") != "one_or_more" or (
        test.get("match") not in ("all", "one_or_more")
    ) or test.get("reported_elements") != "all":
        raise ValueError("source Test cardinality/acquisition differs")
    if set(test) - {"capability", "existence", "match", "object",
                    "states", "states_match", "test_title", "reported_elements"}:
        raise ValueError("unreviewed source Test options")
    if reference == OBSERVATIONS["denied_remote_logon_trustees"]:
        if test.get("capability") != "windows.userright" or (
            test.get("match") != "one_or_more"
        ) or len(test.get("states", [])) != 1 or "states_match" in test:
            raise ValueError("unrecognized Trustee Test semantics")
        state = test["states"][0]
        if set(state) != {"field","existence","match","operation","value"} or (
            state["field"] != "trustee_name" or state["existence"] != "one_or_more" or
            state["match"] != "all" or state["operation"] not in
            ("pattern_match","case_insensitive_equals") or type(state["value"]) is not str
        ):
            raise ValueError("Trustee State changed or unsupported")
        return {
            "items": "any_item",
            "same_item_field": "trustee_name",
            "field_values": "at_least_one_exists_and_all_match",
            "predicate": {state["operation"]: state["value"]},
        }
    if test.get("capability") != "windows.wmi.query" or (
        test.get("match") != "all" or test.get("states_match") != "any"
    ) or len(test.get("states", [])) != 2:
        raise ValueError("unrecognized WMI DomainRole source alternatives")
    alternatives = []
    for state in test["states"]:
        try:
            record = state["record"]
            field = record["fields"]["domainrole"]
        except (TypeError, KeyError) as exc:
            raise ValueError("unrecognized nested DomainRole path") from exc
        if set(state) != {"field", "record"} or state["field"] != "result" or (
            set(record) != {"existence", "match", "fields"}
        ) or record["existence"] != "one_or_more" or record["match"] != "all" or (
            set(record["fields"]) != {"domainrole"}
        ) or set(field) != {"existence","match","operation","value"} or (
            field["existence"] != "one_or_more" or field["match"] != "all"
            or field["operation"] != "equals" or type(field["value"]) is not str
        ):
            raise ValueError("nested record existence, field matching or type changed")
        alternatives.append(field["value"])
    return {
        "items": "every_item",
        "record": "result",
        "record_requirement": "at_least_one_exists_and_all_match",
        "field": "domainrole",
        "field_requirement": "at_least_one_exists_and_all_match",
        # These are two WHOLE record States ORed inside EACH Item,
        # not an unproved scalar "some_value_is_in" shortcut.
        "any_record_state_every_value_equals": alternatives,
    }


def _logical_view(node, *, depth=0):
    if depth > 128 or not isinstance(node, dict) or len(node) != 1:
        raise ValueError("unsupported source expression")
    operation, content = next(iter(node.items()))
    if operation == "test":
        if content not in REVERSE_CHECKS:
            raise ValueError("unrecognized source Test")
        return {"check": REVERSE_CHECKS[content]}
    if operation not in SOURCE_OPERATORS or (
        not isinstance(content, list) or len(content) < 2
    ):
        raise ValueError("unsupported expression cardinality/operator")
    return {SOURCE_OPERATORS[operation]: [
        _logical_view(x, depth=depth+1) for x in content
    ]}


def _source_logic(node, *, depth=0):
    if depth > 128 or not isinstance(node, dict) or len(node) != 1:
        raise ValueError("unsupported C expression")
    operation, content = next(iter(node.items()))
    if operation == "check":
        if content not in CHECKS:
            raise ValueError("unrecognized C Test alias")
        return {"test": CHECKS[content]}
    inverse = {v:k for k,v in SOURCE_OPERATORS.items()}
    if operation not in inverse or not isinstance(content, list) or (
        len(content) < 2
    ):
        raise ValueError("unsupported C expression")
    return {inverse[operation]:[_source_logic(n,depth=depth+1) for n in content]}


def present_windows_shared_observations(source):
    """Pinned source exactness, reusable observation aliases, seven check views."""
    a = _assessment(source)
    obs = {}
    for alias, source_id in OBSERVATIONS.items():
        obj = a["shared_objects"][source_id]
        if set(obj) != {"capability","select","object_title"} and (
            set(obj) != {"capability","collect","object_title"}
        ):
            raise ValueError("unsupported collection source shape")
        fields = obj.get("collect", obj.get("select"))
        if not isinstance(fields,dict) or (
            (alias=="system_role" and obj.get("capability")!="windows.wmi.query") or
            (alias=="denied_remote_logon_trustees" and
             obj.get("capability")!="windows.userright")
        ):
            raise ValueError("source collection capability/field invalid")
        obs[alias] = {
            "source_object":source_id,
            "from":{obj["capability"]:deepcopy(fields)},
        }
    checks = {}
    for alias, source_id in CHECKS.items():
        t = a["tests"][source_id]
        reference = t.get("object")
        obs_alias = next((k for k,v in OBSERVATIONS.items() if v==reference),None)
        if obs_alias is None:
            raise ValueError("unknown source observation reference")
        checks[alias] = {
            "on":obs_alias,
            "source_test":source_id,
            "must":_require_state(t, reference),
        }
    require = _logical_view(a.get("evaluate"))
    if require != {
        "one_of": [
            {"every": [{"check":"domain_joined_non_dc"},
                       {"check":"deny_local_accounts"},
                       {"check":"deny_guests"},
                       {"check":"deny_domain_admins"},
                       {"check":"deny_enterprise_admins"}]},
            {"every": [{"check":"standalone"},{"check":"deny_guests"}]},
            {"check":"deny_everyone"},
        ]
    }:
        raise ValueError("source conditional branches differ")
    if any(checks[k]["must"]["any_record_state_every_value_equals"] != values
           for k, values in ROLE_VALUES.items()):
        raise ValueError("pinned DomainRole source alternatives changed")
    if any(next(iter(checks[k]["must"]["predicate"].items())) != predicate
           for k, predicate in TRUSTEE_PREDICATES.items()):
        raise ValueError("pinned trustee source predicate changed")
    if obs["system_role"]["from"] != {"windows.wmi.query": {
        "namespace": r"root\cimv2",
        "query": "SELECT DomainRole FROM win32_computersystem",
    }} or obs["denied_remote_logon_trustees"]["from"] != {
        "windows.userright": {"userright": "SE_DENY_REMOTE_INTERACTIVE_LOGON_NAME"}
    }:
        raise ValueError("pinned source collection selector/query changed")
    return {
        "stage":VIEW_VERSION, "source_assessment":SOURCE_ASSESSMENT_ID,
        "source_sha256":fingerprint(a), "observations":obs,
        "checks":checks, "require":require, "authoring_research_only":True,
        "read_only_source_reconstruction":True, "scanner_executed":False,
    }


def reconstruct_windows_source(view, source):
    """Do not re-author 0.3 source: prove *entire* C view reverse source exact."""
    a = _assessment(source)
    if not isinstance(view,dict) or view != present_windows_shared_observations(a):
        raise ValueError("C projection is not exactly source compatible")
    if _source_logic(view["require"]) != a["evaluate"]:
        raise ValueError("C logic differs from source")
    return deepcopy(a)
