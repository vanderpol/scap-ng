#!/usr/bin/env python3
"""Issue #235/#229: read-only forensic census of Test all_exist intent.

Use the immutable six-STIG YAML archive. Do not normalize source Tests.
Report selector shape, fixed vs discovered populations, repeated mode choices,
and exact source-shape contrasts. No collector/scanner equivalence claimed.
"""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from collections import Counter, defaultdict
from pathlib import Path
import yaml

PINNED="03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
COMPARATORS={"equals","case_insensitive_equals","matches_regex",
             "greater_than","greater_than_or_equal","less_than","less_than_or_equal",
             "not_equal","case_insensitive_not_equal","begins_with","ends_with"}
SEL_META={"datatype","value_match","selection_match","require","redact_result"}

def walk(node):
    if isinstance(node,dict):
        yield node
        for val in node.values():
            yield from walk(val)
    elif isinstance(node,list):
        for val in node:
            yield from walk(val)

def resolved_source(source,test):
    obj=test.get("object")
    if isinstance(obj,str):
        return (source.get("shared_objects") or {}).get(obj), "named"
    if isinstance(obj,dict):
        return obj,"inline"
    return None,"objectless_or_unresolved"

def describe_object(obj):
    if not isinstance(obj,dict):
        return {"shape":"objectless_or_unresolved", "selection_kinds":[],
                "potential_expected_population":"not_determined",
                "dynamic":False, "fixed_multiple_values":False}
    main=[k for k in ("select","collect","set","for_each") if k in obj]
    shape="+".join(main) if main else "other"
    select=obj.get("select")
    modes=set()
    equality_arrays=0
    if isinstance(select,dict):
        for field,condition in select.items():
            if isinstance(condition,dict):
                for op,val in condition.items():
                    if op in COMPARATORS:
                        modes.add(op)
                    if op in {"equals","case_insensitive_equals"} and isinstance(val,list) and len(val)>1:
                        equality_arrays+=1
            else:
                modes.add("direct_scalar")
    dynamic=any("variable" in n or "input" in n or "from" in n for n in walk(obj))
    if "set" in obj or "for_each" in obj or dynamic:
        possible="dynamic_or_composed"
    elif equality_arrays:
        possible="explicit_multi_value_selection"
    elif modes and modes.issubset({"equals","case_insensitive_equals","direct_scalar"}):
        possible="fixed_literal_selection"
    elif modes & {"matches_regex","begins_with","ends_with","not_equal"}:
        possible="open_ended_match"
    elif "collect" in obj:
        possible="collector_defined_population"
    else:
        possible="needs_manual_review"
    return {"shape":shape,"selection_kinds":sorted(modes),
            "potential_expected_population":possible,"dynamic":dynamic,
            "fixed_multiple_values":equality_arrays>0}

