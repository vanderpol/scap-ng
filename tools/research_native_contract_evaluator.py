#!/usr/bin/env python3
"""#235: bounded fixture-only runtime for the one-AST native auditor language.

DOES NOT scan hosts, lower legacy OVAL graphs, implement actual Windows/DNS
providers or establish source parity. Its purpose is to falsify the claim
that named-resource and collection authoring require different evaluation
semantics. The separate OVAL result tables are reused for Boolean AND/OR
only: this does NOT copy legacy item/existence behavior.
"""
from __future__ import annotations
from dataclasses import dataclass
import re
from oval_result_truth_tables import (
    aggregate_operator, evaluate_collected_object_test,
    TRUE, FALSE, ERROR, UNKNOWN, NOT_APPLICABLE)
from research_linux_init_permissions import only_these_bits

STATUSES={"complete","incomplete","error","not collected","not applicable"}
VALUE_STATUS={"absent","unknown","error"}

@dataclass(frozen=True)
class Decision:
    result:str
    reason:str
    provider:str|None=None
    observed:int=0
    selected:int=0
    possible:int=0

def _and(states):
    if not states:return TRUE
    return aggregate_operator("AND",states)

def compare(item,field,operation,desired):
    if "fields" not in item or not isinstance(item["fields"],dict):
        raise ValueError("provider Item must expose fields mapping")
    if field not in item["fields"]:
        return UNKNOWN # unexpected undeclared evidence omission; not known absent
    value=item["fields"][field]
    if isinstance(value,dict) and set(value)=={"field_status"}:
        status=value["field_status"]
        if status not in VALUE_STATUS:raise ValueError("unrecognized field status")
        # Known absence and unreadability differ. A known absent required
        # field does not satisfy an equals/contains/etc property; unreadable
        # evidence prevents determination and is NOT silently filtered out.
        return FALSE if status=="absent" else (ERROR if status=="error" else UNKNOWN)
    if operation=="equals":
        if type(value)!=type(desired):return ERROR
        return TRUE if value==desired else FALSE
    if operation=="not_equals":
        if type(value)!=type(desired):return ERROR
        return TRUE if value!=desired else FALSE
    if operation=="contains":
        if not isinstance(value,(list,tuple)) or any(type(x)!=str for x in value):
            return ERROR
        return TRUE if desired in value else FALSE
    if operation=="at_least":
        if type(value)!=int or type(desired)!=int:
            return ERROR
        return TRUE if value>=desired else FALSE
    if operation=="between":
        if type(value)!=int:
            return ERROR
        return TRUE if desired[0]<=value<=desired[1] else FALSE
    if operation=="only_these_bits":
        try:
            return TRUE if only_these_bits(value,desired) else FALSE
        except ValueError:
            return ERROR
    if operation=="matches_regex":
        if not isinstance(value,str):return ERROR
        return TRUE if re.search(desired,value) else FALSE
    raise ValueError("unregistered native comparison "+str(operation))

def predicates(item,compiled):
    return _and([compare(item,p["field"],p["operator"],p["value"]) for p in compiled])

def evaluate_collection(node,evidence,fixtures,scope=None):
    if not isinstance(evidence,dict):
        raise ValueError("explicit fixture evidence is required")
    flag=evidence.get("status")
    if flag not in STATUSES:
        raise ValueError("provider must declare status")
    if node["using"] and evidence.get("using")!=node["using"]:
        return Decision(ERROR,"missing or mismatched typed acquisition parameters",node["provider"])
    if "using" in evidence and evidence["using"]!=node["using"]:
        return Decision(ERROR,"acquisition parameters do not match evidence",node["provider"])
    if "items" not in evidence:
        return Decision(ERROR,"provider omitted mandatory Items field",node["provider"])
    records=evidence["items"]
    if not isinstance(records,list):
        raise ValueError("items must be list")
    if flag=="error":
        return Decision(ERROR,"provider collection error",node["provider"],len(records))
    if flag=="not collected":
        return Decision(UNKNOWN,"provider not collected",node["provider"],len(records))
    if flag=="not applicable":
        return Decision(NOT_APPLICABLE,"provider not applicable",node["provider"],len(records))

    selected=[]
    unresolved=[]
    ids=set()
    for item in records:
        if not isinstance(item,dict):raise ValueError("Item must be a mapping")
        ident=item.get("id")
        if not isinstance(ident,str) or not ident:
            raise ValueError("stable Item id required")
        if ident in ids:
            return Decision(ERROR,"duplicate evidence Item identity",node["provider"],len(records))
        ids.add(ident)
        selection=predicates(item,node["where"])
        if selection==TRUE:selected.append(item)
        elif selection in {ERROR,UNKNOWN}:
            unresolved.append(selection)
    n=len(selected)
    info=(node["provider"],len(records),n,len(unresolved))
    mode=node["mode"]
    tested=[]
    for item in selected:
        if node.get("nested") is not None:
            local=dict(scope or {})
            local["__current__"]=item
            if node.get("as") is not None:local[node["as"]]=item
            tested.append(evaluate(node["nested"],fixtures,local).result)
        else:
            tested.append(predicates(item,node["predicates"]))
    uncertain=ERROR if ERROR in unresolved+tested else UNKNOWN
    if mode=="none":
        if n:return Decision(FALSE,"selected prohibited Item found",*info)
        if flag=="complete" and not unresolved:
            return Decision(TRUE,"proved no selected prohibited Items",*info)
        return Decision(uncertain,"prohibition not proved from incomplete evidence",*info)

    if mode=="some":
        if TRUE in tested:
            return Decision(TRUE,"compliant witness found",*info)
        if flag=="complete" and not unresolved and all(x==FALSE for x in tested):
            return Decision(FALSE,"no compliant witness exists",*info)
        return Decision(uncertain,"cannot prove witness or its absence",*info)

    if mode=="exactly_one":
        if n>1:
            result=ERROR if node["singleton"] else FALSE
            why="singleton provider violated identity" if node["singleton"] else "more than one selected Item"
            return Decision(result,why,*info)
        if n==1 and tested==[FALSE]:
            return Decision(FALSE,"only possible observed compliant singleton fails",*info)
        if flag=="complete" and not unresolved:
            if n==0:return Decision(FALSE,"required resource is absent",*info)
            return Decision(tested[0],"one selected Item and property evaluated",*info)
        return Decision(uncertain,"unique required resource not resolved",*info)

    if mode!="each":raise ValueError("unknown AST quantifier")
    if FALSE in tested:
        return Decision(FALSE,"a selected Item violates requirement",*info)
    if flag=="complete" and not unresolved and n<node["min_count"]:
        return Decision(FALSE,"selected population is smaller than declared minimum",*info)
    if flag=="complete" and not unresolved and all(x==TRUE for x in tested):
        return Decision(TRUE,"all selected Items meet requirements",*info)
    return Decision(uncertain,"cannot establish a complete compliant selected population",*info)

