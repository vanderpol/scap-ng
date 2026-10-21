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

from migrate_v04_states_match_to_logic import migrate


def read_candidate(path):
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            if name.endswith(".json"):
                doc=json.loads(z.read(name))
                if (isinstance(doc,dict) and
                    doc.get("assessment",{}).get("mode")=="automated"):
                    yield name,doc


def collect(doc,path,counter,examples,original_and_tests):
    for testid,test in doc["assessment"].get("tests",{}).items():
        req=test.get("require")
        if not isinstance(req,dict) or not isinstance(req.get("all_items_must"),list):
            continue
        test_scope=test.get("state_fields_require")
        def walk(obj,location):
            if not isinstance(obj,dict):
                return
            logical=obj.get("and")
            is_original_test_state_and = (testid in original_and_tests
                                          and location=="require.all_items_must[0]")
            if isinstance(logical,list) and is_original_test_state_and:
                # This whole AND combines separate OVAL States on an Item.
                # It MUST NOT be relabeled as one State's fields, even if
                # every State happens to use a distinct field name.
                counter["whole_state_and_groups_preserved"]+=1
                single=[next(iter(x)) for x in logical
                        if isinstance(x,dict) and len(x)==1]
                if len(single)==len(logical) and len(set(single))!=len(single):
                    if any(k in ("and","or","one","odd","xor","all","any") for k in single):
                        counter["whole_state_and_repeated_nested_group_keys"]+=1
                    else:
                        counter["whole_state_and_duplicate_fields"]+=1
                if len(examples)<16:
                    examples.append({"path":path,"test_id":testid,
                        "context":location,"scope_class":"whole_state_and_must_keep",
                        "original_states":len(logical),"no_fields_flatten":True})
            elif isinstance(logical,list):
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


def audit(archive,original_archive):
    counts=Counter()
    examples=[]
    documents=0
    tests=0
    originals={path:data for path,data in read_candidate(original_archive)}
    actual=set()
    for path,doc in read_candidate(archive):
        documents+=1
        tests+=len(doc["assessment"].get("tests",{}))
        old=originals.get(path)
        if old is None:
            raise ValueError("Missing original 0.4 Assessment: "+path)
        expected,ledger=migrate(old)
        if expected!=doc:
            raise ValueError("Proposed 0.4 AND/OR document does not match exact old authoring: "+path)
        # A whole-State AND was introduced by the source-aware migrator.
        # Existing field-level AND expressions are NOT this same level.
        original_and_tests={row["test_id"] for row in ledger
                            if row["source_state_operator"]=="all"}
        counts["migrated_whole_state_and_tests"]+=len(original_and_tests)
        collect(doc,path,counts,examples,original_and_tests)
        actual.add(path)
    if set(originals)!=actual:
        raise ValueError("Named current JSON Assessments have missing original sources")
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
        "source_original_state_boundary_verified_by_inverse":True,
        "scanner_runtime_equivalent":False,
        "examples":examples,
    }
    if report["simple_fields_group_candidate_count"]==0:
        raise ValueError("No verified scalar expected-field groups in original source")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-zip",type=Path,required=True)
    p.add_argument("--canonical-source-zip",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.candidate_zip,a.canonical_source_zip)
    a.report.parent.mkdir(exist_ok=True,parents=True)
    a.report.write_text(json.dumps(result,sort_keys=True,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k!="examples"},
                     sort_keys=True,indent=2))


if __name__=="__main__":
    main()