def fingerprint(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest()

def census(path):
    sha=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if sha!=PINNED:raise ValueError("unexpected pinned archive digest "+sha)
    records=[]
    count=Counter()
    byshape=Counter()
    bypopulation=Counter()
    bycap=Counter()
    byfolder=Counter()
    pertype=Counter()
    objects=defaultdict(list)
    semantic_twins=defaultdict(list)
    with zipfile.ZipFile(path) as z:
        if z.testzip():raise ValueError("archive corruption")
        for name in sorted(z.namelist()):
            if not (name.startswith("authoring/") and "/assessments/" in name and name.endswith(".yaml")):
                continue
            doc=(yaml.safe_load(z.read(name)) or {}).get("assessment") or {}
            tests=doc.get("tests")
            if doc.get("mode")!="automated" or not isinstance(tests,dict) or not tests:continue
            count["assessments"]+=1
            for test_id,test in tests.items():
                count["tests"]+=1
                mode=str(test.get("collected_items_require"))
                obj,origin=resolved_source(doc,test)
                cap=str(test.get("capability","<missing>"))
                shape=describe_object(obj)
                objhash=fingerprint({"capability":cap,"object":obj})
                comparison_source={k:v for k,v in test.items()
                                   if k not in {"test_title","collected_items_require","object"}}
                semhash=fingerprint({"obj":obj,"cap":cap,"comparison":comparison_source})
                info={"source":name, "test":test_id,
                      "check":test.get("test_title"),"mode":mode,
                      "capability":cap,"source_origin":origin,
                      "state_bearing":bool(test.get("states")),
                      "object":obj,"source_shape":shape,
                      "objecthash":objhash,"semhash":semhash}
                objects[objhash].append(info)
                semantic_twins[semhash].append(info)
                if not (mode=="all_exist" or mode.startswith("all_exist_and_")):continue
                count["all_exist_tests"]+=1
                if test.get("states"):count["all_exist_with_states"]+=1
                else:count["all_exist_state_free"]+=1
                byshape[shape["shape"]]+=1
                bypopulation[shape["potential_expected_population"]]+=1
                bycap[cap]+=1
                byfolder[name.split("/")[1]]+=1
                for v in shape["selection_kinds"]:pertype[v]+=1
                records.append(info)
    if count["assessments"]!=872 or count["tests"]!=1375 or count["all_exist_tests"]!=201:
        raise AssertionError(("unexpected source population",dict(count)))
    sameobj=[]
    sametest=[]
    for info in records:
        matches=[x for x in objects[info["objecthash"]] if
                 x["mode"] in {"at_least_one_exists","at_least_one_exists_and_all_match"}]
        exact=[x for x in semantic_twins[info["semhash"]] if
               x["mode"] in {"at_least_one_exists","at_least_one_exists_and_all_match"}]
        if matches:sameobj.append({"source":info["source"],"test":info["test"],
                                    "counterpart_count":len(matches),
                                    "counterpart_examples":[{"source":m["source"],"test":m["test"],"mode":m["mode"]} for m in matches[:3]]})
        if exact:sametest.append({"source":info["source"],"test":info["test"],
                                  "counterpart_count":len(exact),
                                  "counterpart_examples":[{"source":m["source"],"test":m["test"],"mode":m["mode"]} for m in exact[:3]]})
    def short(row):
        return {k:row[k] for k in ("source","test","check","capability","state_bearing","source_origin","source_shape")}
    potential={key:[short(r) for r in records if r["source_shape"]["potential_expected_population"]==key]
               for key in sorted(bypopulation)}
    return {
       "status":"FORENSIC SOURCE-CHOICE CENSUS: intent not proven; no content rewrites",
       "source_sha256":sha,
       "counts":dict(count),
       "capabilities":dict(bycap.most_common()),
       "folders":dict(byfolder.most_common()),
       "object_shapes":dict(byshape.most_common()),
       "potential_expected_population":dict(bypopulation.most_common()),
       "selector_kinds":dict(pertype.most_common()),
       "same_object_cross_mode_count":len(sameobj),
       "same_object_cross_mode_examples":sameobj[:60],
       "exact_except_existence_cross_mode_count":len(sametest),
       "exact_except_existence_cross_mode_examples":sametest[:60],
       "all_201_tests":[short(r) for r in records],
       "examples_by_population":{k:v[:15] for k,v in potential.items()},
       "limitations":[
         "No author intent, copy/paste, mistake, or source OVAL XML choice inferred from converted YAML.",
         "Selector categories are structural heuristics, not proof of a fixed or enumerated runtime population.",
         "A shared folder is reused by multiple STIGs and is not a seventh STIG.",
         "No live collection or certified OVAL runtime semantics; do not normalize all_exist automatically.",
         "OVAL 5.12.3 common schema says Test all_exist is equivalent to at_least_one, but generic tables distinguish mixed Item statuses.",
         "5.12.3 System Characteristics permit optional partial-match Items with status does not exist.",
         "The fixed items/condition proposal is not yet a fully proven grammar."
       ]
    }

def markdown(data):
    c=data["counts"]
    lines=["# Do authors really need Test all_exist?",
      "","**SCAP-NG 0.4 source-forensics only. Not an adopted syntax or a statement of original author intent.**",
      "",f"Pinned six-STIG source: {c['all_exist_tests']} of {c['tests']} named Tests in {c['assessments']} unique automated Assessments.",
      f"{c['all_exist_state_free']} State-free; {c['all_exist_with_states']} State-bearing.",
      "","## Capability distribution","",
      "| Capability | Tests |","| --- | ---: |"]
    lines += [f"| `{a}` | {n} |" for a,n in data["capabilities"].items()]
    lines += ["","## Selected Object shape","",
              "| Shape | Test count |","| --- | ---: |"]
    lines += [f"| `{a}` | {n} |" for a,n in data["object_shapes"].items()]
    lines += ["","## What population can the collector plausibly select?","",
              "These are **heuristics**, not semantic conclusions.",
              "","| Category | Tests |","| --- | ---: |"]
    lines += [f"| `{a}` | {n} |" for a,n in data["potential_expected_population"].items()]
    lines += ["","## Direct evidence of differing authoring choices","",
              f"- `all_exist` Tests whose selected Object is also used by at-least-one Test(s): **{data['same_object_cross_mode_count']}**",
              f"- `all_exist` Tests also found with the same Object and comparison body but different existence mode: **{data['exact_except_existence_cross_mode_count']}**",
              "","These comparisons detect inconsistent or intentional vocabulary choices; neither proves that a source author copied a Test in error.",
              "","## Representative cases (full ledger in JSON)",""]
    for key,rows in data["examples_by_population"].items():
        lines += ["",f"### {key}", ""]
        for row in rows[:5]:
            lines.append(f"- `{row['source']}` — `{row['test']}`: {row['check']}")
    lines+=["","## Technical distinction that remains open","",
      "1. Under a complete collection of only existing Items, Test `all_exist` and `at_least_one_exists` agree: one or more exist.",
      "2. When a complete collected Object references an existing Item and another Item marked does-not-exist, the common OVAL existence table returns false for `all_exist` but true for `at_least_one_exists`.",
      "3. OVAL 5.12.3 says collectors MAY report optional partially matching, nonexistent Items. Some source selectors may expose those and some may not.",
      "4. Incomplete and error collection flags require separate result propagation; neither mode alone proves all required objects have been inventoried.",
      "5. In an Object using a variable or literal expected names, `all_exist` may express a meaningful fixed-resource obligation. Pattern-matched discovery does not specify a target count by itself.",
      "","**Working policy:** retain `all_exist` source-exact while investigating collection status and original source XML. Do not remove it from import support on the strength of a corpus percentage.",
      "","## Research limitations",""]
    lines += ["- "+x for x in data["limitations"]]
    return "\n".join(lines)+"\n"

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--json",required=True)
    p.add_argument("--markdown",required=True)
    args=p.parse_args()
    data=census(args.archive)
    Path(args.json).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    Path(args.markdown).write_text(markdown(data))
    print(json.dumps({k:data[k] for k in ("counts","object_shapes","potential_expected_population",
                                      "same_object_cross_mode_count",
                                      "exact_except_existence_cross_mode_count")},indent=2))
