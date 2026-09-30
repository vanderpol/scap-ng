#!/usr/bin/env python3
"""Aggregate per-package summaries from the full NIWC Current OVAL census."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",type=Path)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()

    files=sorted(args.root.rglob("*-summary.json"))
    rows=[json.loads(p.read_text(encoding="utf-8")) for p in files]
    totals={
        "packages":len(rows),
        "definitions":sum(r.get("definitions",0) for r in rows),
        "semantic_equal":sum(r.get("semantic_equal",0) for r in rows),
        "deprecated_blockers":sum(r.get("deprecated_blockers",0) for r in rows),
        "publisher_extension_blockers":sum(r.get("publisher_extension_blockers",0) for r in rows),
        "unexpected_failures":sum(r.get("unexpected_failures",0) for r in rows),
        "max_dependency_depth":max((r.get("max_dependency_depth",0) for r in rows),default=0),
    }
    extension_elements=sorted({
        item
        for row in rows
        for item in row.get("publisher_extension_elements",[])
    })
    out={"totals":totals,"publisher_extension_elements":extension_elements,"packages":rows}
    payload=json.dumps(out,indent=2,sort_keys=True)+"\n"
    print(payload,end="")
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(payload,encoding="utf-8")
    return 1 if totals["unexpected_failures"] else 0

if __name__=="__main__":
    raise SystemExit(main())
