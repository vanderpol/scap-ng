#!/usr/bin/env python3
"""Refs #245: six-STIG C complexity triage over VERIFIED 0.4-A source IR.

Classify potential authoring surfaces, not proven C conversions.
The CLI verifies the full IR with A's independent decoder first.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path

CATEGORIES=("named_variables","shared_objects","foreach","set","filter",
            "selector_projection","record_predicate","objectless_test",
            "multiple_tests","assessment_dependencies")

def _contains_record_predicate(node):
    if isinstance(node,dict):
        if "record" in node and isinstance(node["record"],dict):
            return True
        return any(_contains_record_predicate(v) for v in node.values())
    if isinstance(node,list):
        return any(_contains_record_predicate(v) for v in node)
    return False

def classify_source_assessment(assessment,index):
    if not isinstance(assessment,dict) or assessment.get("mode")!="automated":
        raise ValueError("automated source Assessment required")
    if not isinstance(index,dict) or index.get("mode")!="automated":
        raise ValueError("matching source index required")
    dataflow=index.get("source_dataflow")
    if not isinstance(dataflow,dict) or dataflow.get("status")!="SOURCE_DATAFLOW_ONLY_NOT_EXECUTABLE":
        raise ValueError("verified source dataflow index required")
    tests=assessment.get("tests")
    if not isinstance(tests,dict) or not tests:
        raise ValueError("at least one source Test required")
    if not isinstance(dataflow.get("sites"),list):
        raise ValueError("missing source site index")
    sites=Counter(s["kind"] for s in dataflow["sites"])
    counts={
        "named_variables":len(assessment.get("variables") or {}),
        "shared_objects":len(assessment.get("shared_objects") or {}),
        "foreach":sites["for_each"],"set":sites["set"],
        "filter":sites["filter"],"selector_projection":sites["projection"],
        "record_predicate":sum(_contains_record_predicate(t.get("states",[]))
                               for t in tests.values()),
        "objectless_test":sum("object" not in t for t in tests.values()),
        "multiple_tests":max(0,len(tests)-1),
        "assessment_dependencies":len(assessment.get("dependencies") or {}),
    }
    hazards=[name for name in CATEGORIES if counts[name]>0]
    if any(counts[name] for name in (
        "named_variables","foreach","set","filter","selector_projection")):
        tier="DYNAMIC_SOURCE_GRAPH_NEEDS_COMPATIBILITY"
    elif counts["record_predicate"]:
        tier="RECORD_SOURCE_NEEDS_NARROW_COMPILER_PROOF"
    elif counts["shared_objects"] or counts["multiple_tests"] or counts["assessment_dependencies"]:
        tier="COMPOSITION_NEEDS_SOURCE_CHECK"
    else:
        tier="SIMPLE_SOURCE_REVIEW_CANDIDATE"
    return {
        "tier":tier,"counts":counts,"hazards":hazards,
        "C_compiler_proven":False,"OVAL_source_runtime_parity_proven":False,
        "legacy_source_ir_required_for_lossless_fallback":True,
    }

def summarize_verified_documents(documents,indexes):
    if not isinstance(documents,dict) or not isinstance(indexes,dict) or set(documents)!=set(indexes):
        raise ValueError("full matching verified AST/index mappings required")
    tiers=Counter();flags=Counter();groups=defaultdict(Counter)
    cases=[];n_assessments=0;n_tests=0
    for path,doc in sorted(documents.items()):
        a=doc.get("assessment") if isinstance(doc,dict) else None
        if not isinstance(a,dict) or a.get("mode")!="automated":
            continue
        category=classify_source_assessment(a,indexes[path])
        n_assessments+=1;n_tests+=len(a["tests"])
        tiers[category["tier"]]+=1
        flags.update(category["hazards"])
        segments=path.split("/")
        group=segments[1] if len(segments)>1 and segments[0]=="authoring" else "other"
        groups[group][category["tier"]]+=1
        cases.append({"path":path,"assessment_id":a["id"],
                      "tier":category["tier"],"hazards":category["hazards"]})
    return {
        "stage":"C_SOURCE_COMPLEXITY_TRIAGE_NOT_NATIVE_C_COVERAGE",
        "verified_A_source_envelope_required":True,
        "assessment_count":n_assessments,"named_test_count":n_tests,
        "tier_counts":dict(sorted(tiers.items())),
        "hazard_assessment_counts":dict(sorted(flags.items())),
        "by_source_group":{k:dict(sorted(v.items())) for k,v in sorted(groups.items())},
        "cases":cases,
        "C_converted_assessment_count_claimed":0,"scanner_runtime_semantics_proven":False,
    }

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--verified-ir",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--assert-six",action="store_true")
    args=ap.parse_args(argv)
    from v04_a_lossless_ir import decode_and_verify
    ir=json.loads(args.verified_ir.read_text(encoding="utf-8"))
    documents=decode_and_verify(ir)
    indexes={e["source_path"]:e.get("assessment_index") for e in ir["documents"]}
    result=summarize_verified_documents(documents,indexes)
    if args.assert_six and (result["assessment_count"],result["named_test_count"])!=(872,1375):
        raise ValueError("six-STIG source snapshot counts changed unexpectedly")
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print("C source triage only:",result["assessment_count"],"Assessments;",
          result["named_test_count"],"Tests; report:",args.output)

if __name__=="__main__":
    main()
