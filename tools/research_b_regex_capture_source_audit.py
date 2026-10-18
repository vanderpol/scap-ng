#!/usr/bin/env python3
"""#237 source regex_capture ambiguity audit across pinned converted six STIGs.

OVAL Definitions 5.x specifies the FIRST capture group only, empty string
when unmatched. Python regex counting is approximate; source XML and OVAL
regex dialect parity remain unproven. Never treat this as an execution count.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re

from research_b_full_corpus_import import read_source,import_corpus


def capture_expressions(document):
    found=[]
    def walk(node,trail):
        if isinstance(node,dict):
            for key,value in node.items():
                if key=="regex_capture":
                    found.append((trail+[key],value))
                walk(value,trail+[str(key)])
        elif isinstance(node,list):
            for i,entry in enumerate(node):
                walk(entry,trail+[str(i)])
    walk(document,[])
    return found


def audit(capsules):
    items=[]
    by_group=Counter()
    for aid,cap in sorted(capsules.items()):
        a=cap["source_document"].get("assessment",{})
        if a.get("mode")!="automated":
            continue
        variables=a.get("variables",{})
        if not isinstance(variables,dict):
            continue
        for variable_name,source in sorted(variables.items()):
            for path,expr in capture_expressions(source):
                pattern=expr.get("pattern") if isinstance(expr,dict) else None
                if type(pattern) is not str:
                    group_kind="dynamic_or_missing"
                    groups=None
                elif len(pattern)>4096:
                    group_kind="too_long_for_research"
                    groups=None
                else:
                    try:
                        comp=re.compile(pattern)
                        groups=comp.groups
                        group_kind=(
                            "no_capture_groups" if groups==0 else
                            "first_capture_only" if groups==1 else
                            "multiple_capture_groups")
                    except re.error:
                        group_kind="unsupported_Python_regex"
                        groups=None
                by_group[group_kind]+=1
                items.append({
                    "assessment_id":aid,
                    "source_path":cap["source_path"],
                    "source_variable":variable_name,
                    "expression_path":"/".join(path),
                    "pattern":pattern,
                    "capture_groups_python_re":groups,
                    "classification":group_kind,
                    "original_OVAL_first_capture_parity_verified":False,
                })
    return {
        "format":"scap-ng-b-six-stream-regex-capture-risk-audit/0.1",
        "source_kind":"converted_0.3_not_original_SCAP_1.4_XML",
        "parity_verified":False,
        "expressions":len(items),
        "distinct_assessments":len({x["assessment_id"] for x in items}),
        "group_count_summary":dict(sorted(by_group.items())),
        "cases":items,
    }


def markdown(report):
    lines=[
        "# B six-STIG source regex_capture parity risk audit",
        "",
        "**Research only. Counts Python capture groups in converted 0.3 source,",
        "not original OVAL regex compilation or source-equivalent execution.**",
        "",
        f"**Expressions:** {report['expressions']}",
        f"**Assessments:** {report['distinct_assessments']}",
        "",
        "| Capture-group shape | Expressions |",
        "| --- | ---: |",
    ]
    for k,v in sorted(report["group_count_summary"].items(),
                      key=lambda p:(-p[1],p[0])):
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "The [published OVAL Definitions schema](https://github.com/OVALProject/Language/blob/master/schemas/oval-definitions-schema.xsd)",
        "documents that regex_capture uses **only the first capture group**",
        "and produces an **empty string** for a nonmatching target.",
        "A converted expression with two or more groups is **not automatically",
        "incorrect**, but must not be rewritten to select another group.",
        "",
        "## Multi-group/zero-group source examples",
        "",
        "| Assessment | Variable | Groups | Source expression path |",
        "| --- | --- | ---: | --- |",
    ]
    relevant=[x for x in report["cases"] if x["classification"] in (
        "multiple_capture_groups","no_capture_groups")]
    for x in relevant[:40]:
        lines.append(f"| {x['assessment_id']} | {x['source_variable']} | "
                     f"{x['capture_groups_python_re']} | {x['expression_path']} |")
    if not relevant:lines.append("| None | — | — | — |")
    lines+=["","[Complete exact source patterns](regex-capture-audit.json).",
            "All resulting values still require original SCAP 1.4 source",
            "differential tests, including OVAL-versus-Python regex lexical parity.",
            "These cases are **not** added to executable conversion totals.",""]
    return "\n".join(lines)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--markdown",type=Path,required=True)
    args=p.parse_args()
    docs,raw=read_source(args.authoring_zip)
    _,caps=import_corpus(docs,raw,expected_benchmarks=6)
    result=audit(caps)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    args.markdown.parent.mkdir(parents=True,exist_ok=True)
    args.markdown.write_text(markdown(result))
    print(json.dumps({"assessments":result["distinct_assessments"],
                      "expressions":result["expressions"],
                      "shapes":result["group_count_summary"]},sort_keys=True))


if __name__=="__main__":
    main()
