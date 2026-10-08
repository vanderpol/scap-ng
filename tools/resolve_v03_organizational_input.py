#!/usr/bin/env python3
"""Freeze explicitly selected 0.3 Organizational Input as typed policy values.

This resolves expected-State data, not scanners or collection. Caller must
explicitly supply the Input Set(s) and an aware run-start timestamp. It does
not select an Input Set from file/host/environment metadata and never changes
a Test's operation, collection target, or quantifiers.
"""
from __future__ import annotations

import copy
import datetime as dt
import math


class InputResolutionError(ValueError):
    def __init__(self,code,detail):
        super().__init__(f"{code}: {detail}")
        self.code=code


def _time(value):
    if isinstance(value,dt.datetime):
        moment=value
    else:
        try:
            moment=dt.datetime.fromisoformat(value.replace("Z","+00:00"))
        except (ValueError,TypeError,AttributeError) as exc:
            raise InputResolutionError("invalid_time",str(value)) from exc
    if moment.tzinfo is None or moment.utcoffset() is None:
        raise InputResolutionError("invalid_time","timezone offset required")
    return moment


def _valid_type(value,datatype):
    if datatype=="boolean":
        return type(value) is bool
    if datatype=="integer":
        return type(value) is int
    if datatype in ("float","number"):
        return type(value) in (int,float) and math.isfinite(value)
    if datatype in ("string","version","ipv4","ipv6","path"):
        return type(value) is str
    return False


def _validate_parameter_value(parameter,value):
    name=parameter["id"]
    cardinality=parameter.get("cardinality")
    if cardinality not in ("one","zero_or_one","one_or_more","zero_or_more"):
        raise InputResolutionError("invalid_parameter_cardinality",name)
    if cardinality in ("one","zero_or_one"):
        if value is None and cardinality=="zero_or_one":
            return
        members=[value]
    else:
        if not isinstance(value,list):
            raise InputResolutionError("invalid_cardinality",name)
        members=value
    if cardinality in ("one","one_or_more") and not members:
        raise InputResolutionError("invalid_cardinality",name)
    if any(not _valid_type(item,parameter.get("datatype")) for item in members):
        raise InputResolutionError("invalid_datatype",name)
    constraints=parameter.get("constraints") or {}
    if not isinstance(constraints,dict):
        raise InputResolutionError("invalid_constraints",name)
    if "min_items" in constraints and len(members)<constraints["min_items"]:
        raise InputResolutionError("constraint_min_items",name)
    if "max_items" in constraints and len(members)>constraints["max_items"]:
        raise InputResolutionError("constraint_max_items",name)
    if constraints.get("unique_items") and any(
        item in members[:i] for i,item in enumerate(members)
    ):
        raise InputResolutionError("constraint_unique_items",name)
    if "allowed" in constraints and any(item not in constraints["allowed"] for item in members):
        raise InputResolutionError("constraint_allowed",name)
    if any(isinstance(item,(int,float)) and not isinstance(item,bool)
           and (("minimum" in constraints and item<constraints["minimum"])
                or ("maximum" in constraints and item>constraints["maximum"]))
           for item in members):
        raise InputResolutionError("constraint_range",name)
    if "max_length" in constraints and any(
        isinstance(item,str) and len(item)>constraints["max_length"]
        for item in members
    ):
        raise InputResolutionError("constraint_max_length",name)


def resolve_input_sets(benchmark,selected_input_sets,*,run_start):
    """Return immutable-by-convention deep-copied policy values and provenance.

    Missing required organization Parameters stay unresolved and result in
    structured not_evaluated input readiness, never a default. Invalid,
    duplicate, unapproved, or wrong-Benchmark bindings fail policy resolution.
    """
    if not isinstance(selected_input_sets,list):
        raise InputResolutionError("implicit_input_selection","explicit list required")
    start=_time(run_start)
    identity=benchmark["id"]
    version=benchmark.get("version")
    if isinstance(version,dict):
        version=version.get("value")
    parameters=benchmark.get("parameters") or []
    declared={}
    for entry in parameters:
        name=entry.get("id")
        if not isinstance(name,str) or name in declared:
            raise InputResolutionError("invalid_parameter_identity",name)
        declared[name]=entry
    effective={}
    provenance={}
    unavailable={}
    for entry in selected_input_sets:
        item=entry.get("organizational_input",entry)
        bound=item.get("benchmark") or {}
        if bound.get("id")!=identity or bound.get("version")!=version:
            raise InputResolutionError("wrong_benchmark_input_set",item.get("id"))
        status=(item.get("provenance") or {}).get("authorization_status")
        if status!="approved":
            raise InputResolutionError("unapproved_input",item.get("id"))
        values=item.get("values") or {}
        if not isinstance(values,dict):
            raise InputResolutionError("invalid_input_set_values",item.get("id"))
        after=item.get("effective_from")
        before=item.get("expires_at")
        stale=(after is not None and start<_time(after)) or (
            before is not None and start>=_time(before))
        for param_id,value in values.items():
            contract=declared.get(param_id)
            if contract is None:
                raise InputResolutionError("unknown_parameter",param_id)
            if contract.get("resolution")!="organization":
                raise InputResolutionError("publisher_parameter_override",param_id)
            if param_id in effective or param_id in unavailable:
                raise InputResolutionError("ambiguous_input",param_id)
            if stale:
                unavailable[param_id]="expired_or_not_yet_effective_input"
                continue
            _validate_parameter_value(contract,value)
            effective[param_id]=copy.deepcopy(value)
            provenance[param_id]={
                "input_set_id":item.get("id"),
                "input_set_version":item.get("version"),
                "supplied":copy.deepcopy(item.get("provenance")),
                "parameter_provenance":copy.deepcopy(
                    (item.get("value_provenance") or {}).get(param_id)),
            }
    missing=[]
    for name,decl in declared.items():
        if (decl.get("resolution")=="organization" and decl.get("required")
            and name not in effective):
            missing.append({"parameter":name,"code":unavailable.get(name,"missing_organizational_input")})
    return {
        "benchmark":{"id":identity,"version":version},
        "run_start":start.isoformat(),
        "effective_values":effective,
        "value_provenance":provenance,
        "readiness":{
            "outcome":"not_evaluated" if missing else "ready",
            "unresolved_parameters":missing,
        },
    }


def bind_assessment_inputs(rule,selector,assessment,policy_context):
    """Project already-frozen Benchmark values into one selected Assessment."""
    choice=(rule.get("assessment_choices") or {}).get(selector)
    if choice is None or choice.get("assessment")!=assessment.get("id"):
        raise InputResolutionError("invalid_assessment_choice",selector)
    values=policy_context["effective_values"]
    bound={}
    missing=[]
    for name,contract in (assessment.get("inputs") or {}).items():
        assignment=(choice.get("inputs") or {}).get(name)
        param_id=assignment if isinstance(assignment,str) else (
            assignment or {}).get("parameter")
        if not param_id:
            if contract.get("required"):
                raise InputResolutionError("unbound_assessment_input",name)
            continue
        if param_id not in values:
            if contract.get("required"):
                missing.append({"input":name,"parameter":param_id,
                                "code":"missing_organizational_input"})
            continue
        bound[name]=copy.deepcopy(values[param_id])
    return {
        "outcome":"not_evaluated" if missing else "ready",
        "reason":{"code":"missing_organizational_input","unresolved":missing}
            if missing else None,
        "bindings":bound,
        "frozen":True,
    }
