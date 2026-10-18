#!/usr/bin/env python3
"""#240: source-backed six-STIG census of non-executable 0.4-A IR dataflow.

Derives counts and bounded actual authoring witnesses from fully decoded,
verified IR. It never evaluates a Variable, collector, filter or Test result.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import canonical_json
from v04_a_lossless_ir import decode_and_verify


def census(ir):
    """Independent full roundtrip check, then stable typed-source inventory."""
    docs = decode_and_verify(ir)
    by_namespace = defaultdict(Counter)
    totals = Counter()
    witnesses = {}
    foreach_bindings = []
    cases = []
    for row in ir["documents"]:
        if row["kind"] != "assessment":
            continue
        a = row["assessment_index"]
        if a["mode"] != "automated":
            continue
        flow = a["source_dataflow"]
        path = row["source_path"]
        namespace = path.split("/")[1]
        totals["automated_assessments"] += 1
        by_namespace[namespace]["automated_assessments"] += 1
        counts = Counter()
        for node in flow["nodes"]:
            counts[f"named_{node['kind']}_nodes"] += 1
        for edge in flow["edges"]:
            counts[f"edge_{edge['role']}"] += 1
            counts["all_edges"] += 1
        for site in flow["sites"]:
            counts[f"site_{site['kind']}"] += 1
            counts["all_sites"] += 1
        if any(x["kind"] == "variable" for x in flow["nodes"]):
            counts["assessments_with_named_variables"] += 1
        if any(x["kind"] == "object" for x in flow["nodes"]):
            counts["assessments_with_shared_objects"] += 1
        for site in flow["sites"]:
            if site["kind"] != "for_each":
                continue
            owner = row["source_ast"]["assessment"]
            for segment in site["path"][:-1]:
                owner = owner[segment]
            definition = owner["for_each"]
            projected = [
                {"selector": selector_name, "from": selector["from"]}
                for selector_name, selector in sorted((owner.get("select") or {}).items())
                if isinstance(selector, dict) and isinstance(selector.get("from"), str)
            ]
            foreach_bindings.append({
                "assessment_id": row["id"],
                "source_path": path,
                "site_path": site["path"],
                "source_object": definition["in"],
                "item_alias": definition["item"],
                "projections": projected,
            })
        for marker in ("set", "filter", "for_each", "projection"):
            if counts[f"site_{marker}"]:
                counts[f"assessments_with_{marker}"] += 1
                candidate = {
                    "assessment_id": row["id"],
                    "source_path": path,
                    "site_count": counts[f"site_{marker}"],
                }
                if marker not in witnesses or (
                    candidate["site_count"], candidate["assessment_id"]
                ) > (
                    witnesses[marker]["site_count"], witnesses[marker]["assessment_id"]
                ):
                    witnesses[marker] = candidate
        by_namespace[namespace].update(counts)
        totals.update(counts)
        cases.append({
            "id": row["id"], "source_path": path,
            "named_variables": counts["named_variable_nodes"],
            "named_objects": counts["named_object_nodes"],
            "edges": counts["all_edges"],
            "sites": counts["all_sites"],
        })
    complexity = sorted(
        cases, key=lambda d: (-d["edges"], -d["named_variables"],
                             -d["sites"], d["id"], d["source_path"])
    )[:8]
    return {
        "status": "VERIFIED_SOURCE_STRUCTURE_NOT_EXECUTABLE",
        "source_graph_sha256": ir["source_graph_sha256"],
        "ir_sha256": sha256(canonical_json(ir) + b"\n").hexdigest(),
        "document_count": len(docs),
        "counts": dict(sorted(totals.items())),
        "by_source_namespace": {
            namespace: dict(sorted(row.items()))
            for namespace, row in sorted(by_namespace.items())
        },
        "source_backed_examples": dict(sorted(witnesses.items())),
        "foreach_source_bindings": sorted(foreach_bindings, key=lambda x: (
            x["assessment_id"], canonical_json(x["site_path"]))),
        "largest_dataflow_examples": complexity,
        "limitations": [
            "source namespace does not represent a deduplicated per-Benchmark reachability count",
            "ordered lexical source edges are not runnable collection instructions",
            "filter/Set status and foreach lineage/evaluation are not computed",
            "YAML/JSON convergence and 0.4 version declarations remain research gates",
            "source AST parity is not scanner/OVAL runtime equivalence",
        ],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ir", type=Path, required=True)
    parser.add_argument("--out-report", type=Path)
    parser.add_argument("--assert-six", action="store_true")
    args = parser.parse_args(argv)
    result = census(json.loads(args.ir.read_text(encoding="utf-8")))
    if args.assert_six and (
        result["document_count"] != 4001 or
        result["counts"]["automated_assessments"] != 872 or
        result["counts"]["named_test_nodes"] != 1375
    ):
        raise ValueError("pinned six-STIG IR source census totals differ")
    if args.assert_six and (
        not result["counts"].get("edge_variable_value") or
        not result["counts"].get("edge_object_acquisition")
    ):
        raise ValueError("six-STIG collection/Variable source evidence unexpectedly missing")
    printed = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    print(printed, end="")
    if args.out_report:
        args.out_report.parent.mkdir(parents=True, exist_ok=True)
        args.out_report.write_text(printed, encoding="utf-8")


if __name__ == "__main__":
    main()
