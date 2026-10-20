#!/usr/bin/env python3
"""Exact-reachable Benchmark version declaration preview for 0.4.0 (#232).

This is a source-preserving *candidate* for resolving Benchmark 0.3.0 versus
reachable Assessment 0.4.0 contracts. It never edits source archives, makes
no semantic migration of Assessments, and cannot output executable bundles.
The candidate changes only Benchmark.assessment_specifications in memory;
source and candidate hashes, all edges, and both parsers are independently
checked. Source version policy needs explicit owner acceptance.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)
from v04_a_benchmark_spec_migration_preview import build_preview
from v04_canonical_source_ir import (
    _schema_validators, decode_and_verify, normalize_documents,
)

STATUS = "VERSION_DECLARATION_CANDIDATE_NOT_APPROVED"


def _logical_report(report):
    """Ignore YAML/JSON filename extensions; never normalize logical IDs."""
    result = dict(report)
    changes = []
    for record in result["benchmark_changes"]:
        rec = dict(record)
        rec["path"] = rec["path"].removesuffix(".yaml").removesuffix(".json")
        changes.append(rec)
    result["benchmark_changes"] = changes
    return result


def preview(documents, *, validate_benchmark_schema=True):
    before = normalize_documents(documents)
    if before["benchmark_version_conflicts"] == 0:
        # An already-consistent source requires no migration or invented patch.
        return {
            "status": "VERSION_DECLARATIONS_ALREADY_COMPATIBLE",
            "source_ir": before,
            "candidate_ir": before,
            "source_graph_sha256": before["source_graph_sha256"],
            "candidate_graph_sha256": before["source_graph_sha256"],
            "original_source_unchanged": True,
            "changes": [],
            "conflicts_before": 0,
            "conflicts_after": 0,
            "choice_links": before["rule_choice_links"],
            "approval_required": False,
        }
    hashes = {path: sha256(canonical_json(doc)).hexdigest()
              for path, doc in documents.items()}
    plan, staged = build_preview(documents)
    if plan["source_incompatible_edges"] != before["benchmark_version_conflicts"]:
        raise ValueError("source conflict count changed across independent auditors")
    if plan["candidate_incompatible_edges"]:
        raise ValueError("unresolved candidate version declarations")
    after = normalize_documents(staged)
    if after["benchmark_version_conflicts"]:
        raise ValueError("candidate remains version-inconsistent")
    if before["totals"] != after["totals"] or before["rule_choice_links"] != after["rule_choice_links"]:
        raise ValueError("candidate changed source objects or Rule choices")
    if before["assessment_truth_dependencies"] != after["assessment_truth_dependencies"]:
        raise ValueError("candidate changed Assessment dependencies")
    if before["source_dataflow"] != after["source_dataflow"]:
        raise ValueError("candidate changed Object/Variable dataflow")
    if decode_and_verify(after) != {
        path.removesuffix(".yaml") + ".json" if path.endswith(".yaml") else path: doc
        for path, doc in staged.items()
    }:
        raise ValueError("candidate source-IR reconstruction mismatch")
    changed = {row["path"] for row in plan["benchmark_changes"]}
    if len(changed) != len(plan["benchmark_changes"]):
        raise ValueError("duplicate candidate Benchmark path")
    for path, original in documents.items():
        if sha256(canonical_json(original)).hexdigest() != hashes[path]:
            raise ValueError("original authoring source mutated")
        revised = staged[path]
        if path not in changed and revised != original:
            raise ValueError(f"{path}: unexpected non-Benchmark source change")
        if path in changed:
            if set(original) != {"benchmark"} or set(revised) != {"benchmark"}:
                raise ValueError(f"{path}: invalid Benchmark source")
            for key in set(original["benchmark"]) | set(revised["benchmark"]):
                if key != "assessment_specifications" and (
                    original["benchmark"].get(key) != revised["benchmark"].get(key)
                ):
                    raise ValueError(f"{path}: changed Benchmark field outside declarations")
    if validate_benchmark_schema:
        validators = _schema_validators(Path(__file__).resolve().parents[1] / "schema/v0.4.0")
        validator = validators["benchmark"]
        for path in changed:
            problems = list(validator.iter_errors(staged[path]))
            if problems:
                raise ValueError(f"{path}: version candidate failed native Benchmark schema: "
                                 f"{problems[0].message}")
    return {
        "status": STATUS,
        "source_ir": before,
        "candidate_ir": after,
        "source_graph_sha256": before["source_graph_sha256"],
        "candidate_graph_sha256": after["source_graph_sha256"],
        "original_source_unchanged": True,
        "changes": plan["benchmark_changes"],
        "conflicts_before": before["benchmark_version_conflicts"],
        "conflicts_after": after["benchmark_version_conflicts"],
        "choice_links": after["rule_choice_links"],
        "approval_required": True,
    }


def preview_pair(json_archive, yaml_archive, *, validate_benchmark_schema=True):
    from_json = preview(read_authoring_archive(json_archive, "json"),
                        validate_benchmark_schema=validate_benchmark_schema)
    from_yaml = preview(read_authoring_archive(yaml_archive, "yaml"),
                        validate_benchmark_schema=validate_benchmark_schema)
    if canonical_json(from_json["candidate_ir"]) != canonical_json(from_yaml["candidate_ir"]):
        raise ValueError("JSON/YAML version candidate graph differs")
    if canonical_json(from_json["source_ir"]) != canonical_json(from_yaml["source_ir"]):
        raise ValueError("JSON/YAML original source graph differs")
    # The candidate preview report must also be source-format independent.
    fields = ("status", "source_graph_sha256", "candidate_graph_sha256",
              "conflicts_before", "conflicts_after", "choice_links", "approval_required")
    for key in fields:
        if from_json[key] != from_yaml[key]:
            raise ValueError(f"JSON/YAML version preview disagreement: {key}")
    if _logical_report({"benchmark_changes": from_json["changes"]}) != _logical_report(
        {"benchmark_changes": from_yaml["changes"]}):
        raise ValueError("JSON/YAML Benchmark version patch differs")
    out = {
        "status": from_json["status"],
        "stage": "source_only_not_executable",
        "source_graph_sha256": from_json["source_graph_sha256"],
        "candidate_graph_sha256": from_json["candidate_graph_sha256"],
        "original_source_unchanged": True,
        "benchmark_changes": _logical_report(
            {"benchmark_changes": from_json["changes"]})["benchmark_changes"],
        "benchmarks_changed": len(from_json["changes"]),
        "conflicts_before": from_json["conflicts_before"],
        "conflicts_after": from_json["conflicts_after"],
        "rule_choice_links": from_json["choice_links"],
        "source_document_count": from_json["source_ir"]["totals"]["documents"],
        "yaml_json_source_and_candidate_parity": "PASS",
        "benchmark_native_schema": "PASS" if validate_benchmark_schema else "NOT_CHECKED_TEST_FIXTURE",
        "version_policy_approved": False,
        "executable_compiler_completed": False,
        "signed_bundle": False,
        "scanner_parity": False,
        "approval_options": [
            "replace unused 0.3 Benchmark declaration with exact reachable 0.4 specification",
            "retain original 0.3 declaration and explicitly append reachable 0.4",
        ],
    }
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", type=Path, required=True)
    p.add_argument("--yaml-archive", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--assert-six", action="store_true")
    args = p.parse_args()
    result = preview_pair(args.json_archive, args.yaml_archive)
    if args.assert_six:
        if (
            result["source_document_count"], result["benchmarks_changed"],
            result["conflicts_before"], result["conflicts_after"], result["rule_choice_links"]
        ) != (4001, 0, 0, 0, 2958):
            raise ValueError("approved six-STIG version closure baseline changed")
        # The reviewed 0.4 declaration was applied by source generation.
        documents = read_authoring_archive(args.json_archive, "json")
        specs = [doc["benchmark"]["assessment_specifications"]
                 for doc in documents.values() if "benchmark" in doc]
        if (len(specs) != 6 or any(
            len(rows) != 1 or rows[0] != {
                "id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"
            } for rows in specs
        )):
            raise ValueError("Benchmark source carries unexpected Assessment specifications")
        result["version_policy_approved"] = True
        result["owner_decision"] = "2026-10-20 exact-reachable 0.4-only Benchmark declarations"
        result["approved_declared_benchmarks"] = len(specs)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                           encoding="utf-8")
    print(json.dumps({k: v for k, v in result.items() if k != "benchmark_changes"},
                     sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
