#!/usr/bin/env python3
"""Build an OVAL 5.12.3 coverage ledger from schema, conformance, and production evidence."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def keyed(rows):
    return {f'{x.get("namespace","")}#{x.get("name","")}':x for x in rows}


def classify(key, schema_row, self_counts, prod_counts, prod_examples):
    s=self_counts.get(key,0)
    p=prod_counts.get(key,0)
    if s and p:
        status="conformance_and_production"
    elif s:
        status="conformance_only"
    elif p:
        status="production_only"
    else:
        status="schema_only"
    namespace,name=key.rsplit("#",1)
    return {
        "qualified_name":key,
        "namespace":namespace,
        "name":name,
        "self_assertion_count":s,
        "niwc_priority_stig_count":p,
        "niwc_example_ir_paths":list(prod_examples.get(key,[])),
        "deprecated":bool(schema_row.get("deprecated",False)),
        "deprecation_evidence":schema_row.get("deprecation_evidence"),
        "status":status,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("schema_catalog",type=Path)
    ap.add_argument("self_assertion_inventory",type=Path)
    ap.add_argument("niwc_inventory",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    schema=json.loads(args.schema_catalog.read_text(encoding="utf-8"))
    self_inv=json.loads(args.self_assertion_inventory.read_text(encoding="utf-8"))
    prod=json.loads(args.niwc_inventory.read_text(encoding="utf-8"))

    categories={
        "tests":(
            keyed(schema.get("test_elements",[])),
            self_inv.get("qualified_test_types",{}),
            prod.get("qualified_test_types",{}),
        ),
        "objects":(
            keyed(schema.get("object_elements",[])),
            self_inv.get("qualified_object_types",{}),
            prod.get("qualified_object_types",{}),
        ),
        "states":(
            keyed(schema.get("state_elements",[])),
            self_inv.get("qualified_state_types",{}),
            prod.get("qualified_state_types",{}),
        ),
    }

    ledger={}
    summary={}
    by_namespace=defaultdict(lambda:Counter())

    for category,(schema_rows,self_counts,prod_counts) in categories.items():
        schema_keys=set(schema_rows)
        observed_extra=(set(self_counts)|set(prod_counts))-schema_keys
        prod_examples=prod.get("qualified_type_examples",{}).get(category,{})
        rows=[
            classify(k,schema_rows[k],self_counts,prod_counts,prod_examples)
            for k in sorted(schema_keys)
        ]
        counts=Counter(x["status"] for x in rows)
        ledger[category]=rows
        summary[category]={
            "schema_total":len(schema_keys),
            "conformance_and_production":counts["conformance_and_production"],
            "conformance_only":counts["conformance_only"],
            "production_only":counts["production_only"],
            "schema_only":counts["schema_only"],
            "deprecated_total":sum(1 for x in rows if x["deprecated"]),
            "production_only_deprecated":sum(
                1 for x in rows if x["status"]=="production_only" and x["deprecated"]
            ),
            "observed_not_in_schema":sorted(observed_extra),
        }
        for row in rows:
            by_namespace[row["namespace"]][f'{category}_{row["status"]}']+=1
            by_namespace[row["namespace"]][f'{category}_schema_total']+=1

    out={
        "format":"scap-ng-oval-5.12.3-evidence-ledger-0.1",
        "scope":{
            "schema":"vendored SCAP 1.4 / OVAL 5.12.3 schemas",
            "conformance":"pinned OVAL-Community SCAP Self-Assertion OVAL_Test_Content",
            "production":"four pinned priority NIWC published STIG benchmarks",
        },
        "interpretation":{
            "conformance_and_production":"exercised by focused language tests and observed in production content",
            "conformance_only":"exercised by Self-Assertion but not seen in current priority STIG sample",
            "production_only":"seen in production STIGs but not exercised by Self-Assertion",
            "schema_only":"defined by OVAL 5.12.3 schemas but not exercised by either current evidence corpus",
        },
        "summary":summary,
        "by_namespace":{k:dict(sorted(v.items())) for k,v in sorted(by_namespace.items())},
        "ledger":ledger,
        "gate":{
            "all_observed_types_declared_by_schema":not any(
                summary[c]["observed_not_in_schema"] for c in summary
            ),
            "full_schema_semantic_conformance_claimed":False,
            "note":"Schema-only entries are explicit untested semantic surface, not assumed coverage.",
        },
    }
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"summary":summary,"gate":out["gate"]},indent=2,sort_keys=True))
    return 0 if out["gate"]["all_observed_types_declared_by_schema"] else 1


if __name__=="__main__":
    raise SystemExit(main())
