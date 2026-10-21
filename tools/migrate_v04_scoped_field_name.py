#!/usr/bin/env python3
"""Rename only the obsolete 0.4.0 scoped field key without changing semantics.

Official authored name: fields_require, BEFORE the grouped predicates that
inherit it. Collected-Item `require.items`, field overrides, and nested OVAL
record cardinalities are untouched. Rewrites are reversible against the
pinned previous authoring source, not a runtime evaluator.

No implicit AND/OR is introduced: keep the explicit Boolean groups and
leave further optional shorthand until six-state evaluation proof exists.

Refs #248 #239.
"""
from __future__ import annotations

from collections import Counter
from copy import deepcopy

OLD="state_fields_require"
NEW="fields_require"


def _walk(value, counts):
    if isinstance(value, list):
        return [_walk(child,counts) for child in value]
    if not isinstance(value,dict):
        return value
    if OLD in value and NEW in value:
        raise ValueError("Ambiguous mixed old/new 0.4 field-scope requirement")
    converted={}
    if OLD in value:
        # Put the inherited requirement before the predicates it governs.
        converted[NEW]=_walk(value[OLD],counts)
        counts["scoped_field_name_renamed"]+=1
    for key,child in value.items():
        if key!=OLD:
            converted[key]=_walk(child,counts)
    return converted


def _reverse(value):
    if isinstance(value,list):
        return [_reverse(x) for x in value]
    if not isinstance(value,dict):
        return value
    if OLD in value:
        raise ValueError("Former field-scope spelling in generated 0.4 authoring")
    return {OLD if key==NEW else key:_reverse(child) for key,child in value.items()}


def migrate(doc):
    result=deepcopy(doc)
    a=result.get("assessment") if isinstance(result,dict) else None
    counts=Counter()
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return result,counts
    for test_id,test in (a.get("tests") or {}).items():
        if not isinstance(test,dict):
            raise ValueError("Invalid 0.4 Test "+str(test_id))
        a["tests"][test_id]=_walk(test,counts)
    return result,counts


def recover(candidate,old):
    assert_original=deepcopy(candidate)
    a=assert_original.get("assessment") if isinstance(assert_original,dict) else None
    if isinstance(a,dict) and a.get("mode")=="automated":
        for test_id,test in (a.get("tests") or {}).items():
            a["tests"][test_id]=_reverse(test)
    if assert_original != old:
        raise ValueError("Field-scope rename touched original predicate, Test or Object semantics")
    return True


def assert_new_spelling(doc):
    a=doc.get("assessment") if isinstance(doc,dict) else None
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return
    def scan(obj,route):
        if isinstance(obj,dict):
            if OLD in obj:
                raise ValueError(f"Old scoped State-field name in 0.4 authoring at {route}")
            for key,val in obj.items():
                scan(val,route+(key,))
        elif isinstance(obj,list):
            for i,val in enumerate(obj):
                scan(val,route+(i,))
    for testid,test in (a.get("tests") or {}).items():
        scan(test,("tests",testid))
