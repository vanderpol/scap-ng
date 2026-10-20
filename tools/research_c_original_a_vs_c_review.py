#!/usr/bin/env python3
"""Refs #245: unbiased original source-backed A Test projection versus C.
The A-side is the exact native 0.4-A Test IR produced by the existing C
compiler (not an independent A authoring exercise). Preserve original A import
as the third baseline. Structural parity is not live scanner parity.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import yaml
from jsonschema import Draft202012Validator

from research_c_unified_compiler import compile_c_unified

CASES=[
 ("linux/linux-def_kernelmodule_test.xml","Linux kernel modules (3 Tests)"),
 ("linux/linux-def_partition_test.xml","Linux partitions with shared State (3 Tests)"),
 ("windows/win-def_passwordpolicy_test.xml","Windows password policy (7 Tests)"),
 ("linux/linux-def_systemdunitproperty_test.xml","Linux systemd properties (10 Tests)"),
 ("linux/unix-def_sysctl_test.xml","Unix sysctl on Linux (5 Tests)"),
]
PIN="e3538595c5083b9c34d937a81d319234df9bbfaa"

def require(ok,msg):
    if not ok:raise ValueError(msg)

def one(items,msg):
    xs=list(items)
    require(len(xs)==1,msg+" expected one result, got "+str(len(xs)))
    return xs[0]

def write_yaml(path,obj):
    txt=yaml.safe_dump(obj,sort_keys=False,allow_unicode=True,width=110)
    path.write_text(txt,encoding="utf-8")
    return {"nonblank_lines":sum(bool(line.strip()) for line in txt.splitlines()),
            "lines":len(txt.splitlines()),"utf8_bytes":len(txt.encode("utf-8"))}

def rekey_original_logic(node,crosswalk):
    require(isinstance(node,dict) and len(node)==1,"invalid source logic")
    k,v=next(iter(node.items()))
    if k=="test":
        require(v in crosswalk,"source Test missing from re-keyed C")
        return {"test":crosswalk[v]}
    require(k in ("all","any") and isinstance(v,list) and bool(v),
            "unsupported original Boolean logic")
    return {k:[rekey_original_logic(x,crosswalk) for x in v]}

def compare(review,native,out):
    out.mkdir(parents=True,exist_ok=True)
    manifest=json.loads((native/"conversion-manifest.json").read_text())
    converted={(x["file"],x["definition_id"]):x
               for x in manifest["native_C_converted"]}
    failures={(x["file"],x["definition_id"]):x["reason"]
              for x in manifest["unsupported"]}
    reviews={}
    for p in review.glob("*.review.json"):
        row=json.loads(p.read_text())
        key=(row["source"]["file"],row["source"]["definition_id"])
        require(key not in reviews,"duplicate pinned source Definition")
        reviews[key]=row
    schema=json.loads((Path(__file__).resolve().parents[1]/
                       "schema/v0.4.0/assessment-language.schema.json").read_text())
    validator=Draft202012Validator(schema)
    summary=[]
    lines=["# SCAP-NG 0.4-A vs C: full original-OVAL side-by-side research",
           "",
           "Original OVAL pinned at OVAL-Community/SCAP-Self-Assertion commit "+PIN,
           "",
           "A is the exact versioned 0.4-A Test/State/Object projection from",
           "the C compiler, schema validated below. The separate original",
           "A-compatible imported Assessment is also preserved unabridged.",
           "This is not a separately authored 0.4-A artifact, live scanner",
           "parity, or an approved C language. Counted YAML is machine",
           "serialized identically for A and C, with no deleted properties.",
           "",
           "| Original content | Tests | A nonblank lines | C nonblank lines | C line saving |",
           "| --- | ---: | ---: | ---: | ---: |"]
    for rel,title in CASES:
        key,row=one(((k,r) for k,r in reviews.items() if k[0]==rel),
                    "source Definition "+rel)
        src=row["A_source_compatibility_fallback"]
        if key not in converted:
            require(key in failures,"source missing from the native-C manifest")
            summary.append({"source":rel,"full_C_compilation":False,
                            "blocker":failures[key]})
            lines.append("| "+title+" | "+str(len(src["tests"]))+
                         " | — | — | blocked: "+failures[key].split(":")[0]+" |")
            continue
        m=converted[key]
        require(m["C_source_test_count"]==len(src["tests"]),
                "source Test coverage mismatch")
        name=rel.split("/")[-1].removesuffix(".xml")
        c=yaml.safe_load((native/m["c_source"]).read_text())
        require(isinstance(c,dict) and isinstance(c.get("checks"),dict) and
                len(c["checks"])==len(src["tests"]),
                "not complete C Definition")
        compiled=compile_c_unified(c)
        require(compiled["scanner_executed"] is False and
                compiled["source_parity_verified"] is False,
                "unsupported scanner parity claim")
        cross={v["source_test"]:alias for alias,v in c["checks"].items()}
        require(set(cross)==set(src["tests"]),
                "not all original Test references survive C")
        evaluate=rekey_original_logic(src["evaluate"],cross)
        require(evaluate==compiled["expression"]["source_tree"],
                "original source Boolean AST changed")
        arm={"assessment":{
            "id":src["id"],"mode":"automated","evaluate":evaluate,
            "tests":compiled["tests"]}}
        if compiled["shared_objects"]:
            arm["assessment"]["shared_objects"]=compiled["shared_objects"]
        require(not list(validator.iter_errors(arm)),
                "0.4-A native Test projection violates versioned schema: "+
                "; ".join(x.message for x in list(validator.iter_errors(arm))[:2]))
        path=out/name
        s=write_yaml(path.with_suffix(".original-A-compatible.yaml"),{"assessment":src})
        a=write_yaml(path.with_suffix(".0.4-A-native.yaml"),arm)
        cmet=write_yaml(path.with_suffix(".0.4-C.yaml"),c)
        delta=round(100*(a["nonblank_lines"]-cmet["nonblank_lines"])/
                    a["nonblank_lines"],1)
        summary.append({"source":rel,"full_C_compilation":True,
                        "source_test_count":len(src["tests"]),
                        "A_native":a,"C_authoring":cmet,
                        "A_source_compatible":s,
                        "C_nonblank_line_saving_pct":delta,
                        "C_byte_saving_pct":round(
                            100*(a["utf8_bytes"]-cmet["utf8_bytes"])/a["utf8_bytes"],1),
                        "source_boolean_ast_equal":True,
                        "source_test_refs_preserved":True,
                        "native_A_schema_valid":True,
                        "scanner_execution_proven":False})
        lines.append("| "+title+" | "+str(len(src["tests"]))+" | "+
                     str(a["nonblank_lines"])+" | "+str(cmet["nonblank_lines"])+
                     " | "+str(delta)+"% |")
    lines+=["","## Review instructions","",
            "For a successful case compare the corresponding 0.4-A-native.yaml",
            "and 0.4-C.yaml files in this directory. The matching",
            "original-A-compatible.yaml retains original imported objects,",
            "States, Tests, titles and Test provenance for independent checking.",
            "",
            "There is deliberately no claim that small cases demonstrate a",
            "win on complex Set/Filter/Variable graphs. The latter still require",
            "real full native C conversion and a six-state scanner evidence gate.",
            "A negative line saving is a real C readability/size warning.",
            ""]
    (out/"A-VS-C-REVIEW.md").write_text("\n".join(lines),encoding="utf-8")
    (out/"metrics.json").write_text(json.dumps({
        "kind":"PINNED_OVAL_NATIVE_A_PROJECTION_VERSUS_C_RESEARCH",
        "pinned_original_oval_sha":PIN,"cases":summary},
        indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return "\n".join(lines),summary

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--review",type=Path,required=True)
    p.add_argument("--native",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    args=p.parse_args()
    report,summary=compare(args.review,args.native,args.out)
    print(report)
    print("METRICS:",json.dumps([{
        "source":x["source"],"saved_pct":x.get("C_nonblank_line_saving_pct"),
        "passed":x["full_C_compilation"]} for x in summary],sort_keys=True))

if __name__=="__main__":
    main()
