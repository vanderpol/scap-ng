#!/usr/bin/env python3
"""#232/#229: six-STIG research-only source expression plan census.

Independently revalidate complete typed 0.4-A source envelopes, compile each
automated Assessment's evaluate/applicability Boolean tree and verify that
supplied artificial outcomes traverse the plan. These synthetic runs are NOT
scanner observations or evidence of source OVAL parity.
"""
from __future__ import annotations
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import canonical_json
from v04_a_lossless_ir import decode_and_verify
from v04_a_truth_plan import (STAGE, SIX, UnsupportedExpression,
                              compile_expression, execute_supplied_results)
from v04_a_truth_plan_source_oracle import source_expected_outcome

FIXED_SCENARIOS = ("true", "false", "error", "unknown",
                   "not_evaluated", "not_applicable")
MANIFEST_STAGE = "RESEARCH_SIX_STATE_EXPRESSION_PLANS_SUPPLIED_INPUT_ONLY"


def build_manifest(ir):
    documents = decode_and_verify(ir)
    plans, blockers, counted = [], [], Counter()
    evaluate_witnesses = []
    for path, doc in sorted(documents.items()):
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        counted["automated_assessments_seen"] += 1
        for field in ("evaluate", "applicability"):
            if field == "applicability" and assessment.get(field) is None:
                continue
            try:
                plan = compile_expression(assessment, field=field)
            except UnsupportedExpression as exc:
                blockers.append({"assessment_id": assessment["id"],
                                 "source_path": path, "field": field,
                                 "reason": str(exc)})
                continue
            for instruction in plan["instructions"]:
                counted["opcode_" + instruction["op"]] += 1
                counted["all_instructions"] += 1
            counted["compiled_expression_roots"] += 1
            if field == "evaluate":
                counted["assessments_with_compiled_evaluate"] += 1
                evaluate_witnesses.append({
                    "assessment_id": assessment["id"],
                    "source_path": path,
                    "instruction_count": plan["instruction_count"],
                    "test_leaf_occurrences": sum(i["op"] == "read_test"
                                                 for i in plan["instructions"]),
                    "max_source_path_depth": max(len(i["path"])
                                                 for i in plan["instructions"]),
                    "operators": dict(sorted(Counter(
                        i["op"] for i in plan["instructions"]
                        if i["op"] not in ("read_test", "read_assessment")
                    ).items())),
                })
            else:
                counted["compiled_applicability_roots"] += 1
            # Exercise all six supplied outcome classes in the exact source
            # expression; do NOT claim each Test actually collects those.
            checks = {}
            for outcome in FIXED_SCENARIOS:
                supplied_tests = dict.fromkeys(plan["requires"]["tests"], outcome)
                supplied_deps = dict.fromkeys(plan["requires"]["dependencies"], outcome)
                observed = execute_supplied_results(plan, supplied_tests, supplied_deps)
                expected = source_expected_outcome(assessment[field],
                                                   supplied_tests, supplied_deps)
                if observed["outcome"] != expected:
                    raise ValueError(f"{path}:{field}: source oracle disagrees for {outcome}")
                checks[outcome] = observed["outcome"]
                counted["synthetic_expression_executions"] += 1
                counted["independent_oracle_topology_checks"] += 1
            ids = [("test", key) for key in plan["requires"]["tests"]]
            ids += [("assessment", key) for key in plan["requires"]["dependencies"]]
            for scenario in ("ascending", "descending", "name_bytes"):
                assigned = {}
                for index, (kind, ident) in enumerate(ids):
                    if scenario == "ascending":
                        selected = index % len(FIXED_SCENARIOS)
                    elif scenario == "descending":
                        selected = (-index - 1) % len(FIXED_SCENARIOS)
                    else:
                        selected = sum(ident.encode("utf-8")) % len(FIXED_SCENARIOS)
                    assigned[(kind, ident)] = FIXED_SCENARIOS[selected]
                mixed_tests = {name: assigned[("test", name)]
                               for name in plan["requires"]["tests"]}
                mixed_deps = {name: assigned[("assessment", name)]
                              for name in plan["requires"]["dependencies"]}
                actual = execute_supplied_results(plan, mixed_tests, mixed_deps)["outcome"]
                expected = source_expected_outcome(assessment[field],
                                                   mixed_tests, mixed_deps)
                if actual != expected:
                    raise ValueError(f"{path}:{field}: mixed source oracle disagrees ({scenario})")
                counted["synthetic_expression_executions"] += 1
                counted["independent_oracle_topology_checks"] += 1
                counted["mixed_leaf_oracle_checks"] += 1
            plans.append({
                "assessment_id": assessment["id"],
                "source_path": path,
                "source_sha256": sha256(canonical_json(doc)).hexdigest(),
                "expression_field": field,
                "plan": plan,
                "synthetic_result_scenarios_not_collections": checks,
            })
    return {
        "stage": MANIFEST_STAGE,
        "executor_stage": STAGE,
        "source_ir_sha256": sha256(canonical_json(ir) + b"\n").hexdigest(),
        "source_graph_sha256": ir["source_graph_sha256"],
        "counts": dict(sorted(counted.items())),
        "unapproved_expression_blockers": blockers,
        "largest_source_expressions": sorted(
            evaluate_witnesses,
            key=lambda x: (-x["instruction_count"], -x["max_source_path_depth"],
                           x["assessment_id"], x["source_path"]),
        )[:8],
        "plans": plans,
        "not_proven": [
            "actual Test/Item/State/Variable collection or execution",
            "source OVAL end-to-end scanner result equivalence",
            "runtime applicability binding or conditional branch policy",
            "signed bundle, executable 0.4 compiler, publisher version migration",
            "synthetic supplied-result scenarios are NOT compliance outcomes",
        ],
    }


def verify_manifest(ir, manifest):
    """Rebuild independently from checked source and demand identical bytes."""
    if canonical_json(build_manifest(ir)) != canonical_json(manifest):
        raise ValueError("research expression plan index, provenance or scenarios tampered")
    return True


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--ir", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--report", type=Path)
    p.add_argument("--assert-six", action="store_true")
    args = p.parse_args(argv)
    ir = json.loads(args.ir.read_text(encoding="utf-8"))
    manifest = build_manifest(ir)
    verify_manifest(ir, manifest)
    c = manifest["counts"]
    if args.assert_six:
        if c["automated_assessments_seen"] != 872:
            raise ValueError("six-STIG automated Assessment count has changed")
        if (c.get("assessments_with_compiled_evaluate", 0) != 872
                or manifest["unapproved_expression_blockers"]):
            raise ValueError("six-STIG evaluate source plan coverage is incomplete or blocked")
    encoded = canonical_json(manifest) + b"\n"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(encoded)
    report = {
        "stage": MANIFEST_STAGE,
        "verified": True,
        "manifest_sha256": sha256(encoded).hexdigest(),
        "source_ir_sha256": manifest["source_ir_sha256"],
        "counts": c,
        "blocked_expression_count": len(manifest["unapproved_expression_blockers"]),
        "blocked_sources": manifest["unapproved_expression_blockers"][:15],
        "operator_counts": {k:v for k,v in c.items() if k.startswith("opcode_")},
        "largest_source_expressions": manifest["largest_source_expressions"],
        "scanner_executed": False,
        "native_executable_compiler_complete": False,
        "synthetic_result_execution_only": True,
    }
    printed = json.dumps(report, sort_keys=True, indent=2) + "\n"
    print(printed, end="")
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(printed, encoding="utf-8")


if __name__ == "__main__":
    main()
