#!/usr/bin/env python3
"""0.4 research-only: explicit Test/group/field requirement scopes, fail closed.

Do not treat this as adopted 0.4 syntax. All before/after rewrites invert
exactly back to current strict 0.4 documents. Native record fields are NOT
covered by scalar field inheritance.
"""
from collections import Counter
from copy import deepcopy
from pathlib import Path
import argparse, json, zipfile

import research_04_rhel9_compact_preview as corpus
from research_04_native_deep_content_census import SIX_ANCHORS,resolve_benchmark_dir,SUPPORTED_MAPPING_DATA
from research_04_one_grammar_proof import make_single,lower_single,normalize_inert_source_checks
from migrate_v04_enum_selectors import migrate,restore

VERBS={"all":"and","any":"or","one":"one","odd":"odd"}
SOURCE={v:k for k,v in VERBS.items()}
SCOPED="state_fields_require"

def parse(states):
    if not isinstance(states,list):raise ValueError("States not list")
    out=[]
    for entry in states:
        if not isinstance(entry,dict) or len(entry)!=1:
            raise ValueError("State node must have exactly one key")
        k,v=next(iter(entry.items()))
        if k in VERBS and isinstance(v,list):
            out.append(("group",k,parse(v)))
        elif isinstance(v,dict):
            if "record" in v:out.append(("record",k,deepcopy(v)))
            elif not isinstance(v.get("require"),str):raise ValueError("Field lacks explicit source require")
            else:out.append(("field",k,deepcopy(v)))
        else:raise ValueError("Unsupported State node")
    return out

def values(nodes):
    for kind,key,val in nodes:
        if kind=="field":yield val["require"]
        if kind=="group":yield from values(val)

def opt(nodes,parent):
    """Minimize explicit declarations; shared logical scope only if a net win."""
    result=[];cost=0;groups=0;overrides=0
    for kind,key,payload in nodes:
        if kind=="record":result.append({key:deepcopy(payload)});continue
        if kind=="field":
            field=deepcopy(payload)
            if field["require"]==parent:field.pop("require")
            else:cost+=1;overrides+=1
            result.append({key:field});continue
        low,entries,g,o=opt(payload,parent)
        choice=(low,entries,None,g,o)
        for scoped in sorted(set(values(payload))):
            if scoped==parent:continue
            candidate,body,ng,no=opt(payload,scoped)
            if 1+candidate<choice[0]:choice=(1+candidate,body,scoped,ng,no)
        count,children,scoped,ng,no=choice
        group={VERBS[key]:children}
        if scoped is not None:group[SCOPED]=scoped;ng+=1
        cost+=count;groups+=ng;overrides+=no
        result.append(group)
    return cost,result,groups,overrides

def compact(doc):
    out=deepcopy(doc);stats=Counter()
    for t in (out.get("assessment",{}).get("tests") or {}).values():
        if not isinstance(t,dict) or not isinstance(t.get("states"),list):continue
        if SCOPED in t:raise ValueError("already scoped")
        tree=parse(t["states"])
        original_fields=sum(1 for _ in values(tree))
        best=(*opt(tree,None),None)
        for root in sorted(set(values(tree))):
            candidate,states,groups,overrides=opt(tree,root)
            if 1+candidate<best[0]:best=(1+candidate,states,groups,overrides,root)
        count,states,groups,overrides,root=best
        t["states"]=states
        if root is not None:t[SCOPED]=root
        stats.update(tests=1,fields=original_fields,requirements_after=count,
                     saved=original_fields-count,group_scopes=groups,
                     field_overrides=overrides,test_scopes=int(root is not None))
    return out,stats

def expand(doc):
    out=deepcopy(doc)
    for name,t in (out.get("assessment",{}).get("tests") or {}).items():
        if not isinstance(t,dict) or not isinstance(t.get("states"),list):continue
        top=t.pop(SCOPED,None)
        if top is not None and (not isinstance(top,str) or not top):
            raise ValueError("Invalid Test scope")
        count=[0]
        def descend(states,parent):
            converted=[]
            for entry in states:
                if not isinstance(entry,dict):raise ValueError("Malformed State entry")
                branches=[k for k,v in entry.items() if k in SOURCE and isinstance(v,list)]
                if branches:
                    if len(branches)!=1 or set(entry)-set(branches)-{SCOPED}:
                        raise ValueError("Invalid logic branch keys")
                    k=branches[0]; sc=entry.get(SCOPED,parent)
                    if SCOPED in entry and (not isinstance(sc,str) or sc==parent):
                        raise ValueError("Redundant or invalid group scope")
                    children=descend(entry[k],sc)
                    if SCOPED in entry and not has_scalar(children):
                        raise ValueError("Unused group scope")
                    converted.append({SOURCE[k]:children})
                    continue
                if len(entry)!=1:raise ValueError("Malformed scalar State node")
                k,v=next(iter(entry.items()))
                if not isinstance(v,dict):raise ValueError("Malformed field")
                leaf=deepcopy(v)
                if "record" in leaf:
                    if "require" in leaf:raise ValueError("Invalid record-wrapper require")
                    converted.append({k:leaf})
                    continue
                if "require" not in leaf:
                    if parent is None:raise ValueError("Hidden default not permitted")
                    leaf["require"]=parent
                elif parent is not None and leaf["require"]==parent:
                    raise ValueError("Redundant same-value field override")
                count[0]+=1
                converted.append({k:leaf})
            return converted
        t["states"]=descend(t["states"],top)
        if top is not None and count[0]==0:raise ValueError("Unused Test field scope")
    return out

