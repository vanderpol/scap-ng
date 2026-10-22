#!/usr/bin/env python3
"""Produce a source-backed, reviewable ledger for every unconverted 0.4 Test.

One row per remaining legacy Test, preserving the exact Test source and its
capability, alternative-State operator and field-cardinality annotations.
This is an inventory, NOT approval of semantic rewriting.
"""
import argparse, collections, json, pathlib, zipfile
import yaml

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--archive",type=pathlib.Path,required=True)
    p.add_argument("--out",type=pathlib.Path,required=True)
    a=p.parse_args()
    entries=[]
    with zipfile.ZipFile(a.archive) as z:
        for path in sorted(z.namelist()):
            if not path.startswith("authoring/") or not path.endswith((".json",".yaml")):continue
            doc=yaml.safe_load(z.read(path)) if path.endswith(".yaml") else json.loads(z.read(path))
            assess=doc.get("assessment")
            if not isinstance(assess,dict) or assess.get("mode")!="automated":continue
            for tid,t in (assess.get("tests") or {}).items():
                if not isinstance(t.get("require"),str):continue
                states=t.get("states") or []
                reasons=[]
                if states:reasons.append("state_comparisons")
                if t.get("states_match"):reasons.append("alternative_state_aggregation")
                if t.get("state_fields_require"):reasons.append("field_cardinality")
                if t["require"].startswith("all_exist"):reasons.append("all_exist_cardinality")
                if "only_one_matches" in t["require"]:reasons.append("exactly_one_matches")
                if "some_match" in t["require"]:reasons.append("some_match")
                if "none_match" in t["require"]:reasons.append("negative_match")
                if not reasons:reasons.append("other")
                entries.append({"assessment":assess.get("id"),"path":path,
                    "test":tid,"capability":t.get("capability"),
                    "require":t["require"],"states_match":t.get("states_match"),
                    "state_fields_require":t.get("state_fields_require"),
                    "reasons":reasons,"source_test":t})
    n=len(entries)
    # The canonical field-requirement migration intentionally leaves 221
    # source-exact exceptions, including 47 all-match/record-sensitive cases.
    if n!=221:raise ValueError(f"Review baseline changed: {n} residual Tests instead of 221")
    a.out.parent.mkdir(parents=True,exist_ok=True)
    counts=dict(sorted(collections.Counter(x["require"] for x in entries).items()))
    reasons=dict(sorted(collections.Counter(reason for x in entries for reason in x["reasons"]).items()))
    report={"status":"needs-semantic-review","records":n,
            "warning":"Source identity only; neither OVAL six-state parity nor native-schema conformance is established.",
            "by_requirement":counts,"by_reason":reasons,"entries":entries}
    a.out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"records":n,"by_requirement":counts,"by_reason":reasons},indent=2))
if __name__=="__main__":main()
