#!/usr/bin/env python3
"""Issue #235: synthetic source-independent evidence evaluation for authoring research.

NOT a native scanner, completed provider, general six-state evaluator, source
converter, or equivalence proof for migrated SCAP 1.4 / OVAL material.
"""
from __future__ import annotations
from dataclasses import dataclass

PASS="true"
FAIL="false"
ERROR="error"
UNKNOWN="unknown"
COMPLETE="complete"
INCOMPLETE="incomplete"

@dataclass(frozen=True)
class Result:
    verdict: str
    reason: str
    observed: int
    selected: int
    possible_matches: int

def field_value(item,name):
    fields=item["fields"]
    if name not in fields: return UNKNOWN,None
    val=fields[name]
    if isinstance(val,dict) and set(val)=={"field_status"}:
        if val["field_status"]=="error":return ERROR,None
        if val["field_status"] in {"absent","unknown"}:return UNKNOWN,None
        raise ValueError("unsupported field status")
    return PASS,val

def compare(item,field,assertion):
    status,value=field_value(item,field)
    if status!=PASS:return status
    if not isinstance(assertion,dict) or len(assertion)!=1:
        raise ValueError("comparison must have one operator")
    op,expected=next(iter(assertion.items()))
    if op=="equals":
        return PASS if type(value)==type(expected) and value==expected else FAIL
    if op=="contains":
        if not isinstance(value,(list,tuple)):
            raise ValueError("contains requires a fully collected list")
        return PASS if expected in value else FAIL
    if op=="between":
        if not isinstance(value,(int,float)) or isinstance(value,bool):
            raise ValueError("between requires typed numeric value")
        if not isinstance(expected,list) or len(expected)!=2 or not all(
            isinstance(x,(int,float)) and not isinstance(x,bool) for x in expected):
            raise ValueError("between needs two typed numeric bounds")
        return PASS if expected[0]<=value<=expected[1] else FAIL
    raise ValueError("unsupported comparison operator "+str(op))

def matches(item,predicates):
    if not isinstance(predicates,dict):raise ValueError("predicates must be a mapping")
    statuses=[compare(item,k,v) for k,v in predicates.items()]
    if FAIL in statuses:return FAIL
    if ERROR in statuses:return ERROR
    if UNKNOWN in statuses:return UNKNOWN
    return PASS

def uncertain(sources,checks):
    return ERROR if ERROR in sources or ERROR in checks else UNKNOWN

def evaluate(collection, *, where, must=None, mode="each",minimum_resources=0,singleton=False):
    """Evaluate fully specified in-memory evidence, not actual host values.

    each: all selected must comply, selected count is compared with minimum.
    none: no selected resources; never an overloaded field predicate.
    some: at least one selected Item proves a matching property.
    exactly_one: exactly one SELECTED Item, also compliant. Does not count
                 only the compliant subset.
    singleton: simulate unique-resource provider promise; a duplicate is a
               provider integrity error rather than a policy failure.

    An incomplete population cannot establish an empty selection. Observed
    definitive violations can still settle a result. Missing/unreadable
    selectors are not silently discarded. Unknown/error are provisional
    states, not full OVAL 5.12.3 results or scanner parity.
    """
    status=collection.get("status")
    if status not in {"complete","incomplete","error","not collected","not applicable"}:
        raise ValueError("explicit valid collection status required")
    items=collection.get("items",[])
    if not isinstance(items,list):raise ValueError("items must be a list")
    if status=="error":return Result(ERROR,"provider acquisition failed",len(items),0,0)
    if status=="not collected":return Result(UNKNOWN,"provider did not collect",len(items),0,0)
    if status=="not applicable":
        return Result("not applicable","provider not applicable",len(items),0,0)
    if mode not in {"each","some","none","exactly_one"}:
        raise ValueError("unsupported quantifier")
    if not isinstance(minimum_resources,int) or isinstance(minimum_resources,bool) or minimum_resources<0:
        raise ValueError("invalid minimum_resources")
    if minimum_resources and mode!="each":
        raise ValueError("minimum_resources only for each")
    if singleton and mode!="exactly_one":raise ValueError("singleton requires exactly_one")
    if mode=="none":
        if must is not None:raise ValueError("none forbids must")
    elif not isinstance(must,dict):
        raise ValueError("must required")

    selected=[]
    unresolved=[]
    identifiers=set()
    for item in items:
        ident=item.get("id")
        if not isinstance(ident,str) or not ident:
            raise ValueError("each evidence Item requires stable id")
        if ident in identifiers:
            return Result(ERROR,"duplicate Item identity",len(items),len(selected),len(unresolved))
        identifiers.add(ident)
        answer=matches(item,where)
        if answer==PASS:selected.append(item)
        elif answer in {UNKNOWN,ERROR}:unresolved.append(answer)
    n=len(selected)
    checked=[matches(item,must) for item in selected] if must is not None else []
    data=(len(items),n,len(unresolved))

    if mode=="none":
        if n:return Result(FAIL,"known selected Item exists",*data)
        if status=="complete" and not unresolved:
            return Result(PASS,"confirmed zero selected Items",*data)
        return Result(uncertain(unresolved,[]),"selection incomplete",*data)

    if mode=="some":
        if PASS in checked:return Result(PASS,"known satisfying Item",*data)
        if status=="complete" and not unresolved and all(x==FAIL for x in checked):
            return Result(FAIL,"no Item satisfies condition",*data)
        return Result(uncertain(unresolved,checked),"no decisive witness yet",*data)

    if mode=="exactly_one":
        if n>1 and singleton:return Result(ERROR,"singleton provider violated uniqueness",*data)
        if n>1:return Result(FAIL,"more than one selected Item",*data)
        if n==1 and checked[0]==FAIL:
            return Result(FAIL,"sole observed candidate fails; others cannot rescue exact-one",*data)
        if status=="complete" and not unresolved:
            if n==0:return Result(FAIL,"zero selected Items",*data)
            return Result(checked[0],"one selected Item; property evaluated",*data)
        return Result(uncertain(unresolved,checked),"exact selected count unresolved",*data)

    if FAIL in checked:
        return Result(FAIL,"known selected Item violates requirement",*data)
    if status=="complete" and not unresolved and n<minimum_resources:
        return Result(FAIL,"selected population below declared minimum",*data)
    if status=="complete" and not unresolved and all(x==PASS for x in checked):
        return Result(PASS,"all selected Items comply and minimum met",*data)
    return Result(uncertain(unresolved,checked),"cannot establish all-compliant complete selection",*data)

def population(status,*items):
    return {"status":status,"items":list(items)}

def mount(ident,options=None,path="/home"):
    return {"id":ident,"fields":{"mount_point":path,"mount_options":options or ["rw"]}}
