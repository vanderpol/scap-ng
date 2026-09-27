#!/usr/bin/env python3
"""Compare Self-Assertion construct usage to the vendored OVAL 5.12.3 schema catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def schema_keys(rows):
    return {f'{row.get("namespace","")}#{row.get("name","")}' for row in rows}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("inventory",type=Path)
    ap.add_argument("catalog",type=Path)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()

    inv=json.loads(args.inventory.read_text(encoding="utf-8"))
    cat=json.loads(args.catalog.read_text(encoding="utf-8"))

    expected={
        "tests":schema_keys(cat.get("test_elements",[])),
        "objects":schema_keys(cat.get("object_elements",[])),
        "states":schema_keys(cat.get("state_elements",[])),
    }
    observed={
        "tests":set(inv.get("qualified_test_types",{})),
        "objects":set(inv.get("qualified_object_types",{})),
        "states":set(inv.get("qualified_state_types",{})),
    }

    result={
        "format":"scap-ng-oval-self-assertion-schema-coverage-0.1",
        "role":"schema_to_conformance_corpus_accounting",
        "observed_counts":{k:len(v) for k,v in observed.items()},
        "schema_counts":{k:len(v) for k,v in expected.items()},
        "unknown_to_schema":{k:sorted(observed[k]-expected[k]) for k in observed},
        "schema_types_exercised":{k:sorted(observed[k] & expected[k]) for k in observed},
        "schema_types_not_exercised":{k:sorted(expected[k]-observed[k]) for k in observed},
    }
    result["gate"]={
        "all_observed_types_declared_by_schema":not any(result["unknown_to_schema"].values()),
        "note":"Unexercised schema types are coverage backlog, not importer failures.",
    }

    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({
        "observed_counts":result["observed_counts"],
        "unknown_to_schema":{k:len(v) for k,v in result["unknown_to_schema"].items()},
        "unexercised_schema_types":{k:len(v) for k,v in result["schema_types_not_exercised"].items()},
    },indent=2,sort_keys=True))
    return 0 if result["gate"]["all_observed_types_declared_by_schema"] else 1


if __name__=="__main__":
    raise SystemExit(main())