def evaluate(ast,fixtures,scope=None):
    """Evaluate compiler AST over caller-provided typed evidence fixtures.

    Fixture keys are provider IDs. A real scanner must cache acquisitions by
    provider version + normalized using inputs + target/scope, not just ID.
    This trial intentionally rejects incompatible acquisition parameters
    rather than assuming cached results apply.
    """
    scope=scope or {}
    # INTERNAL COMPILER-OWNED compatibility IR, not authored YAML. This
    # delegates source OVAL Test existence/item truth tables to the PINNED
    # reference combiner. This one node is a bounded bridge demo: it does
    # not execute original command collections, Records, Variables or States.
    if ast["kind"]=="compat_oval_test":
        if "source_test_id" not in ast or not isinstance(ast.get("test"),dict):
            raise ValueError("compatibility IR requires source_test_id and Test inputs")
        source=ast["test"]
        permitted={"flag","existence","check","item_results","has_state",
                   "exists","does_not_exist","error","not_collected"}
        if not {"flag","existence","check","exists"}<=set(source) or set(source)-permitted:
            raise ValueError("compatibility Test has missing or unexpected input fields")
        result=evaluate_collected_object_test(**source)
        return Decision(result,"source-compatible OVAL Test "+ast["source_test_id"])
    if ast["kind"]=="fields":
        selected=scope.get("__current__")
        if selected is None:raise ValueError("fields assertion requires selected Item scope")
        return Decision(predicates(selected,ast["predicates"]),"selected Item fields")
    if ast["kind"]=="logic":
        subs=[evaluate(branch,fixtures,scope) for branch in ast["children"]]
        result=aggregate_operator("AND" if ast["operator"]=="all" else "OR",
                                  [x.result for x in subs])
        return Decision(result,"Boolean "+ast["operator"]+" of "+str(len(subs))+" requirements")
    if ast["kind"]!="collection":
        raise ValueError("unknown compiler AST node")
    if ast.get("parent_ref") is not None:
        ref=ast["parent_ref"]
        owner=scope.get(ref["alias"])
        if owner is None:
            return Decision(ERROR,"dependent source has no bound parent",ast["provider"])
        evidence=owner.get("fields",{}).get(ref["relation"])
        if not isinstance(evidence,dict) or not {"status","items"}<=set(evidence):
            return Decision(UNKNOWN,"dependent resource lacks explicit complete/item evidence",
                            ast["provider"])
        if not isinstance(evidence["items"],list):
            return Decision(ERROR,"dependent resource Items must be a list",ast["provider"])
        for child in evidence["items"]:
            if not isinstance(child,dict) or not isinstance(child.get("fields"),dict):
                return Decision(ERROR,"dependent Item needs identity and typed fields",ast["provider"])
            if child["fields"].get(ast["owner_field"])!=owner.get("id"):
                return Decision(ERROR,"dependent Item attached to wrong parent",ast["provider"])
    else:
        evidence=fixtures.get(ast["provider"])
        if evidence is None:
            return Decision(UNKNOWN,"no fixture acquisition supplied",ast["provider"])
        # Research fixture form for multiple acquisitions from one provider:
        # {"acquisitions":[{"using":{...},"status":"complete","items":[...]},...]}
        # Never let evidence for one registry path/view stand in for another.
        if isinstance(evidence,dict) and "acquisitions" in evidence:
            if set(evidence)!={"acquisitions"} or not isinstance(evidence["acquisitions"],list):
                return Decision(ERROR,"invalid multi-acquisition evidence envelope",ast["provider"])
            if any(not isinstance(x,dict) or "using" not in x
                   for x in evidence["acquisitions"]):
                return Decision(ERROR,"acquisition missing query identity",ast["provider"])
            matches=[x for x in evidence["acquisitions"] if x["using"]==ast["using"]]
            if len(matches)>1:
                return Decision(ERROR,"duplicate acquisition identity",ast["provider"])
            if not matches:
                return Decision(UNKNOWN,"no evidence for requested acquisition identity",ast["provider"])
            evidence=matches[0]
    return evaluate_collection(ast,evidence,fixtures,scope)
