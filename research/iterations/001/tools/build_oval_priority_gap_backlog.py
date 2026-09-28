#!/usr/bin/env python3
"""Prioritize OVAL semantic coverage gaps for the current SCAP-NG target platforms."""
from __future__ import annotations
import argparse, json
from collections import defaultdict
from pathlib import Path

PRIORITY_NAMESPACES = {
    "http://oval.mitre.org/XMLSchema/oval-definitions-5#independent": 1,
    "http://oval.mitre.org/XMLSchema/oval-definitions-5#linux": 1,
    "http://oval.mitre.org/XMLSchema/oval-definitions-5#unix": 1,
    "http://oval.mitre.org/XMLSchema/oval-definitions-5#windows": 1,
}

STATUS_PRIORITY = {
    "production_only": 0,
    "conformance_and_production": 1,
    "conformance_only": 2,
    "schema_only": 3,
}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("ledger",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    d=json.loads(args.ledger.read_text(encoding="utf-8"))

    rows=[]
    for category in ("tests","objects","states"):
        for item in d["ledger"][category]:
            ns=item["namespace"]
            if ns not in PRIORITY_NAMESPACES:
                continue
            row={"category":category,**item}
            if row.get("status")=="production_only" and row.get("deprecated"):
                row["recommended_treatment"]="source_content_remediation_blocker"
            elif row.get("status")=="production_only":
                row["recommended_treatment"]="focused_conformance_and_native_mapping"
            elif row.get("status")=="schema_only" and row.get("deprecated"):
                row["recommended_treatment"]="defer_unless_encountered_in_migration"
            elif row.get("status")=="schema_only":
                row["recommended_treatment"]="coverage_backlog"
            else:
                row["recommended_treatment"]="maintain_evidence"
            row["priority_key"]=[
                STATUS_PRIORITY[item["status"]],
                -int(item.get("niwc_priority_stig_count",0)),
                category,
                item["name"],
            ]
            rows.append(row)

    rows.sort(key=lambda x:tuple(x["priority_key"]))
    by_status=defaultdict(list)
    for row in rows:
        by_status[row["status"]].append(row)

    out={
        "format":"scap-ng-oval-priority-gap-backlog-0.1",
        "scope":"independent-linux-unix-windows",
        "priority_policy":[
            "production-only constructs first",
            "then constructs supported by both conformance and production evidence",
            "then conformance-only constructs",
            "then schema-only constructs",
            "within a status, higher NIWC occurrence count first",
            "deprecated OVAL test families are outside SCAP-NG and are source-remediation blockers, not runtime implementation backlog",
        ],
        "counts":{k:len(v) for k,v in sorted(by_status.items())},
        "production_only":by_status.get("production_only",[]),
        "schema_only":by_status.get("schema_only",[]),
        "all_priority_rows":rows,
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "counts":out["counts"],
        "production_only":[
            f'{x["category"]}:{x["name"]}' for x in out["production_only"]
        ],
        "schema_only_count":len(out["schema_only"]),
    },indent=2,sort_keys=True))

if __name__=="__main__":
    main()
