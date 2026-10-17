#!/usr/bin/env python3
"""Research #235/#229: should Item existence be authored for every Test?

Audit exact source Test modes and separate state/record-field existence.
Compute *counterexamples*, not a broad claim that generic OVAL operators are
interchangeable. Compare explanatory prose and literal existence truth tables.
No original XML scanner runtime claim.
"""
import argparse
from collections import Counter,defaultdict
from itertools import product
import json,hashlib,zipfile
from pathlib import Path
import yaml

from oval_result_truth_tables import aggregate_existence
from research_english_first_04_compact_layout import PINNED

MODES=("at_least_one_exists","none_exist","all_exist","any_exist","only_one_exists")
EXAMPLES_PER_MODE=7
XSD=Path("third_party/scap-1.4-schemas/oval_5.12.3/oval-common-schema.xsd")
DEFINITION=Path("third_party/scap-1.4-schemas/oval_5.12.3/oval-definitions-schema.xsd")
KEY_DOCUMENTATION="When used in the context of an OVAL test's check_existence attribute, this value is equivalent to 'at_least_one_exists' because non-existent items have no impact upon evaluation."
KEY_SCHEMATRON="No state should be referenced when check_existence has a value of 'none_exist'."

def category(path):
    parts=path.split("/")
    if len(parts)>2 and parts[1]=="shared":return "shared"
    return parts[1] if len(parts)>1 else "other"

