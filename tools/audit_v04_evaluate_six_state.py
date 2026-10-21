#!/usr/bin/env python3
"""Independent six-state differential for 0.4 evaluate ALL/ANY/ODD -> AND/OR/XOR.

Run on two full six-STIG authoring archives: the source-normalized 0.4
AND/OR-State candidate and the separately generated Test-result logical
candidate. Only assessment.evaluate may change; all other Assessment,
Test, Object, State, Set, Filter, Variable, and Item requirements must be
identical. Evaluation uses original OVAL 5.12.3 result tables for the old
operator names and a separate candidate logical model for the new ones.

IF/THEN/ELSE branch semantics are not independently validated here:
we verify expressions under deterministic proposed 'true chooses then;
otherwise else' traversal, and report the limitation. Actual scanner
execution remains unproven.

Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile

from oval_result_truth_tables import aggregate_operator
from research_v04_oval_logic_scopes import candidate_logic,RESULTS

OLD={"all":"AND","any":"OR","one":"ONE","odd":"XOR"}
NEW={"and","or","one","xor"}


def _error(msg):
    raise ValueError("OVAL evaluate six-state differential: "+msg)


def _read(path):
    with ZipFile(path) as z:
        data={}
        for file in z.namelist():
            if file.endswith(".json") and file.startswith("authoring/"):
                if file in data:
                    _error("duplicate archive document: "+file)
                data[file]=json.loads(z.read(file))
    if len(data)!=4001:
        _error("expected 4,001 source documents, got "+str(len(data)))
    return data


def _leaves(expr, keys):
    if not isinstance(expr,dict) or not expr:
        _error("empty or malformed Test-result expression")
    if set(expr)=={"test"}:
        keys.add("test:"+expr["test"])
    elif set(expr)=={"assessment"}:
        keys.add("assessment:"+expr["assessment"])
    elif set(expr)=={"not_applicable"}:
        pass
    elif set(expr)=={"not"}:
        _leaves(expr["not"],keys)
    elif set(expr)=={"if","then","else"}:
        for key in ("if","then","else"):
            _leaves(expr[key],keys)
    elif len(expr)==1:
        op,children=next(iter(expr.items()))
        if op not in {*OLD,*NEW} or not isinstance(children,list) or not children:
            _error("unsupported aggregate expression "+str(op))
        for child in children:
            _leaves(child,keys)
    else:
        _error("ambiguous logical expression with multiple keys")


def _not(value):
    return {"true":"false","false":"true"}.get(value,value)


def evaluate(expr,values,*,candidate=False):
    keys=set(expr)
    if keys=={"test"}:
        return values["test:"+expr["test"]]
    if keys=={"assessment"}:
        return values["assessment:"+expr["assessment"]]
    if keys=={"not_applicable"}:
        return "not applicable"
    if keys=={"not"}:
        return _not(evaluate(expr["not"],values,candidate=candidate))
    if keys=={"if","then","else"}:
        criterion=evaluate(expr["if"],values,candidate=candidate)
        key="then" if criterion=="true" else "else"
        return evaluate(expr[key],values,candidate=candidate)
    if len(expr)!=1:
        _error("invalid Boolean aggregate expression")
    op,children=next(iter(expr.items()))
    if not isinstance(children,list) or not children:
        _error("Boolean expression has no operands")
    result=[evaluate(x,values,candidate=candidate) for x in children]
    if candidate:
        if op not in NEW:
            _error("candidate retained obsolete logical operator: "+op)
        return candidate_logic(op,result)
    if op not in OLD:
        _error("original source has new logical operator: "+op)
    return aggregate_operator(OLD[op],result)


def vector_matrix(keys):
    """Bounded deterministic six-state vectors, no probabilistic sampling."""
    keys=sorted(keys)
    statuses=tuple(sorted(RESULTS))
    seen=set()
    cases=[]
    def add(mapping):
        key=tuple(mapping[k] for k in keys)
        if key not in seen:
            seen.add(key)
            cases.append(mapping)
    for status in statuses:
        add({k:status for k in keys})
    for base in ("true","false","unknown","not applicable"):
        for name in keys:
            for state in statuses:
                values={k:base for k in keys}
                values[name]=state
                add(values)
    # Preserve pairwise mismatched truth/Error propagation for up to 6
    # distinct leaves, then bounded but deterministic coverage for more.
    for i,left in enumerate(keys[:6]):
        for right in keys[i+1:6]:
            for a,b in (("true","false"),("false","true"),
                        ("true","error"),("false","unknown"),
                        ("not evaluated","error"),("unknown","not applicable")):
                values={k:"false" for k in keys}
                values[left],values[right]=a,b
                add(values)
    return cases


def compare(source,rewritten):
    a=source.get("assessment")
    b=rewritten.get("assessment")
    if not isinstance(a,dict) or not isinstance(b,dict):
        if source!=rewritten:
            _error("non-Assessment authoring content changed")
        return None
    if a.get("mode")!="automated":
        if source!=rewritten:
            _error("manual Assessment changed")
        return None
    if not isinstance(a.get("evaluate"),dict) or not isinstance(b.get("evaluate"),dict):
        _error("automated Assessment missing evaluation expression")
    x=deepcopy(source)
    y=deepcopy(rewritten)
    x["assessment"].pop("evaluate")
    y["assessment"].pop("evaluate")
    if x!=y:
        _error("changed non-evaluate Test/Item/State fields in "+str(a.get("id")))
    left,right=a["evaluate"],b["evaluate"]
    original_leaves,new_leaves=set(),set()
    _leaves(left,original_leaves)
    _leaves(right,new_leaves)
    if original_leaves!=new_leaves:
        _error("source Test/Assessment operands lost or invented")
    vector_count=0
    for values in vector_matrix(original_leaves):
        old_value=evaluate(left,values)
        new_value=evaluate(right,values,candidate=True)
        vector_count+=1
        if old_value!=new_value:
            _error("six-state result mismatch in "+str(a.get("id"))+
                   ": "+str(values)+" produced "+old_value+" vs "+new_value)
    if left!=right:
        return {"assessment_id":a.get("id"),
                "vectors":vector_count,
                "source_evaluate_sha256":sha256(json.dumps(left,sort_keys=True).encode()).hexdigest(),
                "new_evaluate_sha256":sha256(json.dumps(right,sort_keys=True).encode()).hexdigest(),
                "conditional_present":"if" in json.dumps(left)}
    return None


def audit(original_path,candidate_path):
    source=_read(original_path)
    after=_read(candidate_path)
    if set(source)!=set(after):
        _error("lost or added authoring paths in new candidate")
    changed=[]
    totals=Counter()
    for name in sorted(source):
        result=compare(source[name],after[name])
        if result is not None:
            changed.append({"path":name,**result})
            totals["changed_documents"]+=1
            totals["tested_vectors"]+=result["vectors"]
            if result["conditional_present"]:
                totals["conditional_expressions"]+=1
    if not changed:
        _error("no Test-result Boolean expression changes were found")
    if totals["conditional_expressions"]:
        # Conditional/IF axes are preserved structurally, but this
        # truth-vector model is a candidate traversal, not scanner parity.
        pass
    return {
        "status":"SIX_STATE_EVALUATE_OPERATOR_PARITY_PASS_SCANNER_OPEN",
        "documents":len(source),"changed_documents":len(changed),
        "total_deterministic_six_state_vectors":totals["tested_vectors"],
        "conditional_expressions":totals["conditional_expressions"],
        "changes":changed,
        "no_changes_outside_evaluate":True,
        "state_and_item_cardinalities_unchanged":True,
        "schema_promoted":False,"scanner_executed":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--candidate-zip",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    args=p.parse_args()
    report=audit(args.source_zip,args.candidate_zip)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(report,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="changes"},
                    indent=2,sort_keys=True))


if __name__=="__main__":
    main()
