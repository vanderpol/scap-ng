#!/usr/bin/env python3
"""Inspect suspicious OVAL-aligned existence/match combinations in pinned 0.3 ZIP.

No content changes or semantic normalization. This is a read-only source audit.
"""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import zipfile

import yaml

TARGETS = {("none","one"), ("none","one_or_more"), ("none","all"), ("one","one")}
EXTENSIONS = (".automated.yaml",)


def audit(zip_path):
    suspects=[]
    pairs=Counter()
    with zipfile.ZipFile(zip_path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Corrupt authoring archive")
        for filename in sorted(archive.namelist()):
            if not (filename.startswith("authoring/") and filename.endswith(EXTENSIONS)):
                continue
            doc=yaml.safe_load(archive.read(filename))
            a=(doc or {}).get("assessment") or {}
            if a.get("mode")!="automated":
                continue
            for test_id,test in (a.get("tests") or {}).items():
                if not isinstance(test,dict):
                    continue
                item_pair=(test.get("existence"),test.get("match"))
                pairs[("items",)+item_pair]+=1
                if item_pair in TARGETS:
                    suspects.append({
                        "scope":"items", "file":filename, "assessment_id":a.get("id"),
                        "test_id":test_id,"existence":item_pair[0],"match":item_pair[1],
                        "assessment_title":a.get("title"),"test":test,
                        "evaluate":a.get("evaluate"),
                        "assessment_provenance":a.get("provenance"),
                        "test_provenance":test.get("provenance"),
                        "has_states":bool(test.get("states")),
                        "source_ids":{k:v for k,v in test.items() if
                            any(token in k.lower() for token in ("source","legacy","oval","origin"))}
                    })
                for idx, state in enumerate(test.get("states") or []):
                    if not isinstance(state,dict) or "field" not in state:
                        continue
                    field_pair=(state.get("existence"),state.get("match"))
                    pairs[("field",)+field_pair]+=1
                    if field_pair in TARGETS:
                        suspects.append({
                            "scope":"field","file":filename,"assessment_id":a.get("id"),
                            "test_id":test_id,"state_index":idx,"field":state.get("field"),
                            "existence":field_pair[0],"match":field_pair[1],
                            "predicate":state,"assessment_title":a.get("title"),
                            "assessment_provenance":a.get("provenance"),
                        })
    return {"source_zip":str(zip_path.name),
            "pairs":{"/".join(map(str,k)):v for k,v in sorted(pairs.items())},
            "suspects":suspects,
            "suspect_count":len(suspects)}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--authoring-zip",type=Path,required=True)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    r=audit(a.authoring_zip)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n")
    for x in r["suspects"]:
        print("SUSPECT",json.dumps({
            "scope":x["scope"],"id":x["assessment_id"],"test":x["test_id"],
            "file":x["file"],"field":x.get("field"),
            "pair":[x["existence"],x["match"]],"has_states":x.get("has_states"),
            "source_ids":x.get("source_ids"),
            "title":x.get("assessment_title")}))
    print("SUSPECT_COUNTS",json.dumps(dict(Counter(
        (x["scope"],x["existence"],x["match"]) for x in r["suspects"]).__iter__()),default=str)
        if False else json.dumps({"/".join(map(str,k)):v for k,v in sorted(Counter(
        (x["scope"],x["existence"],x["match"]) for x in r["suspects"]).items())}))
    print("SUSPECT_TOTAL",r["suspect_count"])
if __name__=="__main__":
    main()
