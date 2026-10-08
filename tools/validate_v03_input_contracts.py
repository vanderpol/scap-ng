#!/usr/bin/env python3
"""Validate authoring-time direct Assessment Input bindings for 0.3.

A policy Parameter supplies *expected State values*, never collection targets,
operation, Test selection, or executable content. This checks declarations,
static bindings and honest discoverability. Runtime authorization/expiry,
per-target evaluation and frozen request provenance are separate concerns.
"""
from __future__ import annotations


def _state_inputs(payload, *, test_id, state_id):
    if not isinstance(payload,dict):
        return
    if isinstance(payload.get("value"),dict) and set(payload["value"])=={"input"}:
        yield (str(test_id),str(state_id),str(payload.get("field")),payload["value"]["input"])
    for name in ("all","any","one","odd"):
        for child in payload.get(name,[]) or []:
            yield from _state_inputs(child,test_id=test_id,state_id=state_id)
    if isinstance(payload.get("not"),dict):
        yield from _state_inputs(payload["not"],test_id=test_id,state_id=state_id)


def _declared_consumers(assessment):
    consumers=[]
    named=assessment.get("states") or {}
    for test_id,test in (assessment.get("tests") or {}).items():
        for idx,ref in enumerate(test.get("states") or []):
            if isinstance(ref,str):
                item=named.get(ref)
                if item is None:
                    raise ValueError(f"{assessment.get('id')}: unresolved named State {ref}")
                state_id=ref
            elif isinstance(ref,dict):
                item=ref
                state_id=f"{test_id}.states[{idx}]"
            else:
                raise ValueError(f"{assessment.get('id')}: invalid State reference")
            payload=item.get("state") if isinstance(item,dict) else None
            consumers.extend(_state_inputs(payload,test_id=test_id,state_id=state_id))
    return consumers


def validate_input_contracts(benchmark,rules,assessments):
    parameters=benchmark.get("parameters") or []
    if not isinstance(parameters,list):
        raise ValueError("Benchmark parameters must be a list")
    param_by_id={}
    for p in parameters:
        if not isinstance(p,dict) or not isinstance(p.get("id"),str):
            raise ValueError("Benchmark Parameter missing id")
        if p["id"] in param_by_id:
            raise ValueError(f"duplicate Benchmark Parameter id {p['id']}")
        param_by_id[p["id"]]=p
    for rid,rule in rules.items():
        declarations=rule.get("organizational_input_requirements") or {}
        for selector,choice in (rule.get("assessment_choices") or {}).items():
            aid=choice.get("assessment")
            if aid not in assessments:
                raise ValueError(f"{rid}/{selector}: unresolved Assessment {aid}")
            assessment=assessments[aid]
            declared_inputs=assessment.get("inputs") or {}
            bindings=choice.get("inputs") or {}
            references=_declared_consumers(assessment)
            seen={(test,state,slot,name) for test,state,slot,name in references}
            for test,state,slot,name in references:
                if not slot or name not in declared_inputs:
                    raise ValueError(f"{rid}/{selector}: undeclared Assessment Input {name} at {test}/{state}/{slot}")
            for name,binding in bindings.items():
                if name not in declared_inputs:
                    raise ValueError(f"{rid}/{selector}: unknown Assessment Input binding {name}")
                parameter=binding if isinstance(binding,str) else binding.get("parameter")
                if parameter not in param_by_id:
                    raise ValueError(f"{rid}/{selector}: missing Benchmark Parameter {parameter}")
                contract=declared_inputs[name]
                declared=param_by_id[parameter]
                if contract.get("datatype")!=declared.get("datatype"):
                    raise ValueError(f"{rid}/{selector}: datatype mismatch for {name} -> {parameter}")
                if contract.get("cardinality")!=declared.get("cardinality"):
                    raise ValueError(f"{rid}/{selector}: cardinality mismatch for {name} -> {parameter}")
                if not any(row[3]==name for row in references):
                    raise ValueError(f"{rid}/{selector}: bound Input {name} has no State consumer")
            for name,contract in declared_inputs.items():
                if contract.get("required") and name not in bindings:
                    raise ValueError(f"{rid}/{selector}: required Assessment Input {name} is unbound")
            expected=[]
            for test,state,slot,name in references:
                if name not in bindings:
                    raise ValueError(f"{rid}/{selector}: Assessment Input {name} has no Parameter binding")
                binding=bindings[name]
                parameter=binding if isinstance(binding,str) else binding["parameter"]
                if param_by_id[parameter].get("resolution")=="organization":
                    expected.append((parameter, bool(declared_inputs[name].get("required")),
                                     test,state,slot))
            published=[]
            for declaration in declarations.get(selector,[]) or []:
                for use in declaration.get("uses",[]) or []:
                    published.append((declaration.get("input"),declaration.get("required"),
                                      use.get("test"),use.get("state"),use.get("state_slot")))
            if sorted(expected)!=sorted(published):
                raise ValueError(f"{rid}/{selector}: Organizational Input discovery locations do not match State consumers")
        unknown=set(declarations)-set(rule.get("assessment_choices") or {})
        if unknown:
            raise ValueError(f"{rid}: input discoverability references undeclared selectors {sorted(unknown)}")
