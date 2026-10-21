#!/usr/bin/env python3
"""Lossless explicit expansion of 0.4.0 scoped State-field requirements.

This is a *structural authoring oracle* for independently testing the current
versioned field-scope grammar. A field-level OVAL existence+match requirement
can be inherited from the nearest explicit condition group or Test. This
NEVER changes Test Item existence (require.items), Test result matching
(check/all_items_must), or nested Windows record requirements.

The function does NOT implement field/Item scanner evaluation and therefore
cannot establish OVAL unknown/error/incomplete semantics by itself.

Refs #248 #239 #227.
"""
from __future__ import annotations

from copy import deepcopy

GROUPS=frozenset({"all","any","one","odd","and","or"})


def _expand_entry(entry, inherited, path, field_log):
    if not isinstance(entry, dict) or not entry:
        raise ValueError(f"{path}: expected a nonempty State/condition mapping")
    operators=[key for key in GROUPS if isinstance(entry.get(key),list)]
    if operators:
        if len(operators)!=1 or set(entry)-{operators[0],"state_fields_require"}:
            raise ValueError(f"{path}: malformed or ambiguous logical condition group")
        op=operators[0]
        children=entry[op]
        if not children:
            raise ValueError(f"{path}: logical condition group is empty")
        local=entry.get("state_fields_require",inherited)
        if not local:
            raise ValueError(f"{path}: no explicit State-field requirement in Test/group scope")
        return {op:[_expand_entry(e,local,f"{path}.{op}[{i}]",field_log)
                    for i,e in enumerate(children)]}
    if len(entry)!=1:
        raise ValueError(f"{path}: expected one field predicate or logical group")
    field,value=next(iter(entry.items()))
    if field=="state_fields_require":
        raise ValueError(f"{path}: isolated State-field requirement has no predicates")
    if not isinstance(value,dict):
        raise ValueError(f"{path}.{field}: expected mapping predicate")
    if "record" in value:
        # Record wrapper and each record subfield have their own OVAL
        # cardinality. They MUST NEVER inherit the scalar field scope.
        if set(value)!={"record"} or not isinstance(value["record"],dict):
            raise ValueError(f"{path}.{field}: invalid OVAL record wrapper")
        record=value["record"]
        if "require" not in record or not isinstance(record.get("fields"),dict):
            raise ValueError(f"{path}.{field}: record-level requirement missing")
        if any(not isinstance(f,dict) or "require" not in f
               for f in record["fields"].values()):
            raise ValueError(f"{path}.{field}: nested record field requirement missing")
        field_log.append({"site":f"{path}.{field}","type":"record_independent",
                          "inherited_scalar":False})
        return deepcopy(entry)
    effective=value.get("require",inherited)
    if not effective:
        raise ValueError(f"{path}.{field}: missing explicitly scoped existence/match")
    new=deepcopy(value)
    new["require"]=effective
    field_log.append({"site":f"{path}.{field}",
                      "type":"scalar",
                      "source_scope":"field" if "require" in value else "inherited",
                      "effective_requirement":effective})
    return {field:new}


def expand(test):
    """Expand scoped source authoring to field-explicit, pure 0.4.0 Test.

    The return is (expanded_Test, field_scope_ledger). Test-level group and
    State-group state_fields_require declarations disappear only after
    materializing their values into ALL affected scalar field predicates.
    """
    if not isinstance(test,dict) or "require" not in test:
        raise ValueError("0.4.0 Test must have explicit Item/match requirement")
    new=deepcopy(test)
    scope=new.pop("state_fields_require",None)
    log=[]
    if isinstance(new["require"],dict) and "all_items_must" in new["require"]:
        conditions=new["require"]["all_items_must"]
        if not isinstance(conditions,list) or not conditions:
            raise ValueError("all_items_must must contain at least one condition")
        new["require"]["all_items_must"]=[
            _expand_entry(entry,scope,f"require.all_items_must[{i}]",log)
            for i,entry in enumerate(conditions)]
    if isinstance(new.get("states"),list):
        new["states"]=[
            _expand_entry(entry,scope,f"states[{i}]",log)
            for i,entry in enumerate(new["states"])]
    return new,log


def assert_equivalent(source,expanded):
    actual,ledger=expand(source)
    if actual!=expanded:
        raise ValueError("Expanded State existence/matching or other Test data changed")
    if not ledger and "state_fields_require" in source:
        raise ValueError("Unused explicit field scope is suspicious")
    return {"status":"SCOPED_REQUIRE_SOURCE_EXPLICIT_STRUCTURAL_PARITY",
            "field_sites":len(ledger),
            "inherited_scalar_fields":sum(
                item.get("source_scope")=="inherited" for item in ledger),
            "field_overrides":sum(
                item.get("source_scope")=="field" for item in ledger),
            "record_fields_not_inherited":sum(
                item["type"]=="record_independent" for item in ledger),
            "scanner_six_state_parity":False}
