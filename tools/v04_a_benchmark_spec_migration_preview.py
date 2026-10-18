#!/usr/bin/env python3
"""#232/#239: evidence-backed, UNAPPROVED 0.4-A Benchmark spec migration preview.

Never mutate source archives. Derive the exact external automated Assessment
specifications reachable through actual Rule choices *per Benchmark*. Generate
an independently verifiable, isolated candidate with only Benchmark
assessment_specifications changed. The candidate is NOT an accepted 0.4
version policy, normalized compiler IR, signed bundle, or runnable scanner.
"""
from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import PurePosixPath

from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)
from v04_a_benchmark_choice_version_closure import inspect_edges, _folder
from v04_a_specification_version_gate import _identity


def build_preview(documents):
    """Return a proposed exact-reachable migration plan and isolated documents.

    The owner's normative choice between replacing and retaining legacy
    declarations remains OPEN. The preview uses 'exact reachable' as a
    candidate only; all original source is preserved.
    """
    before = inspect_edges(documents)  # fail closed on broken identities/links
    original = {path: canonical_json(doc) for path, doc in documents.items()}
    benchmarks = {}
    assessments = {}
    required = {}
    for path, doc in documents.items():
        kind, data = next(iter(doc.items()))
        namespace = _folder(path)
        if kind == "benchmark":
            benchmarks[namespace] = (path, data)
            required[namespace] = set()
        elif kind == "assessment":
            assessments[data["id"]] = data
    for path, doc in documents.items():
        kind, data = next(iter(doc.items()))
        if kind != "rule":
            continue
        namespace = _folder(path)
        if namespace not in benchmarks:
            raise ValueError(f"{path}: missing Benchmark namespace")
        for choice in data["assessment_choices"].values():
            assessment = assessments[choice["assessment"]]
            if assessment["mode"] == "automated":
                required[namespace].add(_identity(
                    assessment["specification"], path + ".automated_assessment"))
    staged = deepcopy(documents)
    changes = []
    for namespace, (path, data) in sorted(benchmarks.items()):
        original_specs = [_identity(x, path) for x in data["assessment_specifications"]]
        exact = sorted(required[namespace])
        if not exact:
            # A Benchmark without automated choices must not be silently
            # assigned another source's assessment specification.
            raise ValueError(f"{path}: no automated Assessment choices; human version review required")
        if len(set(original_specs)) != len(original_specs):
            raise ValueError(f"{path}: duplicate original specifications")
        before_set, after_set = set(original_specs), set(exact)
        patch = {
            "benchmark_id": data["id"],
            "path": path,
            "existing_specs": [{"id": sid, "version": version} for sid, version in original_specs],
            "reachable_automated_specs": [{"id": sid, "version": version} for sid, version in exact],
            "add_specs": [{"id": sid, "version": version} for sid, version in sorted(after_set - before_set)],
            "drop_specs": [{"id": sid, "version": version} for sid, version in sorted(before_set - after_set)],
            "source_document_sha256": sha256(original[path]).hexdigest(),
        }
        # This is an isolated in-memory candidate, not a source authoring edit.
        changed = staged[path]["benchmark"]
        changed["assessment_specifications"] = patch["reachable_automated_specs"]
        patch["proposed_document_sha256"] = sha256(canonical_json(staged[path])).hexdigest()
        changes.append(patch)
    after = inspect_edges(staged)
    if after["incompatible_edge_count"] != 0:
        raise ValueError(f"proposed source declarations still conflict: {after['incompatible_edge_count']}")
    if before["counts"]["choice_links"] != after["counts"]["choice_links"]:
        raise ValueError("migration changed Rule choice link count")
    for key, count in before["counts"].items():
        if key != "incompatible_automated_choice_links" and after["counts"].get(key) != count:
            raise ValueError(f"migration changed {key}")
    paths = {p["path"] for p in changes}
    for path, original_bytes in original.items():
        if canonical_json(documents[path]) != original_bytes:
            raise ValueError("source input mutated: " + path)
        if path not in paths and canonical_json(staged[path]) != original_bytes:
            raise ValueError("non-Benchmark source changed: " + path)
        if path in paths:
            a, b = documents[path]["benchmark"], staged[path]["benchmark"]
            for key in set(a) | set(b):
                if key != "assessment_specifications" and a.get(key) != b.get(key):
                    raise ValueError(f"Benchmark changed outside spec declaration: {path}:{key}")
    proposed_index = graph_index(staged)
    if proposed_index["counts"]["documents"] != len(documents):
        raise ValueError("migration changed source document count")
    report = {
        "status": "RESEARCH_CANDIDATE_NOT_APPROVED",
        "strategy": "exact_reachable_automated_assessment_specifications",
        "normative_approval_required": True,
        "allowed_to_compile": False,
        "source_document_count": len(documents),
        "benchmark_changes": changes,
        "source_rule_choice_counts": before["counts"],
        "proposed_rule_choice_counts": after["counts"],
        "source_incompatible_edges": before["incompatible_edge_count"],
        "candidate_incompatible_edges": after["incompatible_edge_count"],
        "source_graph_sha256": graph_index(documents)["graph_sha256"],
        "proposed_graph_sha256": proposed_index["graph_sha256"],
        "preservation_proved": True,
        "alternatives": [
            "retain both 0.3 and 0.4 declarations (not selected)",
            "replace legacy unreferenced 0.3 with exact required 0.4 (demonstrated candidate)",
        ],
        "limitations": [
            "candidate only; changing source Benchmark contracts still needs owner approval",
            "manual Assessments are native and are not auto-upgraded or edited",
            "does not validate full native 0.4 schema, result parity, or signed bundle",
            "does not justify promotion of scoped research Test/State syntax",
        ],
    }
    return report, staged


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json-archive", required=True)
    p.add_argument("--yaml-archive")
    p.add_argument("--report-json")
    p.add_argument("--assert-six-preview", action="store_true")
    args = p.parse_args(argv)
    report, staged = build_preview(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        alternate, yaml_staged = build_preview(read_authoring_archive(args.yaml_archive, "yaml"))
        def normalized_paths(value):
            if isinstance(value, dict):
                return {key: normalized_paths(child) for key, child in value.items()}
            if isinstance(value, list):
                return [normalized_paths(child) for child in value]
            if isinstance(value, str) and value.startswith("authoring/"):
                return value.removesuffix(".json").removesuffix(".yaml").removesuffix(".yml")
            return value
        if normalized_paths(alternate) != normalized_paths(report):
            raise ValueError("YAML/JSON migration reports are not identical")
        if graph_index(staged)["graph_sha256"] != graph_index(yaml_staged)["graph_sha256"]:
            raise ValueError("YAML/JSON staged source graphs are not identical")
        report["yaml_json_agree"] = True
    if args.assert_six_preview:
        if (len(report["benchmark_changes"]) != 6
                or report["source_document_count"] != 4001
                or report["source_rule_choice_counts"]["choice_links"] != 2958
                or report["source_incompatible_edges"] != 1391
                or report["candidate_incompatible_edges"] != 0
                or sum(len(x["add_specs"]) for x in report["benchmark_changes"]) != 6
                or sum(len(x["drop_specs"]) for x in report["benchmark_changes"]) != 6):
            raise ValueError("six-STIG pinned migration expectation changed")
        report["six_preview_pinned"] = True
    serialized = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(serialized, end="")
    if args.report_json:
        from pathlib import Path
        Path(args.report_json).write_text(serialized, encoding="utf-8")


if __name__ == "__main__":
    main()
