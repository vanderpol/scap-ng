#!/usr/bin/env python3
"""Safely hoist explicit inherited Test field cardinality to a condition group.

Read a *research-only* 0.4.0 `fields` preview. Exactly one top-level
AND/OR group must contain only complete `fields` conditions, with no
overriding local requirement. Replace the old Test.state_fields_require
with ONE group-level `require` BEFORE `and`/`or`. No item cardinality,
field predicate, actual Boolean operator or operand order is changed.

The migration is bounded to the 16 proven source-backed Tests / 44 child
field groups; all other content is identical and original source can be
restored exactly. NOT an accepted authoring schema. Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile,ZIP_DEFLATED
import yaml


def fingerprint(obj):
    return sha256(json.dumps(obj,sort_keys=True,separators=(",",":"),
                            ensure_ascii=False).encode()).hexdigest()


def migrate_test(test):
    out=deepcopy(test)
    previous=out.get("state_fields_require")
    req=out.get("require")
    if (not isinstance(previous,str) or not isinstance(req,dict)
        or set(req)!={"items","all_items_must"}
        or req.get("items") not in ("one_or_more","may_be_absent")
        or len(req.get("all_items_must",[]))!=1):
        return out,None
    cond=req["all_items_must"][0]
    if not isinstance(cond,dict):
        return out,None
    ops=[k for k in ("and","or") if k in cond]
    if len(ops)!=1 or set(cond)!={ops[0]}:
        return out,None
    op=ops[0]
    children=cond[op]
    if (not isinstance(children,list) or len(children)<2
        or any(not isinstance(c,dict) or set(c)!={"fields"} or
               not isinstance(c["fields"],dict) or len(c["fields"])<2
               or any(not isinstance(name,str) or not name
                      or not isinstance(field,dict) or not field
                      or "record" in field
                      for name,field in c["fields"].items())
               for c in children)):
        return out,None
    # A group-level requirement has exactly the same inherited scope as
    # this simple source Test: all and only these complete State conditions.
    before=fingerprint(test)
    out.pop("state_fields_require")
    out["require"]["all_items_must"][0]={"require":previous,op:children}
    record={"source_test_sha256":before,
            "candidate_test_sha256":fingerprint(out),
            "state_operator":op,
            "fields_children":len(children),
            "source_shared_requirement":previous}
    return out,record


def restore_test(test,record):
    original=deepcopy(test)
    if fingerprint(original)!=record["candidate_test_sha256"]:
        raise ValueError("Group-level requirement/provenance changed after migration")
    req=original["require"]
    group=req["all_items_must"][0]
    op=record["state_operator"]
    if (set(group)!={"require",op} or group["require"]!=record["source_shared_requirement"]
        or len(group[op])!=record["fields_children"]):
        raise ValueError("Original AND/OR State group and field cardinality not recoverable")
    original["state_fields_require"]=group["require"]
    req["all_items_must"][0]={op:deepcopy(group[op])}
    if fingerprint(original)!=record["source_test_sha256"]:
        raise ValueError("Original Test cannot be exactly reconstructed")
    return original


def migrate_document(source):
    dest=deepcopy(source)
    a=dest.get("assessment") if isinstance(dest,dict) else None
    changed=[]
    if isinstance(a,dict) and a.get("mode")=="automated":
        for testid,test in list((a.get("tests") or {}).items()):
            new,proof=migrate_test(test)
            if proof:
                a["tests"][testid]=new
                changed.append({"test_id":testid,**proof})
    for record in changed:
        testid=record["test_id"]
        restored=restore_test(dest["assessment"]["tests"][testid],record)
        if restored!=source["assessment"]["tests"][testid]:
            raise ValueError("Source Test changed during hoist")
    return dest,changed


def rewrite_archive(original_zip,candidate_zip,candidate_yaml,report_path):
    totals=Counter()
    changed=[]
    with ZipFile(original_zip) as source, ZipFile(candidate_zip,"w",ZIP_DEFLATED) as output, \
         ZipFile(candidate_yaml,"w",ZIP_DEFLATED) as yaml_output:
        for name in source.namelist():
            if not name.startswith("authoring/") or not name.endswith(".json"):
                raise ValueError("Unexpected non-authoring ZIP member in candidate")
            raw=source.read(name)
            doc=json.loads(raw)
            new,ledger=migrate_document(doc)
            totals["documents"]+=1
            if ledger:
                totals["affected_documents"]+=1
                totals["tests"]+=len(ledger)
                totals["fields_children"]+=sum(x["fields_children"] for x in ledger)
                changed.append({"source_file":name,"tests":ledger})
                payload=(json.dumps(new,indent=2,ensure_ascii=False)+"\n").encode()
            else:
                payload=raw
            output.writestr(name,payload)
            authored=yaml.safe_dump(new,sort_keys=False,allow_unicode=True).encode()
            if yaml.safe_load(authored)!=new:
                raise ValueError("YAML serialization changed group scope at "+name)
            yaml_output.writestr(name.removesuffix(".json")+".yaml",authored)
    expected={"documents":4001,"affected_documents":14,
              "tests":16,"fields_children":44}
    # Test sites and document counts are separate source-pinned invariants.
    if {k:totals[k] for k in expected}!=expected:
        raise ValueError("Source-inherited group census drift: "+str(dict(totals)))
    result={
      "status":"RESEARCH_INHERITED_REQUIREMENT_HOIST_EXACT_INVERSE",
      "counts":dict(totals),
      "changed":changed,
      "source_sha256":sha256(original_zip.read_bytes()).hexdigest(),
      "candidate_sha256":sha256(candidate_zip.read_bytes()).hexdigest(),
      "candidate_yaml_sha256":sha256(candidate_yaml.read_bytes()).hexdigest(),
      "schema_promoted":False,
      "scanner_semantics_proven":False,
    }
    report_path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source-json",type=Path,required=True)
    p.add_argument("--candidate-json",type=Path,required=True)
    p.add_argument("--candidate-yaml",type=Path,required=True)
    p.add_argument("--proof",type=Path,required=True)
    a=p.parse_args()
    a.candidate_json.parent.mkdir(parents=True,exist_ok=True)
    a.candidate_yaml.parent.mkdir(parents=True,exist_ok=True)
    report=rewrite_archive(a.source_json,a.candidate_json,a.candidate_yaml,a.proof)
    print(json.dumps({k:v for k,v in report.items() if k!="changed"},indent=2))


if __name__=="__main__":
    main()
