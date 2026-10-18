#!/usr/bin/env python3
"""#232/#239: end-to-end source ingestion -> 0.4-A base authoring research ZIP.

This joins separately tested stages into one independently inspectable package:
1. Parse raw YAML or JSON six-STIG research inputs.
2. Exactly invert experimental 0.4 scoped syntax into base 0.4-A authoring.
3. Validate every automated Assessment against the base 0.4 schema.
4. Stage *unapproved* Benchmark specification metadata by actual Rule edges.
5. Emit and independently verify deterministic **UNSIGNED RESEARCH ZIP** bytes.

It does NOT establish scanner execution, typed source semantics, signature
verification, release authority, or a normative executable .scapng format.
The speculative Benchmark metadata and scoped syntax policy require approval.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import io
import json
from pathlib import Path
import zipfile

from v04_a_authoring_graph_index import canonical_json, graph_index, read_authoring_archive
from v04_a_lower_scoped_to_base import lower_all
from v04_a_benchmark_spec_migration_preview import build_preview
from v04_a_benchmark_choice_version_closure import inspect_edges
from v04_a_deterministic_research_container import (
    create_research_container, verify_research_container,
)

REPORT_KIND = "0.4-A research end-to-end base authoring package, not compiled"


def _extract_docs(data):
    """Independent verification of every canonical document inside ZIP."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        docs = {}
        for record in manifest["documents"]:
            path = record["logical_source"] + ".json"
            if path in docs:
                raise ValueError("duplicated packaged source logical path: " + path)
            document = json.loads(archive.read(record["member"]))
            if canonical_json(document) != archive.read(record["member"]):
                raise ValueError("noncanonical bundled Assessment")
            docs[path] = document
    return docs, manifest


def stage_and_package(documents, *, validate_base=True):
    """Return one validated research ZIP, proof report. Inputs never mutated."""
    if not validate_base:
        # Opt-in is exclusively for synthetic negative/positive test fixtures
        # that cannot satisfy complete Assessment schema requirements.
        base_label = "NOT_CHECKED_RESEARCH_FIXTURE"
    else:
        base_label = "ALL_AUTOMATED_ASSESSMENTS_VALIDATED"
    raw_hashes = {path: sha256(canonical_json(doc)).hexdigest()
                  for path, doc in documents.items()}
    original_graph = graph_index(documents)
    lowered, lower_report = lower_all(documents, validate_base=validate_base)
    if lower_report["source_graph_sha256"] != original_graph["graph_sha256"]:
        raise ValueError("lowering lost original source graph identity")
    metadata_plan, staged_docs = build_preview(lowered)
    if metadata_plan["preservation_proved"] is not True:
        raise ValueError("metadata migration source-preservation proof failed")
    data, manifest = create_research_container(lowered)
    verified = verify_research_container(data)
    if verified["member_count"] != len(documents):
        raise ValueError("packaging document count mismatch")
    packaged, packaged_manifest = _extract_docs(data)
    if len(packaged) != len(staged_docs):
        raise ValueError("packaged document count changed")
    # Ensure package is exactly the version-staged, base-syntax output.
    source_docs = {record["logical_source"]: record for record in manifest["documents"]}
    for path, doc in staged_docs.items():
        logical_path = path.rsplit(".", 1)[0]
        if logical_path not in source_docs:
            raise ValueError("staged authoring member missing: " + path)
        record = source_docs[logical_path]
        if sha256(canonical_json(doc)).hexdigest() != record["sha256"]:
            raise ValueError("packaged member differs from staged source: " + path)
    for path, raw_sha in raw_hashes.items():
        if sha256(canonical_json(documents[path])).hexdigest() != raw_sha:
            raise ValueError("original source was mutated: " + path)
    staged_index = graph_index(staged_docs)
    if staged_index["graph_sha256"] != manifest["staged_graph_sha256"]:
        raise ValueError("planned staged graph differs from package manifest")
    edge_report = inspect_edges(staged_docs)
    if edge_report["incompatible_edge_count"] != 0:
        raise ValueError("unresolved per-Benchmark declared Assessment version")
    for doc in packaged.values():
        assessment = doc.get("assessment")
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        for test in (assessment.get("tests") or {}).values():
            if "require" not in test or "collected_items_require" in test or "state_fields_require" in test:
                raise ValueError("packaged Assessment retained unsupported scoped Test vocabulary")
    result = {
        "status": "VERIFIED_BASE_AUTHORING_RESEARCH_ONLY",
        "format": REPORT_KIND,
        "source_document_count": len(documents),
        "source_graph_sha256": original_graph["graph_sha256"],
        "base_lowered_graph_sha256": lower_report["lowered_graph_sha256"],
        "packaged_staged_graph_sha256": staged_index["graph_sha256"],
        "archive_sha256": sha256(data).hexdigest(),
        "archive_bytes": len(data),
        "assessment_counts": lower_report["counters"],
        "rule_choice_links": edge_report["counts"]["choice_links"],
        "benchmark_count": len(edge_report["benchmarks"]),
        "base_schema": base_label,
        "source_preservation": "PASS",
        "independent_archive_verification": verified["status"],
        "allowed_to_scan": False,
        "owner_approved": False,
        "signed_bundle": False,
        "native_0_4_compiler_complete": False,
        "open_approval_gates": [
            "candidate scoped-to-base authoring syntax semantics",
            "Benchmark version declaration migration policy",
            "full capability-specific semantic validation",
            "native scanner IR and signed .scapng bundle format",
        ],
    }
    return data, result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive", type=Path, required=True)
    parser.add_argument("--yaml-archive", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--assert-six", action="store_true")
    args = parser.parse_args(argv)
    data, report = stage_and_package(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        second, same = stage_and_package(read_authoring_archive(args.yaml_archive, "yaml"))
        if data != second or report != same:
            raise ValueError("independent YAML and JSON do not produce identical packaged base content")
        report["yaml_json_byte_parity"] = "PASS"
    if args.assert_six:
        count = report["assessment_counts"]
        if (report["source_document_count"] != 4001
                or report["benchmark_count"] != 6
                or report["rule_choice_links"] != 2958
                or count["lowered_automated_assessments"] != 872
                or count["lowered_tests"] != 1375
                or report["base_schema"] != "ALL_AUTOMATED_ASSESSMENTS_VALIDATED"):
            raise ValueError("full six-STIG base-authoring archive failed pinned assertion")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(data)
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    print(rendered, end="")
    if args.report_json:
        args.report_json.parent.mkdir(parents=True, exist_ok=True)
        args.report_json.write_text(rendered, encoding="utf-8")


if __name__ == "__main__":
    main()
