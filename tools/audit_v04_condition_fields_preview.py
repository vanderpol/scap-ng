#!/usr/bin/env python3
"""Evidence-backed, read-only 'require + fields' naming pilot for NG 0.4.0.

Does NOT change native wire grammar. Shows which real Test condition AND
groups could use a single 'fields:' mapping with an inherited 'require:'
rather than obsolete 'state_fields_require' or an unnecessary Boolean
'and' wrapper. Genuine duplicate field names/nested Boolean combinations
are NOT silently flattened, and individually scoped field exceptions
remain explicit. Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import zipfile


def read_candidate(path):
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".json"):
                doc=json.loads(z.read(name))
                if (isinstance(doc,dict) and
                    doc.get("assessment",{}).get("mode")=="automated"):
                    yield name,doc


def collect(doc,path,counter,examples):
    for testid,test in doc["assessment"].get("tests",{}).items():
        req=test.get("require")
        if not isinstance(req,dict) or not isinstance(req.get("all_items_must"),list):
            continue
        test_scope=test.get("state_fields_require")
        def walk(obj,location):
            if not isinstance(obj,dict):
                return
            logical=obj.get("and")
            if isinstance(logical,list):
                # Must be one OVAL-State-sized complete AND of simple field
                # predicates. No field aliases, repeats, nested operators or
                # record subfields are silently promoted.
                entries=[]
                for item in logical:
                    if not isinstance(item,dict) or len(item)!=1:
                        break
                    field,predicate=next(iter(item.items()))
                    if not isinstance(predicate,dict) or "record" in predicate:
                        break
                    entries.append((field,predicate))
                if len(entries)==len(logical) and len(entries)>=2:
                    names=[x[0] for x in entries]
                    if len(set(names))!=len(names):
                        counter["duplicate_fields_rejected"]+=1
                    else:
                        scope=obj.get("state_fields_require",test_scope)
                        if scope is not None:
                            kind="group_scope" if "state_fields_require" in obj else "test_scope"
                        elif all("require" in value for _,value in entries):
                            kind="explicit_leaf_scope_only"
                        else:
                            kind="missing_explicit_field_scope_rejected"
                        counter[kind]+=1
                        if len(examples)<16:
                            fields={field:value for field,value in entries}
                            example={"path":path,"test_id":testid,
                                "context":location,"existing_and":obj,
                                "research_only_preferred":{
                                    **({"require":scope} if scope is not None else {}),
                                    "fields":fields},
                                "scope_class":kind}
                            examples.append(example)
            # Don't traverse Object/Filter or Item population by accident:
            # each of these recursion frames is an expected-condition group.
            for key,val in obj.items():
                if key in ("and","or","one","xor","all","any","odd"):
                    if isinstance(val,list):
                        for i,item in enumerate(val):
                            walk(item,location+"."+key+"["+str(i)+"]")
        for i,entry in enumerate(req["all_items_must"]):
            walk(entry,"require.all_items_must["+str(i)+"]")


def audit(archive):
    counts=Counter()
    examples=[]
    documents=0
    tests=0
    for path,doc in read_candidate(archive):
        documents+=1
        tests+=len(doc["assessment"].get("tests",{}))
        collect(doc,path,counts,examples)
    report={
        "status":"NAMING_PREVIEW_ONLY_NO_VERSIONED_AUTHORING_CHANGE",
        "source":"canonical_040_json_generated_authoring",
        "automated_documents":documents,"tests":tests,
        "and_groups_by_requirement_source":dict(sorted(counts.items())),
        "simple_fields_group_candidate_count":(
            counts["group_scope"]+counts["test_scope"]+
            counts["explicit_leaf_scope_only"]),
        "exceptions_explicit_field_only":counts["explicit_leaf_scope_only"],
        "fields_mapping_cannot_be_universally_assumed_for_oval":True,
        "scoped_test_item_existence_unchanged":True,
        "native_schema_changed":False,
        "scanner_runtime_equivalent":False,
        "examples":examples,
    }
    if report["simple_fields_group_candidate_count"]==0:
        raise ValueError("No verified scalar expected-field groups in original source")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-zip",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.candidate_zip)
    a.report.parent.mkdir(exist_ok=True,parents=True)
    a.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="examples"},
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
