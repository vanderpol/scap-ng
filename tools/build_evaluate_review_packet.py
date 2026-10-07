#!/usr/bin/env python3
"""Build a compact human-review packet for SCAP-NG evaluate structure."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from measure_evaluate_shapes import analyze_assessment


def dump_yaml(value:Any)->str:
    return yaml.safe_dump(value,sort_keys=False,width=100).rstrip()


def load_rows(root:Path):
    rows=[]
    docs={}
    for path in sorted(root.rglob("*.assessment.yaml")):
        try:
            doc=yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        a=(doc or {}).get("assessment")
        if not isinstance(a,dict) or a.get("mode")!="automated" or "evaluate" not in a:
            continue
        aid=str(a.get("id") or "")
        if ".SV-" not in aid and not aid.startswith("SV-"):
            continue
        row=analyze_assessment(path,doc)
        rows.append(row)
        docs[row["assessment_id"]]=doc
    return rows,docs


def select(rows):
    single=next((r for r in rows if r["trivial_single_test_evaluate"]),None)
    flat=next((r for r in rows if r["flat_test_operator"] and 2 <= r["test_count"] <= 3),None)
    repeated=next((r for r in rows if r["repeated_test_ref_occurrences"]>0),None)
    complex_case=max(rows,key=lambda r:(r["evaluate_depth"],r["evaluate_nodes"]),default=None)
    return [
        ("Single-Test ceremony",single),
        ("Flat composition",flat),
        ("Repeated Test reference",repeated),
        ("Deepest composition",complex_case),
    ]


def case_block(title,row,docs):
    if row is None:
        return f"### {title}\n\nNo representative case in this package.\n"
    a=docs[row["assessment_id"]]["assessment"]
    lines=[
        f"### {title}",
        "",
        f"Assessment: `{row['assessment_id']}`",
        "",
        f"Tests: {row['test_count']}; evaluate depth: {row['evaluate_depth']}; nodes: {row['evaluate_nodes']}.",
        "",
        "```yaml",
        dump_yaml({"evaluate":a["evaluate"]}),
        "```",
        "",
    ]
    if row["trivial_single_test_evaluate"]:
        test_id=a["evaluate"]["test"]
        lines += [
            "Candidate authored shorthand:",
            "",
            "```yaml",
            "tests:",
            f"  {test_id}:",
            "    # Test body unchanged",
            "# evaluate omitted because exactly one Test exists",
            "```",
            "",
            "Compiler/canonical form would materialize the explicit root again; "
            "this is authoring sugar, not a runtime default.",
            "",
        ]
    return "\n".join(lines)


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("root",type=Path)
    p.add_argument("--census",type=Path,required=True)
    p.add_argument("--label",required=True)
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()

    census=json.loads(args.census.read_text(encoding="utf-8"))
    rows,docs=load_rows(args.root)
    chosen=select(rows)
    s=census["summary"]

    parts=[
        f"# Evaluate review packet — {args.label}",
        "",
        "**Status:** generated research evidence; no schema change.",
        "",
        "## Production shape",
        "",
        f"- automated Rule Assessments: **{s['assessments']}**",
        f"- one-Test trivial root: **{s['trivial_single_test_evaluate']} ({s['trivial_single_test_percent']}%)**",
        f"- flat Test-only composition: **{s['flat_test_operator']} ({s['flat_test_operator_percent']}%)**",
        f"- evaluate depth > 2: **{s['nested_evaluate_depth_gt_2']} ({s['nested_evaluate_percent']}%)**",
        f"- repeated Test references: **{s['assessments_with_repeated_test_refs']}**",
        f"- maximum depth/nodes: **{s['max_evaluate_depth']} / {s['max_evaluate_nodes']}**",
        "",
        "## Same-content presentation cases",
        "",
    ]
    for title,row in chosen:
        parts.append(case_block(title,row,docs))

    parts += [
        "## Six-state boundary",
        "",
        "The decision tree cannot be replaced by ordinary Boolean/procedural ordering. "
        "The pinned OVAL-derived tables include decisive mixed-status cases:",
        "",
        "- `AND(false, error) -> false`",
        "- `OR(true, error) -> true`",
        "- `ONE(true, true, error) -> false`",
        "- `XOR(true, error) -> error`",
        "",
        "These are aggregation semantics, not host-language truthiness.",
        "",
        "## Candidate disposition",
        "",
        "1. **Keep named Tests.** Test identity/results/evidence remain independently useful, "
        "and production content repeats Test references.",
        "2. **Keep first-class `evaluate` for real composition.** Nested and non-Boolean "
        "aggregation is present in production.",
        "3. **Do not nest Test definitions into `evaluate` for 0.3.** It saves little compared "
        "with the identity/result complications it creates.",
        "4. **Consider authoring-only single-Test shorthand.** When exactly one Test exists, "
        "the author may omit `evaluate`; normalization materializes `evaluate: {test: ...}` "
        "before executable packaging/validation so the canonical form has no hidden default.",
        "5. **For explicit composition, compare summary-first source order.** Put `evaluate` "
        "after metadata/inputs/dependencies and before named Tests in the human-authored view; "
        "ordering remains non-semantic.",
        "",
        "This packet is evidence for #167, not an accepted 0.3 change.",
        "",
    ]

    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text("\n".join(parts),encoding="utf-8")
    print(json.dumps({
        "label":args.label,
        "selected":[
            {"case":title,"assessment_id":row["assessment_id"] if row else None}
            for title,row in chosen
        ],
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
