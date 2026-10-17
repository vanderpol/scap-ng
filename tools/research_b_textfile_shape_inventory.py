#!/usr/bin/env python3
"""#237: source-driven B textfile Test/State shape priorities over all six STIGs.

Derived from the published converted-0.3 source ZIP, not original SCAP 1.4
XML. Counts are for *source structure*, never scanner parity. All Test shapes
are accounted for; unknown or variable-based selectors are not simplified.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from research_b_full_corpus_import import read_source, import_corpus

CAPABILITY="independent.textfilecontent54"
FORMAT="scap-ng-b-textfile-shape-inventory/0.1"


def _shape(test, assessment):
    obj=test.get("object")
    obj=obj if isinstance(obj,dict) else {}
    select=obj.get("select")
    select=select if isinstance(select,dict) else {}
    pattern=select.get("pattern")
    literal=pattern.get("value") if isinstance(pattern,dict) else None
    capture_group="unknown"
    if isinstance(literal,str):
        if len(literal)>4096:
            capture_group="oversize"
        else:
            try:
                capture_group=str(re.compile(literal).groups)
            except re.error:
                capture_group="regex_unrecognized"
    elif isinstance(literal,dict):
        capture_group="dynamic"
    states=test.get("states",[])
    if not isinstance(states,list):
        state_shape="invalid"
    elif not states:
        state_shape="none"
    elif len(states)>1:
        state_shape="multiple"
    elif not isinstance(states[0],dict):
        state_shape="invalid"
    else:
        state=states[0]
        expected=state.get("value")
        value_kind=("string" if isinstance(expected,str) else
                    "variable" if isinstance(expected,dict) and
                    "variable" in expected else
                    "other")
        state_shape="/".join((
            str(state.get("field","(missing)")),
            str(state.get("operation","(missing)")),
            str(state.get("existence","(missing)")),
            str(state.get("match","(missing)")),
            value_kind))
    tests=assessment.get("tests",{})
    direct=len(tests)==1 and assessment.get("evaluate")=={"test":next(iter(tests))}
    flags=obj.get("collect")
    return {
        "state_shape":state_shape,
        "test_existence":str(test.get("existence","(missing)")),
        "test_match":str(test.get("match","(missing)")),
        "capture_groups":capture_group,
        "direct_single_test":direct,
        "selector_keys":",".join(sorted(str(k) for k in select)),
        "object_keys":",".join(sorted(str(k) for k in obj)),
        "collect_options":",".join(sorted(str(k) for k in flags)) if isinstance(flags,dict) else "(none)",
        "has_variables":bool(assessment.get("variables")),
        "has_shared_objects":bool(assessment.get("shared_objects")),
        "has_for_each":("for_each" in json.dumps(obj,sort_keys=True,default=str)),
    }


def shape_inventory(capsules):
    counts={key:Counter() for key in (
        "state_shape","test_existence","test_match","capture_groups",
        "direct_single_test","selector_keys","object_keys","collect_options",
        "has_variables","has_shared_objects","has_for_each",
    )}
    combinations=Counter()
    examples=defaultdict(list)
    assessments=set()
    test_total=0
    for aid,capsule in sorted(capsules.items()):
        a=capsule["source_document"].get("assessment",{})
        if a.get("mode")!="automated":continue
        tests=a.get("tests",{})
        if not isinstance(tests,dict):continue
        for tid,test in sorted(tests.items()):
            if not isinstance(test,dict) or test.get("capability")!=CAPABILITY:
                continue
            test_total+=1
            assessments.add(aid)
            shape=_shape(test,a)
            for key,value in shape.items():
                counts[key][str(value)]+=1
            combo=" | ".join((shape["state_shape"],shape["test_existence"],
                             shape["test_match"],shape["capture_groups"],
                             str(shape["direct_single_test"])))
            combinations[combo]+=1
            if len(examples[combo])<4:examples[combo].append({
                "assessment_id":aid,"source_test_id":tid,
                "source_path":capsule["source_path"]})
    return {
        "format":FORMAT,
        "source_kind":"converted_0.3_authoring_zip_not_raw_SCAP_1.4",
        "source_equivalence_proven":False,
        "assessments_using_textfile":len(assessments),
        "textfile_test_nodes":test_total,
        "dimensions":{k:dict(sorted(v.items())) for k,v in counts.items()},
        "combinations":[{"shape":k,"test_nodes":v,"examples":examples[k]}
                        for k,v in sorted(combinations.items(),
                                          key=lambda item:(-item[1],item[0]))],
    }


def render_markdown(r):
    lines=[
        "# 0.4-B textfile content source patterns",
        "",
        "**Research census of the six converted 0.3 STIGs; not verified raw SCAP 1.4 semantics.**",
        "The same Assessment may contain many Test nodes. All counts below count",
        "Tests, not distinct Assessments, except where explicitly labeled.",
        "",
        f"**Referenced automated Assessments using textfile content:** {r['assessments_using_textfile']}",
        f"**Textfile Test nodes:** {r['textfile_test_nodes']}",
    ]
    labels={
        "state_shape":"Observed State shapes",
        "test_existence":"Test Item-existence modes",
        "test_match":"Test Item-match modes",
        "capture_groups":"Literal regex capture group counts",
        "direct_single_test":"Direct one-Test Assessment opportunities",
        "has_variables":"Assessment-level Variable dependencies",
        "has_shared_objects":"Shared-Object dependencies",
        "has_for_each":"Embedded foreach dependencies",
    }
    for key,label in labels.items():
        lines+=["","## "+label,"","| Shape | Test nodes |","| --- | ---: |"]
        for value,count in sorted(r["dimensions"][key].items(),
                                   key=lambda p:(-p[1],p[0])):
            lines.append(f"| {value.replace('|', r'\|')} | {count} |")
    lines.extend([
        "","## Top correlated patterns","","| Combined source shape | Test nodes | Example IDs |",
        "| --- | ---: | --- |",
    ])
    for x in r["combinations"][:30]:
        ids=", ".join(ex["assessment_id"] for ex in x["examples"])
        lines.append(f"| {x['shape'].replace('|',r'\|')} | {x['test_nodes']} | {ids} |")
    lines.extend([
        "","[Machine-readable complete groups and source Test IDs](textfile-shapes.json).",
        "",
        "Do not infer that a Python regex capture means lossless OVAL",
        "textfilecontent54 semantics. Prioritize one-feature semantic gates",
        "with original XML differential tests, not speculative YAML rewrites.",
        "No A/B bake-off until all six content streams have comparable support.",
        "",
    ])
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    docs,hashes=read_source(args.authoring_zip)
    _,caps=import_corpus(docs,hashes,expected_benchmarks=6)
    r=shape_inventory(caps)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(r,sort_keys=True,indent=2)+"\n")
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.write_text(render_markdown(r))
    print(json.dumps({"assessments":r["assessments_using_textfile"],
                      "tests":r["textfile_test_nodes"],
                      "top_shapes":r["combinations"][:4]},indent=2))


if __name__=="__main__":
    main()
