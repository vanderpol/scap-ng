#!/usr/bin/env python3
"""Preview lossless OVAL State-aggregation -> explicit AND/OR in SCAP-NG 0.4.

Narrowly migrates original Test 'states_match: any/all' ONLY when it
combines >=2 complete expected conditions inside a structured
'require: {items, all_items_must}' expression. An OR between whole
conditions must not be confused with OR between fields or across Items.

No vocabulary change to fields/state_fields_require or field predicates.
No handling of the five exceptional legacy scalar-requirement Tests.
Every changed Test carries exact inverse proof; no generated candidates
are declared source-execution equivalent without independent checks.

Refs #248 #239.
"""
from __future__ import annotations
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

QUALIFIERS={"any":"or","all":"and"}
OLD="states_match"
LIST="all_items_must"


def _canonical_sha(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",",":"),
                                      ensure_ascii=False).encode()).hexdigest()


def migrate(doc):
    candidate=deepcopy(doc)
    a=candidate.get("assessment") if isinstance(candidate,dict) else None
    if not isinstance(a,dict) or a.get("mode")!="automated":
        return candidate,[]
    changed=[]
    for tid,test in (a.get("tests") or {}).items():
        scope=test.get(OLD)
        if scope not in QUALIFIERS:
            continue
        req=test.get("require")
        # This research migrator must never reinterpret uncommon legacy
        # string requirements or Tests with separate 'states' collections.
        if not isinstance(req,dict) or "states" in test:
            continue
        if set(req)!={"items",LIST} or req["items"] not in (
                "one_or_more","may_be_absent"):
            raise ValueError("Unsafe unsupported Test matching/Item boundary: "+tid)
        clauses=req[LIST]
        if not isinstance(clauses,list) or len(clauses)<2 or not all(
                isinstance(x,dict) and x for x in clauses):
            raise ValueError("Cannot prove OR/AND between complete conditions: "+tid)
        if any(OLD in str(clause) for clause in clauses):
            raise ValueError("Nested State matching semantics not validated: "+tid)
        original_test=deepcopy(test)
        test["require"][LIST]=[{QUALIFIERS[scope]:deepcopy(clauses)}]
        del test[OLD]
        changed.append({"test_id":tid,
                       "source_state_operator":scope,
                       "new_condition_operator":QUALIFIERS[scope],
                       "source_complete_conditions":len(clauses),
                       "source_test_sha256":_canonical_sha(original_test),
                       "normalized_test_sha256":_canonical_sha(test)})
    return candidate,changed


def restore(candidate,ledger):
    original=deepcopy(candidate)
    a=original.get("assessment") if isinstance(original,dict) else None
    if not ledger:
        return original
    if not isinstance(a,dict) or a.get("mode")!="automated":
        raise ValueError("Proof ledger cannot modify non-automated Assessment")
    for item in ledger:
        tid=item["test_id"]
        test=a["tests"][tid]
        if _canonical_sha(test)!=item["normalized_test_sha256"]:
            raise ValueError("Changed NG logical condition cannot be inverted: "+tid)
        requirement=test["require"]
        clauses=requirement[LIST]
        operator=item["new_condition_operator"]
        if (len(clauses)!=1 or set(clauses[0])!={operator}
                or not isinstance(clauses[0][operator],list)
                or len(clauses[0][operator])!=item["source_complete_conditions"]
                or test.get(OLD) is not None):
            raise ValueError("Bad normalized State operator scope: "+tid)
        requirement[LIST]=clauses[0][operator]
        test[OLD]=item["source_state_operator"]
        if _canonical_sha(test)!=item["source_test_sha256"]:
            raise ValueError("Inverse changed source Test semantics: "+tid)
    return original


def validate_exact_inverse(before,after,ledger):
    if restore(after,ledger)!=before:
        raise ValueError("State aggregation normalization not completely reversible")
    check,reproof=migrate(before)
    if check!=after or reproof!=ledger:
        raise ValueError("State aggregation normalization not deterministic")
    return True


def audit_archive(archive,output=None):
    counts=Counter()
    examples=[]
    normalized_records={}
    for path in archive.namelist():
        if not path.endswith(".json"):
            continue
        raw=archive.read(path)
        data=json.loads(raw)
        if not isinstance(data,dict) or "assessment" not in data:
            continue
        updated,ledger=migrate(data)
        validate_exact_inverse(data,updated,ledger)
        if ledger:
            normalized_records[path]=updated
            for row in ledger:
                counts[row["source_state_operator"]]+=1
                if len(examples)<16:
                    examples.append({"path":path,**row})
    if not normalized_records:
        raise ValueError("No source-backed structured State alternatives found")
    report={"status":"EXACT_INVERSE_PREVIEW_NOT_SOURCE_SCANNER_PARITY",
            "counts":dict(sorted(counts.items())),
            "affected_assessments":len(normalized_records),
            "affected_tests":sum(counts.values()),
            "original_source_oval_unchanged":True,
            "fields_naming_unchanged":True,
            "published_release_archives_unchanged":True,
            "sample_changed_sites":examples}
    if output is not None:
        out=Path(output)
        out.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(out,"w",compression=zipfile.ZIP_DEFLATED) as z:
            for path,updated in sorted(normalized_records.items()):
                z.writestr(path,json.dumps(updated,indent=2,ensure_ascii=False)+"\n")
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical-zip",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    p.add_argument("--candidate-changed-only",type=Path)
    p.add_argument("--expected-tests",type=int,default=123)
    a=p.parse_args()
    with zipfile.ZipFile(a.canonical_zip) as z:
        report=audit_archive(z,a.candidate_changed_only)
    if report["affected_tests"]!=a.expected_tests:
        raise ValueError(f"Corpus drift: expected {a.expected_tests} structured State matching Tests; "
                         f"got {report['affected_tests']}")
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="sample_changed_sites"},
                     indent=2,sort_keys=True))


if __name__=="__main__":
    main()
