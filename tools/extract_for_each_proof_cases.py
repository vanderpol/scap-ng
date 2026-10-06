#!/usr/bin/env python3
"""Extract exact per-rule OVAL closures for scoped-iteration proof cases."""
from __future__ import annotations
import argparse, json, shutil
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("--output-dir",required=True)
    args=ap.parse_args()
    report=json.loads(Path(args.audit).read_text())
    out=Path(args.output_dir); out.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for row in report.get("candidates",[]):
        risks=set(row.get("rewrite_risk") or [])
        if not (risks or row.get("nested_dependency_paths") or row.get("intra_variable_multi_field_sources")):
            continue
        src=Path(row["file"])
        if not src.exists():
            continue
        rid=row.get("rule_id") or src.parent.name
        dest=out/f"{rid}.oval.xml"
        shutil.copyfile(src,dest)
        manifest.append({
            "rule_id":rid,
            "title":row.get("title"),
            "source":str(src),
            "file":dest.name,
            "rewrite_risk":row.get("rewrite_risk") or [],
            "nested_dependency_paths":row.get("nested_dependency_paths") or [],
            "same_item_field_sources":row.get("intra_variable_multi_field_sources") or [],
        })
    (out/"manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"proof_cases":len(manifest)},indent=2))

if __name__=="__main__":
    main()