def audit(archive):
    digest=hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest!=PINNED:raise ValueError("source source ZIP SHA changed")
    common=XSD.read_text(encoding="utf-8")
    definitions=DEFINITION.read_text(encoding="utf-8")
    if KEY_DOCUMENTATION not in common or KEY_SCHEMATRON not in definitions:
        raise AssertionError("OVAL 5.12.3 source annotations changed")
    modes=Counter()
    split=Counter()
    samples=defaultdict(list)
    by_cap=defaultdict(Counter)
    by_benchmark=defaultdict(Counter)
    field=Counter()
    field_samples=defaultdict(list)
    flags=Counter()
    anomalous=[]
    unique_assessments=0
    def collect_fields(node, scope, descriptor):
        # Existence of fields in a State is a different layer from existence
        # of Test Items. Do not group state_fields_require with Test existence.
        if isinstance(node,dict):
            if "require" in node:
                key=str(node["require"])
                field[key]+=1
                if len(field_samples[key])<3:field_samples[key].append(descriptor)
            for key,value in node.items():collect_fields(value,scope+"/"+str(key),descriptor)
        elif isinstance(node,list):
            for index,item in enumerate(node):collect_fields(item,scope+"/"+str(index),descriptor)
    with zipfile.ZipFile(archive) as z:
        if z.testzip():raise ValueError("ZIP corruption")
        for path in sorted(z.namelist()):
            if not(path.startswith("authoring/") and "/assessments/" in path and path.endswith(".yaml")):continue
            ass=(yaml.safe_load(z.read(path)) or {}).get("assessment") or {}
            if ass.get("mode")!="automated" or not ass.get("tests"):continue
            unique_assessments+=1
            for name,test in ass["tests"].items():
                mode=test.get("collected_items_require")
                if mode not in MODES:
                    raise ValueError("unrecognized Test existence mode "+repr((path,name,mode)))
                cap=test.get("capability","(missing capability)")
                test_has_state=bool(test.get("states"))
                modes[mode]+=1
                split[mode+":state" if test_has_state else mode+":state-free"]+=1
                by_cap[mode][cap]+=1
                by_benchmark[mode][category(path)]+=1
                if len(samples[mode])<EXAMPLES_PER_MODE:
                    samples[mode].append({
                        "path":path,"test":name,"capability":cap,
                        "has_state":test_has_state,
                        "title":test.get("test_title"),
                        "states_match":test.get("states_match"),
                    })
                if mode=="none_exist" and test_has_state:
                    anomalous.append({"path":path,"test":name})
                if "state_fields_require" in test:
                    field["test_inherited_state_fields:"+str(test["state_fields_require"])]+=1
                if test_has_state:
                    collect_fields(test["states"],"/states",{"path":path,"test":name})
    if unique_assessments!=872 or sum(modes.values())!=1375:
        raise AssertionError("pinned source baseline changed "+repr((unique_assessments,dict(modes))))
    if len(anomalous)!=1:raise AssertionError("expected pinned single anomaly")

    vectors=[
        {"exists":0,"does_not_exist":0,"error":0,"not_collected":0},
        {"exists":1,"does_not_exist":0,"error":0,"not_collected":0},
        {"exists":2,"does_not_exist":0,"error":0,"not_collected":0},
        {"exists":1,"does_not_exist":1,"error":0,"not_collected":0},
        {"exists":1,"does_not_exist":0,"error":1,"not_collected":0},
        {"exists":1,"does_not_exist":0,"error":0,"not_collected":1},
        {"exists":0,"does_not_exist":1,"error":0,"not_collected":0},
        {"exists":0,"does_not_exist":0,"error":1,"not_collected":0},
        {"exists":0,"does_not_exist":0,"error":0,"not_collected":1},
    ]
    examples=[]
    for v in vectors:
        examples.append({**v,**{mode:aggregate_existence(mode,**v) for mode in MODES}})
    against={}
    total=0
    for mode in MODES:
        if mode=="at_least_one_exists":continue
        differences=[]
        for ex,dne,err,nc in product(range(3),repeat=4):
            v=dict(exists=ex,does_not_exist=dne,error=err,not_collected=nc)
            result=aggregate_existence(mode,**v)
            reference=aggregate_existence("at_least_one_exists",**v)
            if result!=reference:
                if len(differences)<7:differences.append({**v,"reference":reference,"other":result})
                total+=1
        against[mode]={"counterexamples":differences,
                       "has_distinct_generic_table_semantics":bool(differences)}
    return {
        "status":"SOURCE POPULATION + PINNED OVAL EXISTENCE TABLE AUDIT, NOT SCANNER PROOF",
        "sha256":digest,"assessments":unique_assessments,"tests":sum(modes.values()),
        "mode_counts":dict(modes),"state_split":dict(split),
        "examples":dict(samples),
        "capability_distribution":{k:dict(v.most_common(14)) for k,v in by_cap.items()},
        "benchmark_distribution":{k:dict(v.most_common()) for k,v in by_benchmark.items()},
        "state_field_requirements":dict(field),
        "state_field_examples":dict(field_samples),
        "comparison_vectors":examples,
        "comparisons_to_at_least_one":against,
        "schema_conflict":{
            "source":"third_party/scap-1.4-schemas/oval_5.12.3/oval-common-schema.xsd",
            "text":KEY_DOCUMENTATION,
            "generic_table":{"example":"EX=1, DE=1","all_exist":"false","at_least_one_exists":"true"},
            "interpretation":"Documentation says equivalent at Test scope, yet generic truth-table entries differ if does_not_exist/error/not_collected status coexists with an existing Item; determine which statuses affect Test check_existence before normalizing."
        },
        "none_exist_with_attached_state":anomalous,
        "decision_recommendation":{
            "normal_authoring":"At least one Item with matching requirements; absent desired Items must not pass silently.",
            "none_exist":"State-free existence Test only, separate from field comparison.",
            "only_one_exists":"Real but uncommon exact Item cardinality, retain special-case capability.",
            "any_exist":"Allows zero collected Items, used by optional checks; do not silently default to required Items.",
            "all_exist":"Investigate equivalence at Test scope and the significance of absent/error Items; postpone authoring decision.",
            "state_field_existence":"Retain separate scope from check-level Item existence."
        },
        "limitations":[
          "Counts are uniquely named source Test definitions in six native converted benchmark sets, not all SCAP 1.4 XML Tests or 65-STIG corpus.",
          "Generic OVAL existence tables do not settle all Item collection flag/State aggregation differences or source XML provenance.",
          "No implicit default introduced by this audit."
        ]
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--output")
    a=p.parse_args()
    result=audit(a.archive)
    if a.output:Path(a.output).write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:result[k] for k in ("status","assessments","tests","mode_counts","state_split","none_exist_with_attached_state")},indent=2))

if __name__=="__main__":main()
