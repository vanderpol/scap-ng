#!/usr/bin/env python3
"""#237: bounded typed Variable value operators for compiler-owned B fixtures.

Pure value transforms, NEVER execute shell commands or acquire evidence.
OVAL 5.12.3 local_variable multiplicity, regex and missing-value semantics
are NOT verified by this research; do not count as converted Assessments.
"""
from __future__ import annotations
from itertools import product
import re

STATUSES={"values","no_values","unknown","error","not_applicable"}
MAX_VALUES=256
MAX_VALUE_LENGTH=4096
MAX_PATTERN_LENGTH=1024


def values(items=(),status="values"):
    if status not in STATUSES or not isinstance(items,(list,tuple)):
        raise ValueError("invalid source Variable value status/envelope")
    if len(items)>MAX_VALUES or any(type(x) is not str or len(x)>MAX_VALUE_LENGTH for x in items):
        raise ValueError("source Variable values must be bounded typed strings")
    if status=="values" and not items:
        raise ValueError("values status requires at least one value")
    if status!="values" and items:
        raise ValueError("unresolved Variable status cannot carry proven values")
    return {"status":status,"values":list(items)}


def _checked(value):
    if not isinstance(value,dict) or set(value)!={"status","values"}:
        raise ValueError("Variable operand must be typed value envelope")
    return values(value["values"],value["status"])


def capture(variable,pattern):
    source=_checked(variable)
    if source["status"]!="values":return source
    if type(pattern) is not str or not pattern or len(pattern)>MAX_PATTERN_LENGTH:
        return values(status="error")
    try:
        expr=re.compile(pattern)
    except re.error:
        return values(status="error")
    if expr.groups!=1 or expr.groupindex:
        return values(status="error")
    collected=[]
    for item in source["values"]:
        match=expr.search(item)
        if match is None:continue
        value=match.group(1)
        if value is None:return values(status="error")
        if len(value)>MAX_VALUE_LENGTH or len(collected)>=MAX_VALUES:
            return values(status="error")
        collected.append(value)
    return values(collected) if collected else values(status="no_values")


def concat(operands):
    if not isinstance(operands,list) or not operands or len(operands)>64:
        raise ValueError("source concat requires 1..64 typed operands")
    resolved=[_checked(x) for x in operands]
    statuses={r["status"] for r in resolved}
    for bad in ("error","unknown","not_applicable","no_values"):
        if bad in statuses:return values(status=bad)
    quantity=1
    for operand in resolved:
        quantity*=len(operand["values"])
        if quantity>MAX_VALUES:return values(status="error")
    output=[]
    for parts in product(*(operand["values"] for operand in resolved)):
        val="".join(parts)
        if len(val)>MAX_VALUE_LENGTH:return values(status="error")
        output.append(val)
    return values(output)


def unique(variable):
    source=_checked(variable)
    if source["status"]!="values":return source
    # Stable-first ordering is provisional: source OVAL unique semantics
    # need original XML and official Variable operator differential tests.
    seen=set();out=[]
    for value in source["values"]:
        if value not in seen:
            out.append(value)
            seen.add(value)
    return values(out)
