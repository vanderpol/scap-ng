#!/usr/bin/env python3
"""Verify every source root Definition against roots in an aggregate regenerated OVAL."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/"tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0,str(TOOLS))
from scap_ng_roundtrip_v003.compare_oval_semantics import compare

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True)
    ap.add_argument("--regenerated",type=Path,required=True)
    ap.add_argument("--mapping-report",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    mapping=json.loads(args.mapping_report.read_text(encoding="utf-8"))
    rows=[]
    equal=0
    for item in mapping.get("results",[]):
        source_id=item.get("definition_id")
        regen_id=item.get("regenerated_definition_id")
        if not source_id or not regen_id:
            rows.append({
                "definition_id":source_id,
                "equal":False,
                "error":"missing regenerated root mapping",
            })
            continue
        try:
            result=compare(
                args.source,args.regenerated,
                source_root=source_id,regenerated_root=regen_id,root_only=True
            )
            ok=bool(result["equal"])
            row={"definition_id":source_id,"regenerated_definition_id":regen_id,"equal":ok}
            if not ok:
                row["source_definition"]=result.get("source_definition")
                row["regenerated_definition"]=result.get("regenerated_definition")
        except Exception as exc:
            ok=False
            row={
                "definition_id":source_id,
                "regenerated_definition_id":regen_id,
                "equal":False,
                "error":str(exc),
            }
        equal+=int(ok)
        rows.append(row)

    failures=[x for x in rows if not x["equal"]]
    report={
        "definitions":len(rows),
        "semantic_equal":equal,
        "failures":len(failures),
        "failure_details":failures,
        "results":rows,
    }
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="results"},indent=2,sort_keys=True))
    return 1 if failures else 0

if __name__=="__main__":
    raise SystemExit(main())
