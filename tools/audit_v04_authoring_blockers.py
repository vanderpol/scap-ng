#!/usr/bin/env python3
"""Audit 0.4.0 six-STIG authoring for actual normative-schema blockers.

This is an inventory, not a declaration that the documents pass JSON Schema.
Checks both YAML/JSON archives, key semantic invariants and source forms.
"""
import argparse, collections, json, pathlib, zipfile
import yaml

def check(archive):
    counts=collections.Counter()
    examples={}
    with zipfile.ZipFile(archive) as z:
        files=sorted(n for n in z.namelist() if n.startswith("authoring/") and n.endswith((".json",".yaml")))
        for path in files:
            d=yaml.safe_load(z.read(path)) if path.endswith(".yaml") else json.loads(z.read(path))
            a=d.get("assessment")
            if not isinstance(a,dict) or a.get("mode")!="automated": continue
            for id,t in (a.get("tests") or {}).items():
                if not isinstance(t,dict):continue
                def hit(key):
                    counts[key]+=1
                    if len(examples.get(key,[]))<6:examples.setdefault(key,[]).append({"path":path,"test":id})
                obj=t.get("object")
                if isinstance(obj,dict):
                    if "capability" in obj:hit("inline_capability_still_declared")
                    elif not t.get("capability"):hit("inline_capability_missing_test_source")
                req=t.get("require")
                if isinstance(req,dict):
                    if set(req)=={"items"}:
                        hit("native_presence_only_tests")
                        if "states" in t or "states_match" in t:hit("presence_only_with_legacy_states")
                    elif set(req)=={"items","all_items_must"}:
                        if not isinstance(req.get("all_items_must"),list):hit("invalid_all_items_must_shape")
                        else:
                            hit("native_all_items_must_tests")
                            if t.get("states") is not None:hit("both_states_and_all_items_must")
                    else:hit("unrecognized_structured_requirement")
                elif isinstance(req,str):
                    hit("legacy_string_require_tests")
                    hit("legacy_"+req)
                else:hit("missing_require")
                if "collected_items_require" in t:hit("stale_collected_items_require")
                if "states" in t:hit("legacy_states")
                if "states_match" in t:hit("legacy_states_match")
                if "state_fields_require" in t:hit("legacy_top_level_field_require")
    return {"archive":str(archive),"documents":len(files),"counts":dict(sorted(counts.items())),"examples":examples}
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--archive",type=pathlib.Path,required=True)
    p.add_argument("--report",type=pathlib.Path,required=True);a=p.parse_args()
    r=check(a.archive);a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps(r,indent=2)+"\n")
    print(json.dumps({"documents":r["documents"],"counts":r["counts"]},indent=2))
    assert r["documents"]==4001,"Unexpected six-STIG archive closure"
    assert not r["counts"].get("inline_capability_still_declared"),"Inline object capability was not normalized"
    assert not r["counts"].get("stale_collected_items_require"),"Stale Test requirement key"
    # Explicitly track the unresolved migration scope; green source roundtrips
    # must not be mistaken for full canonical-schema conformance.
    actual=r["counts"]
    assert actual.get("native_all_items_must_tests")==816, "Source population or conversion changed"
    assert actual.get("native_presence_only_tests")==388, "Source-derived presence-only migration changed"
    assert actual.get("legacy_string_require_tests")==171, "Remaining legacy requirement population changed; review migration"
    assert actual.get("legacy_states")==172, "Unconverted State population changed; review migration"
    assert actual.get("legacy_top_level_field_require")==108, "Unconverted field-level requirement count changed"
    assert actual.get("legacy_states_match")==128, "Unconverted State aggregate population changed"

