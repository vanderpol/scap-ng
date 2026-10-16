#!/usr/bin/env python3
"""Source-boundary study: none_exist Test carrying a State (research #235/#229).

The lone source Assessment not admitted into the English-first authoring
grammar requires zero collected Items yet contains an actual State. We do not
delete it or silently rewrite it as 'no Items match State'. The OVAL 5.12.3
generic reference defines many decisive outcomes, but does not define empty
State aggregation in its local helper. This isolates that ambiguity.
"""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile
import yaml
from oval_result_truth_tables import evaluate_collected_object_test as reference, TRUE, FALSE

PIN="03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
PATH="authoring/shared/assessments/linux/files/verify-boot-loader-root-admin-adminstrator.assessment.yaml"

def run(zip_path):
    digest=hashlib.sha256(Path(zip_path).read_bytes()).hexdigest()
    if digest!=PIN:raise ValueError("source archive changed")
    with zipfile.ZipFile(zip_path) as z:
        ass=(yaml.safe_load(z.read(PATH)) or {})["assessment"]
    matched=[(tid,test) for tid,test in ass["tests"].items()
             if test.get("collected_items_require")=="none_exist" and test.get("states")]
    if len(matched)!=1:
        raise AssertionError("expected one none_exist-with-State source Test")
    tid,t=matched[0]
    if t["states"]!=[{"subexpression":{"require":"at_least_one_exists_and_all_match",
                                  "matches_regex":"^(root|admin|administrator)$"}}]:
        raise AssertionError("source State unexpectedly changed")
    rows=[]
    def add(flag,n,observed,expected):
        try:
            actual=reference(flag,existence="none_exist",check="all",
                             has_state=True,item_results=observed,exists=n)
        except AssertionError:
            actual="REFERENCE_UNDEFINED_EMPTY_STATE_AGGREGATION"
        if actual!=expected:
            raise AssertionError("source-boundary outcome unexpectedly differs: "+repr((flag,n,actual,expected)))
        rows.append({"flag":flag,"existing_items":n,"state_outcomes":observed,"result":actual})
    add("does not exist",0,[],TRUE)
    add("error",0,[],"error")
    add("not collected",0,[],"unknown")
    add("not applicable",0,[],"not applicable")
    add("complete",1,[TRUE],FALSE)
    add("complete",1,[FALSE],FALSE)
    add("incomplete",1,[TRUE],FALSE)
    add("incomplete",0,[],"unknown")
    add("complete",0,[],"REFERENCE_UNDEFINED_EMPTY_STATE_AGGREGATION")
    return {
        "status":"DECISIVE RESULT BOUNDARY VERIFIED, EMPTY COMPLETE AMBIGUITY LEFT OPEN",
        "source_path":PATH,"source_test":tid,"source_sha256":digest,
        "source_test_exact":t,
        "probes":rows,
        "do_not_rewrite_as":[
            "none_collected_items_match_state",
            "state_free_none_exist_with_deleted_original_state",
        ],
        "next_question":"Determine 5.12.3 complete-but-zero-Items Test result when check_existence=none_exist and a State remains. The local generic reference raises on empty State aggregation; no scanner/evidence claim.",
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    a=p.parse_args()
    report=run(a.archive)
    if a.output:Path(a.output).write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("status","source_path","source_test","probes","next_question")},indent=2))

if __name__=="__main__": main()
