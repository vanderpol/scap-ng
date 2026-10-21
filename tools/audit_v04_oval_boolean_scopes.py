#!/usr/bin/env python3
"""Audit original OVAL 5.12.3 Boolean scopes, not an NG syntax promotion.

Three independent original-OVAL axes are kept distinct:
* Test check / check_existence -- across collected Items;
* Test state_operator -- between complete referenced States, per Item;
* State operator -- between the State's field entities, per Item.

This audit inventories real multi-State, multi-field, ONE/XOR, and repeated
field situations where an attractive YAML map could silently lose semantics.
It reads upstream original XML, NOT transformed NG authoring. Refs #248 #239.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha1, sha256
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

OD = "http://oval.mitre.org/XMLSchema/oval-definitions-5"
SOURCE_BLOB_SHA1 = "712cc3176b1e44616aaf2f3ba5e62b299ad0643c"
OPS = ("AND", "OR", "ONE", "XOR")


def bare(tag):
    return tag.rsplit("}", 1)[-1]


def example(store, key, payload, max_per_key=6):
    if len(store.setdefault(key, [])) < max_per_key:
        store[key].append(payload)


def examine_oval(root, source, counts, samples):
    if root.tag != "{" + OD + "}oval_definitions":
        raise ValueError(source + ": expected an OVAL Definitions component")
    sections = {}
    for key in ("definitions", "tests", "objects", "states", "variables"):
        parent = root.find("{" + OD + "}" + key)
        sections[key] = [] if parent is None else list(parent)
        counts["source_" + key] += len(sections[key])
    states = {}
    for st in sections["states"]:
        sid = st.get("id")
        if not sid or sid in states:
            raise ValueError(source + ": duplicate or missing State ID")
        states[sid] = st
    counts["source_documents"] += 1
    for test in sections["tests"]:
        test_id = test.get("id")
        if not test_id:
            raise ValueError(source + ": Test missing ID")
        check = test.get("check")
        exists = test.get("check_existence", "at_least_one_exists")
        counts["test_check:" + str(check)] += 1
        counts["test_existence:" + str(exists)] += 1
        refs = [elem.get("state_ref") for elem in test
                if bare(elem.tag) == "state"]
        if any(not rid or rid not in states for rid in refs):
            raise ValueError(source + ": Test references missing State")
        if refs:
            sop = test.get("state_operator", "AND")
            if sop not in OPS:
                raise ValueError(source + ": unknown Test state_operator " + sop)
            counts["test_state_operator:" + sop] += 1
            if len(refs) > 1:
                counts["test_multiple_states"] += 1
                example(samples, "multiple_state_refs", {
                    "source":source, "test":test_id, "state_operator":sop,
                    "states":refs[:10]})
            if len(refs) > 2 and sop in ("ONE", "XOR"):
                counts["test_three_plus_ONE_XOR"] += 1
                example(samples, "multi_state_one_xor", {
                    "source":source, "test":test_id,
                    "state_operator":sop, "states":refs[:10]})
        elif "state_operator" in test:
            counts["statefree_test_explicit_operator"] += 1
        for ref in refs:
            state = states[ref]
            op = state.get("operator", "AND")
            if op not in OPS:
                raise ValueError(source + ": unknown State field operator " + op)
            fields = [bare(e.tag) for e in state
                      if bare(e.tag) not in ("notes", "Signature")]
            if len(fields) > 1:
                counts["referenced_multi_field_states"] += 1
                example(samples, "multiple_fields_in_one_state", {
                    "source":source, "test":test_id, "state":ref,
                    "state_operator":op, "fields":fields[:16]})
            if op != "AND":
                counts["referenced_nondefault_field_operator:" + op] += 1
                example(samples, "state_field_operator_" + op.lower(), {
                    "source":source, "test":test_id, "state":ref,
                    "state_operator":op,"fields":fields[:16]})
            repeated=[name for name,num in Counter(fields).items() if num>1]
            if repeated:
                counts["referenced_repeated_field_names"] += 1
                example(samples, "same_field_name_repeated_in_state", {
                    "source":source, "test":test_id, "state":ref,
                    "state_operator":op,"repeat_fields":repeated,
                    "fields":fields[:16]})
    # Count all source States separately, including unreferenced source
    # objects. This avoids guessing whether a missing Test is innocuous.
    for state in sections["states"]:
        op=state.get("operator","AND")
        if op not in OPS:
            raise ValueError(source + ": unsupported State operator " + op)
        counts["state_operator:" + op] += 1
        fields=[bare(n.tag) for n in state
                if bare(n.tag) not in ("notes","Signature")]
        if len(fields)>1:
            counts["states_multiple_fields"]+=1
        if any(count>1 for count in Counter(fields).values()):
            counts["states_repeated_field_names"]+=1


def audit(self_root,win_zip):
    counts=Counter()
    examples={}
    source_files=sorted(self_root.rglob("*.xml"))
    for file in source_files:
        root=ET.fromstring(file.read_bytes())
        examine_oval(root,file.relative_to(self_root).as_posix(),counts,examples)
    if len(source_files)!=144:
        raise ValueError("Pinned original Self-Assertion file denominator changed")
    if counts["source_definitions"]!=167 or counts["source_tests"]!=785:
        raise ValueError("Pinned original Self-Assertion Definition/Test inventory changed")
    per_source={"self_assertion_files":len(source_files),
                "original_self_assertion_definitions":167,
                "original_self_assertion_tests":785}
    if win_zip is not None:
        raw=win_zip.read_bytes()
        blob=sha1(b"blob "+str(len(raw)).encode()+b"\x00"+raw).hexdigest()
        if blob!=SOURCE_BLOB_SHA1:
            raise ValueError("Original Win11 OVAL archive blob pin changed")
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            members=[n for n in z.namelist() if n.endswith(".xml")]
            if len(members)!=1:
                raise ValueError("Original Win11 OVAL ZIP XML member ambiguous")
            payload=z.read(members[0])
        datastream=ET.fromstring(payload)
        roots=[n for n in datastream.iter()
               if n.tag=="{"+OD+"}oval_definitions"]
        if not roots:
            raise ValueError("Pinned Win11 datastream lacks original OVAL")
        for i,root in enumerate(roots):
            examine_oval(root,"win11-original/oval-component-"+str(i),
                         counts,examples)
        per_source["win11_archive_sha256"]=sha256(raw).hexdigest()
        per_source["win11_oval_components"]=len(roots)
    return {
        "status":"ORIGINAL_OVAL_BOOLEAN_SCOPE_INVENTORY_NOT_NG_EQUIVALENCE",
        "source_pins":{
            "self_assertion":"e3538595c5083b9c34d937a81d319234df9bbfaa",
            "windows11_blob":SOURCE_BLOB_SHA1 if win_zip is not None else None,
        },
        "scope_source_counts":dict(sorted(counts.items())),
        "source_coverage":per_source,
        "real_source_examples":examples,
        "conclusions_not_proven":[
            "0.4 XML conversion completeness",
            "0.4 ability to represent every repeated field",
            "scanner evaluator six-state parity",
            "schema promotion of fields_operator/fields/matching_items",
        ],
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--self-assertion-original",type=Path,required=True)
    p.add_argument("--win11-original-zip",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    result=audit(a.self_assertion_original,a.win11_original_zip)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":result["status"],
          "source_coverage":result["source_coverage"],
          "scope_source_counts":result["scope_source_counts"]},
          indent=2,sort_keys=True))


if __name__=="__main__":
    main()