def has_scalar(nodes):
    for entry in nodes:
        k,v=next(iter(entry.items()))
        if k in VERBS and isinstance(v,list):
            if has_scalar(v):return True
        elif isinstance(v,dict) and "record" not in v:return True
    return False

def focused_tests():
    requirement="at_least_one_exists_and_all_match"
    absence="none_exist"
    source={"assessment":{"tests":{"shell":{"require":requirement,"states":[{"all":[
        {"exit_status":{"equals":0,"require":requirement}},
        {"stdout_line":{"matches_regex":"ok","require":requirement}},
        {"stderr_line":{"equals":"","require":absence}}
    ]}]}}}}
    shorter,_=compact(source)
    assert expand(shorter)==source
    assert shorter["assessment"]["tests"]["shell"]["states"][0]["and"][2]["stderr_line"]["require"]==absence
    # Test and two alternatives with different requirements.
    source={"assessment":{"tests":{"branches":{"states":[
        {"all":[{"a":{"equals":1,"require":requirement}},{"b":{"equals":1,"require":requirement}}]},
        {"any":[{"c":{"equals":2,"require":absence}},{"d":{"equals":2,"require":absence}}]}
    ]}}}}
    shorter,stats=compact(source)
    assert expand(shorter)==source and stats["saved"]==2
    assert stats["group_scopes"]>=1
    # Actual fields named "and" and "all" remain fields if value is mapping.
    for name in ("all","any","and","or"):
        source={"assessment":{"tests":{"k":{"states":[{name:{"equals":3,"require":requirement}}]}}}}
        assert expand(compact(source)[0])==source
    # Native records are a separate scoped population.
    source={"assessment":{"tests":{"rec":{"states":[{"value":{"record":{
        "require":requirement,"fields":{"productstate":{"equals":7,"require":absence}}
    }}}]}}}}
    assert expand(compact(source)[0])==source
    # Test, group, field missing requirements may never silently default.
    for bad in [
        {"assessment":{"tests":{"a":{"states":[{"a":{"equals":7}}]}}}},
        {"assessment":{"tests":{"a":{"states":[{"and":[{"b":{"equals":8}}]}]}}}},
        {"assessment":{"tests":{"a":{"state_fields_require":requirement,
                      "states":[{"a":{"equals":8,"require":requirement}}]}}}}
    ]:
        try:expand(bad)
        except ValueError:pass
        else:raise AssertionError("Accepted invalid/hidden requirement")

def audit(source_zip,benchmarks):
    result={}
    with zipfile.ZipFile(source_zip) as z:
        if z.testzip() is not None:raise ValueError("Corrupted published source ZIP")
        folders={n.split("/")[1] for n in z.namelist() if
                 n.startswith("authoring/") and "/rules/" in n}
        for benchmark in benchmarks:
            old=corpus.SOURCE_PREFIX
            corpus.SOURCE_PREFIX="authoring/"+resolve_benchmark_dir(folders,benchmark)+"/"
            try:docs,_=corpus.archive_contents(z)
            finally:corpus.SOURCE_PREFIX=old
            total=Counter();examples={}
            for path,old in sorted(docs.items()):
                a=old.get("assessment") if isinstance(old,dict) else None
                if not isinstance(a,dict) or a.get("mode")!="automated":continue
                source,_,notes=make_single(old)
                if lower_single(source)!=normalize_inert_source_checks(old,notes):
                    raise ValueError("0.4 source inversion failure: "+path)
                modern,migrations=migrate(source,SUPPORTED_MAPPING_DATA)
                if restore(modern,migrations)!=source:raise ValueError("Selector inverse failure: "+path)
                reduced,counts=compact(modern)
                if expand(reduced)!=modern:raise ValueError("Scoped inverse failure: "+path)
                if compact(expand(reduced))[0]!=reduced:raise ValueError("Non-idempotent rewrite: "+path)
                total.update(counts);total["assessments"]+=1
                if "SV-253254.automated" in path or "SV-253274.automated" in path:
                    examples[path]=reduced
            result[benchmark]={"counts":dict(total),"examples":examples}
            print(benchmark,json.dumps(dict(total),sort_keys=True),flush=True)
    return result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--six-anchor",action="store_true")
    opts=p.parse_args()
    focused_tests()
    data=audit(opts.source_zip,SIX_ANCHORS if opts.six_anchor else ("rhel_9","windows_11"))
    opts.output.parent.mkdir(parents=True,exist_ok=True)
    opts.output.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
