#!/usr/bin/env python3
"""#227/#235: auditor-first Item requirement language, source exact and fail closed.

This changes ONLY the Item existence + Item matching surface of the proven
English-first compact AST. It preserves selectors, commands, source graphs,
nested records, State field modes, evidence settings, and evaluation trees.

Research candidate, not normative 0.4 or independent OVAL scanner evidence.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from research_english_first_04_complex import to_human,to_native
from research_english_first_04_compact_layout import compact,expand,PINNED
from research_english_first_04_complex import ITEM_REQS,STATELESS_PRESENCE

# The enumerated 10 Item pairs and 5 State-free cases are the admitted source
# semantics. We must not invent defaults, infer regex semantics, or merge axes.
EXIST={
    "at_least_one_item_exists":"at_least_one",
    "items_may_be_absent":"may_be_absent",
    "all_collected_items_exist":"all_must_exist",
    "exactly_one_item_exists":"exactly_one",
}
MATCH={
    "every_item_must_match":"every_item",
    "at_least_one_item_matches":"at_least_one_item",
    "exactly_one_item_matches":"exactly_one_item",
    "no_item_may_match":"no_item",
}
PRESENCE={
    "at_least_one":"at_least_one",
    "exactly_one":"exactly_one",
    "none":"none",
    "all_exist":"all_must_exist",
    "may_be_absent":"may_be_absent",
}
REV_EXIST={v:k for k,v in EXIST.items()}
REV_MATCH={v:k for k,v in MATCH.items()}
REV_PRESENCE={v:k for k,v in PRESENCE.items()}
NATIVE_MATCH_KEYS={
    "every_collected_item":"every_item_must_match",
    "some_collected_item":"at_least_one_item_matches",
    "exactly_one_collected_item":"exactly_one_item_matches",
    "no_collected_item":"no_item_may_match",
}

SUPPORTED_PAIRS={
    (EXIST[e], MATCH[NATIVE_MATCH_KEYS[m]]) for e,m in ITEM_REQS.values()
}
if len(SUPPORTED_PAIRS)!=len(ITEM_REQS):
    raise AssertionError("Item pair vocabulary must remain one-to-one")

def to_auditor_requirement(require):
    if not isinstance(require,dict) or not require:
        raise ValueError("empty Item requirement")
    if set(require)=={"collected_items"}:
        presence=require["collected_items"]
        if presence not in PRESENCE:
            raise ValueError("unsupported State-free presence "+repr(presence))
        return {"items":PRESENCE[presence]}
    if len(require)!=2:
        raise ValueError("requires explicit separate Item existence and matching")
    exist=[k for k in require if k in EXIST]
    match=[k for k in require if k in MATCH]
    if len(exist)!=1 or len(match)!=1 or require[exist[0]] is not True:
        raise ValueError("Item cardinality ambiguity")
    visible=(EXIST[exist[0]],MATCH[match[0]])
    if visible not in SUPPORTED_PAIRS:
        raise ValueError("source-unproven Item pair")
    return {"items":visible[0],visible[1]:deepcopy(require[match[0]])}

def from_auditor_requirement(require):
    if not isinstance(require,dict) or "items" not in require:
        raise ValueError("explicit required Item existence missing")
    exists=require["items"]
    if exists not in REV_PRESENCE:
        raise ValueError("unknown required presence")
    other=set(require)-{"items"}
    if not other:
        return {"collected_items":REV_PRESENCE[exists]}
    if len(other)!=1:
        raise ValueError("exactly one Item matcher required")
    if exists not in REV_EXIST:
        raise ValueError("unsupported Item presence for matcher")
    matcher=next(iter(other))
    if matcher not in REV_MATCH or (exists,matcher) not in SUPPORTED_PAIRS:
        raise ValueError("unproven Item match combination")
    if not isinstance(require[matcher],dict) or not require[matcher]:
        raise ValueError("nonempty State predicate required")
    return {REV_EXIST[exists]:True,REV_MATCH[matcher]:deepcopy(require[matcher])}

def to_auditor(doc):
    if not isinstance(doc,dict) or set(doc)!={"metadata","sources","checks","evaluate"}:
        raise ValueError("invalid whole Assessment")
    out=deepcopy(doc)
    for check in out["checks"].values():
        check["require"]=to_auditor_requirement(check["require"])
    return out

def from_auditor(doc):
    if not isinstance(doc,dict) or set(doc)!={"metadata","sources","checks","evaluate"}:
        raise ValueError("invalid candidate Assessment")
    out=deepcopy(doc)
    for check in out["checks"].values():
        check["require"]=from_auditor_requirement(check["require"])
    return out

SAMPLES={
 "authoring/shared/assessments/linux/other/home-mounted-nosuid-option.assessment.yaml":"linux-home",
 "authoring/shared/assessments/linux/other/initialization-files-0740-less-permissive.assessment.yaml":"linux-files",
 "authoring/ms_windows_11/assessments/automated/SV-253495.automated.yaml":"windows-wmi-rights",
 "authoring/ms_windows_server_dns/assessments/automated/SV-259345.automated.yaml":"dns",
 "authoring/apache_server_2-4_unix_server/assessments/automated/SV-214228.automated.yaml":"apache",
}

def test_invalid():
    wrong=[
       {},{"items":"at_least_one","every_item":{}},
       {"items":"at_least_one","every_item":{"x":1},"at_least_one_item":{"x":2}},
       {"items":"none","every_item":{"x":1}},
       {"items":"foo"},{"items":"may_be_absent","exactly_one_item":{"x":1}},
       {"items":"at_least_one","no_item":{"x":1}},
       {"items":"exactly_one","at_least_one_item":{"x":1}},
       {"items":"at_least_one","every_item":True},
    ]
    for node in wrong:
        try:from_auditor_requirement(node)
        except ValueError:pass
        else:raise AssertionError("invalid Item requirement admitted: "+repr(node))
    return len(wrong)

def inspect(archive,examples_dir=None,output=None):
    if hashlib.sha256(Path(archive).read_bytes()).hexdigest()!=PINNED:
        raise ValueError("pinned source digest changed")
    negatives=test_invalid()
    counts=Counter()
    chars=Counter()
    failures=[]
    samples={}
    if examples_dir:Path(examples_dir).mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("corrupted source archive")
        for path in sorted(z.namelist()):
            if not (path.startswith("authoring/") and "/assessments/" in path and path.endswith(".yaml")):
                continue
            src=(yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if src.get("mode")!="automated" or not src.get("tests"):continue
            counts["total"]+=1
            try:
                previous=compact(to_human(src))
                candidate=to_auditor(previous)
                restored=from_auditor(candidate)
                if restored!=previous or to_native(expand(restored))!=src:
                    raise AssertionError("source AST reconstruction differs")
            except (ValueError,TypeError,KeyError,AssertionError) as e:
                counts["rejected"]+=1
                failures.append({"source":path,"why":str(e)[:200]})
                continue
            counts["exact"]+=1
            counts["tests"]+=len(src["tests"])
            for chk in candidate["checks"].values():
                req=chk["require"]
                counts["presence_"+req["items"]]+=1
                for matching in set(req)-{"items"}:
                    counts["scope_"+matching]+=1
                if list(chk).index("require")<list(chk).index("inspect"):
                    raise AssertionError("State before Object")
            before=yaml.safe_dump(previous,sort_keys=False,allow_unicode=True)
            after=yaml.safe_dump(candidate,sort_keys=False,allow_unicode=True)
            chars["before"]+=len(before)
            chars["candidate"]+=len(after)
            if path in SAMPLES:
                name=SAMPLES[path]
                samples[name]={
                    "source":path,"tests":len(src["tests"]),
                    "original_bytes":len(before),"auditor_bytes":len(after),
                }
                if examples_dir:
                    (Path(examples_dir)/(name+".auditor.research.yaml")).write_text(
                        "# Research-only candidate: lossless native Assessment dictionary, NOT scanner/OVAL runtime parity.\n"+
                        after,encoding="utf-8")
    if counts["total"]!=872 or counts["exact"]!=871 or counts["rejected"]!=1:
        raise AssertionError("unexpected corpus coverage "+repr(counts)+" "+repr(failures[:3]))
    if not failures[0]["source"].endswith("verify-boot-loader-root-admin-adminstrator.assessment.yaml"):
        raise AssertionError("different lossless boundary")
    report={
      "status":"ONE CONSISTENT AUDITOR ITEM REQUIREMENT CANDIDATE; EXACT NATIVE AST INVERSION, NOT SCANNER PARITY",
      "counts":dict(counts),"source_sha256":PINNED,
      "chars":dict(chars),
      "change_pct":round(100*(chars["candidate"]-chars["before"])/chars["before"],2),
      "negative_requirement_guards":negatives,
      "examples":samples,
      "exceptions":failures,
      "limitations":[
        "Not independent SCAP 1.4 six-state scanner/evidence validation.",
        "Source collector, records, Set filters, command/Variable dependencies and field cardinalities are unchanged.",
        "The single none_exist + State source shape remains fail-closed.",
        "Auditor readability must be checked by people; shorter syntax alone does not establish it."
      ],
    }
    if output:Path(output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    p.add_argument("--examples-dir")
    opts=p.parse_args()
    r=inspect(opts.archive,opts.examples_dir,opts.output)
    print(json.dumps(r,indent=2,sort_keys=True))

if __name__=="__main__":main()
