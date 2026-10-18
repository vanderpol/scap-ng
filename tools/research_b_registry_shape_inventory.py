#!/usr/bin/env python3
"""#237: source registry Test frequencies across six streams, not OVAL parity."""
from __future__ import annotations

import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
from research_b_full_corpus_import import read_source,import_corpus


def inventory(capsules):
    test_counts=Counter()
    shape_counts=Counter()
    examples=defaultdict(list)
    ids=set()
    for aid,capsule in sorted(capsules.items()):
        a=capsule["source_document"].get("assessment",{})
        if a.get("mode")!="automated":
            continue
        tests=a.get("tests")
        if not isinstance(tests,dict):
            continue
        for name,test in sorted(tests.items()):
            if not isinstance(test,dict) or test.get("capability")!="windows.registry":
                continue
            ids.add(aid)
            states=test.get("states")
            if states is None:state_kind="none"
            elif not isinstance(states,list):state_kind="non_array"
            elif len(states)!=1:state_kind="multiple_or_empty"
            elif not isinstance(states[0],dict):state_kind="non_object"
            else:
                st=states[0]
                if set(st)=={"field","operation","value","existence","match"}:
                    value=st["value"]
                    datatype="string" if type(value) is str else (
                        "integer" if type(value) is int else "other")
                    state_kind=("/".join((str(st["field"]),str(st["operation"]),
                                        str(st["existence"]),str(st["match"]),datatype)))
                else:state_kind="complex_keys:"+",".join(sorted(st))
            obj=test.get("object")
            source_obj=obj if isinstance(obj,dict) else {}
            selector=source_obj.get("select")
            exact=isinstance(selector,dict) and set(selector)=={"hive","key","name"} and (
                selector.get("hive")=="local_machine") and all(
                isinstance(selector.get(k),dict) and
                set(selector[k])=={"operation","value"} and
                selector[k].get("operation")=="equals" and
                type(selector[k].get("value")) is str for k in ("key","name"))
            direct=(len(tests)==1 and a.get("evaluate")=={"test":name})
            dim={
                "existence":str(test.get("existence","(missing)")),
                "match":str(test.get("match","(missing)")),
                "state":state_kind,
                "direct_single_test":str(direct),
                "exact_HKLM_selector":str(exact),
                "shared_object_reference":str(not isinstance(obj,dict)),
                "has_variables":str(bool(a.get("variables"))),
            }
            for f,v in dim.items():
                test_counts[f+"="+v]+=1
            key=" | ".join((dim["state"],dim["existence"],dim["match"],
                            dim["direct_single_test"],dim["exact_HKLM_selector"]))
            shape_counts[key]+=1
            if len(examples[key])<4:
                examples[key].append({"assessment_id":aid,"source_test_id":name,
                                      "source_path":capsule["source_path"]})
    return {
        "format":"scap-ng-b-registry-shapes/0.1",
        "source_kind":"converted_0.3_not_raw_SCAP_1.4",
        "original_source_parity_verified":False,
        "distinct_referenced_assessments":len(ids),
        "registry_test_nodes":sum(shape_counts.values()),
        "dimensions":dict(sorted(test_counts.items())),
        "shapes":[{"shape":k,"test_nodes":v,"examples":examples[k]}
                  for k,v in sorted(shape_counts.items(),
                                    key=lambda p:(-p[1],p[0]))],
    }


def markdown(report):
    lines=["# B six-STIG Windows registry source patterns",
           "",
           "**Research-only converted 0.3 source shapes; NOT original SCAP 1.4 OVAL parity.**",
           "",
           f"**Referenced registry Assessments:** {report['distinct_referenced_assessments']}",
           f"**Registry Test nodes:** {report['registry_test_nodes']}",
           "",
           "## Frequent source attributes",
           "",
           "| Attribute | Test nodes |",
           "| --- | ---: |"]
    for key,count in sorted(report["dimensions"].items(),
                            key=lambda p:(-p[1],p[0])):
        lines.append("| "+key.replace("|",r"\|")+f" | {count} |")
    lines+=["","## Combined shapes","","| Shape | Test nodes | Example IDs |",
            "| --- | ---: | --- |"]
    for row in report["shapes"][:60]:
        examples=", ".join(x["assessment_id"] for x in row["examples"])
        lines.append("| "+row["shape"].replace("|",r"\|")+
                     f" | {row['test_nodes']} | {examples} |")
    lines+=["","[Complete machine-readable shapes](registry-shapes.json).",
            "",
            "Source omitted registry-view behaviors must be verified against",
            "original XML. Typed value mismatch is not silently coerced.",
            "Source Test counts are NOT unique Assessment counts or scanner parity.",""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--markdown",required=True,type=Path)
    a=p.parse_args()
    docs,hashes=read_source(a.authoring_zip)
    _,caps=import_corpus(docs,hashes,expected_benchmarks=6)
    result=inventory(caps)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    a.markdown.parent.mkdir(parents=True,exist_ok=True)
    a.markdown.write_text(markdown(result))
    print(json.dumps({"assessments":result["distinct_referenced_assessments"],
                      "tests":result["registry_test_nodes"],
                      "top_shapes":result["shapes"][:4]},indent=2))


if __name__=="__main__":
    main()
