#!/usr/bin/env python3
"""Original OVAL source proof for Enterprise/EnterpriseS whole-State OR.

Use the original pinned Windows 11 OVAL, not converted NG or reverse source
AST. Verify original Test state_operator, check, check_existence, two
separately referenced complete registry States and their conditions. Then
verify native original and scope-normalized candidates preserve these
structural boundaries. Refs #248 #239.
"""
from __future__ import annotations
import argparse,hashlib,io,json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from migrate_v04_states_match_to_logic import migrate,restore

OVAL="http://oval.mitre.org/XMLSchema/oval-definitions-5"
WIN=OVAL+"#windows"
SOURCE_BLOB="712cc3176b1e44616aaf2f3ba5e62b299ad0643c"


def by_id(root):
    return {node.get("id"):node for node in root.iter() if node.get("id")}


def proof(archive,assessment):
    raw=Path(archive).read_bytes()
    git_blob=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if git_blob!=SOURCE_BLOB:
        raise ValueError("NIWC original Windows 11 OVAL ZIP does not match SHA-pinned source")
    a=assessment["assessment"]
    tests=a["tests"]
    name="editionid-enterprise-or-enterprises-test"
    if name not in tests or len(tests)!=1:
        raise ValueError("Expected exactly one named registry Test")
    t=tests[name]
    if t.get("capability")!="windows.registry" or t.get("states_match")!="any":
        raise ValueError("Original NG source does not retain OR-ed complete State semantics")
    req=t["require"]
    if req.get("items")!="one_or_more" or len(req.get("all_items_must",[]))!=2:
        raise ValueError("Original NG requires two States for each nonempty Item")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=[x for x in z.namelist() if x.endswith(".xml")]
        if len(members)!=1:
            raise ValueError("Original OVAL source datastream XML member ambiguous")
        root=ET.fromstring(z.read(members[0]))
    candidates=[node for node in root.iter() if node.tag=="{"+WIN+"}registry_test"
                and node.get("comment")==t.get("test_title")]
    if len(candidates)!=1:
        raise ValueError("Original OVAL registry Test title is missing or not unique: "
                         +str(t.get("test_title")))
    oval_test=candidates[0]
    fields=[x for x in oval_test if x.tag=="{"+WIN+"}state"]
    if (oval_test.get("state_operator","AND")!="OR"
            or oval_test.get("check")!="all"
            or oval_test.get("check_existence","at_least_one_exists")!="at_least_one_exists"
            or len(fields)!=2):
        raise ValueError("Pinned original OVAL Test State/Item matching differs from NG")
    ids=by_id(root)
    expected_values=["Enterprise","EnterpriseS"]
    state_details=[]
    for index,ref in enumerate(fields):
        sid=ref.get("state_ref")
        state=ids.get(sid)
        if state is None or state.tag!="{"+WIN+"}registry_state":
            raise ValueError("Original OVAL registry State ref missing/wrong capability: "+str(sid))
        if state.get("operator","AND")!="AND":
            raise ValueError("Original registry State field operator was NOT AND")
        children=[x for x in state if x.tag.startswith("{"+WIN+"}")]
        fields_by_name={x.tag.rsplit("}",1)[-1]:x for x in children}
        if set(fields_by_name)!={"type","value"} or len(children)!=2:
            raise ValueError("Original registry State not a complete type+value pair")
        original_value=(fields_by_name["value"].text or "").strip()
        if (original_value!=expected_values[index]
                or fields_by_name["value"].get("operation","equals")!="equals"):
            raise ValueError("Original State operand/value differs from published NG")
        converted=req["all_items_must"][index]
        if (set(converted)!={"and"} or len(converted["and"])!=2
                or converted["and"][0].get("type",{}).get("equals")!="string"
                or converted["and"][1].get("value",{}).get("equals")!=original_value):
            raise ValueError("Native State does not match original grouped registry field predicates")
        state_details.append({"state_id":sid,"original_field_operator":"AND",
                              "source_value":original_value,
                              "native_complete_condition_index":index})
    rewritten,ledger=migrate(assessment)
    if len(ledger)!=1:
        raise ValueError("Expected exactly one normalized OVAL OR Test")
    proposed=rewritten["assessment"]["tests"][name]
    if (proposed.get("states_match") is not None
            or len(proposed["require"]["all_items_must"])!=1
            or set(proposed["require"]["all_items_must"][0])!={"or"}
            or restore(rewritten,ledger)!=assessment):
        raise ValueError("Scope-aware OR normalization changed original OVAL structure")
    return {
        "status":"SOURCE_OVAL_WHOLE_STATE_OR_PRESERVED",
        "source_original_blob_sha1":git_blob,
        "source_test_id":oval_test.get("id"),
        "source_test_state_operator":"OR",
        "source_check":"all",
        "source_check_existence":"at_least_one_exists",
        "original_complete_states":state_details,
        "normalized_test_or_children":2,
        "native_test_sha256":ledger[0]["source_test_sha256"],
        "normalized_test_sha256":ledger[0]["normalized_test_sha256"],
        "old_authoring_exactly_recovered":True,
        "scanner_semantics_proven":False,
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--original-win11-zip",type=Path,required=True)
    p.add_argument("--native-assessment",type=Path,required=True)
    p.add_argument("--report",type=Path,required=True)
    a=p.parse_args()
    doc=json.loads(a.native_assessment.read_text())
    result=proof(a.original_win11_zip,doc)
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
