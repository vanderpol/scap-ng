#!/usr/bin/env python3
"""Read-only, public-facing 0.4 authoring review inventory (Refs #232).

This report assists a human review of the *actual authoring files* and does
not rewrite or assert equivalence to OVAL or a live scanner. Structural
patterns are review leads, not permission to simplify source-backed checks.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
import re

from audit_v04_authoring_patterns import scan as scan_patterns
from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)


MAX_SAMPLES = 8
PLACEHOLDER = re.compile(r"\b(?:TODO|TBD|FIXME|PLACEHOLDER)\b", re.IGNORECASE)


def _category(path: str) -> str:
    segments = path.split("/")
    return segments[1] if len(segments) > 2 and segments[0] == "authoring" else "outside_authoring"


def _sample(target: dict, category: str, value: dict):
    rows = target.setdefault(category, [])
    if len(rows) < MAX_SAMPLES:
        rows.append(value)


def inventory(documents):
    """Identify review issues without inventing correctness or remediation."""
    graph = graph_index(documents)  # Fail closed on IDs and references.
    global_counts = Counter()
    by_area = defaultdict(Counter)
    samples = {}
    modes = {}
    for path, doc in sorted(documents.items()):
        area = _category(path)
        kind, body = next(iter(doc.items()))
        global_counts[f"{kind}_documents"] += 1
        by_area[area][f"{kind}_documents"] += 1
        if "unclassified" in path.lower():
            global_counts["unclassified_paths"] += 1
            _sample(samples, "unclassified_paths", {"path": path})
        if len(path) > 180:
            global_counts["long_authoring_paths"] += 1
            _sample(samples, "long_authoring_paths", {"path": path, "characters": len(path)})
        if kind == "assessment":
            mode = body.get("mode")
            modes[body["id"]] = mode
            global_counts[f"{mode}_assessments"] += 1
            by_area[area][f"{mode}_assessments"] += 1
            if mode == "manual":
                procedure = body.get("procedure", "")
                if not isinstance(procedure, str) or not procedure.strip():
                    global_counts["missing_manual_procedure"] += 1
                    _sample(samples, "missing_manual_procedure", {"path": path})
                elif PLACEHOLDER.search(procedure):
                    global_counts["manual_placeholder_procedure"] += 1
                    _sample(samples, "manual_placeholder_procedure", {"path": path})
                if "/assessments/manual/" in path:
                    by_area[area]["mode_specific_manual_paths"] += 1
            elif mode == "automated":
                if "/assessments/automated/" in path:
                    by_area[area]["mode_specific_automated_paths"] += 1
                for test_id, test in sorted((body.get("tests") or {}).items()):
                    global_counts["automated_tests"] += 1
                    by_area[area]["automated_tests"] += 1
                    req = test.get("require")
                    if isinstance(req, str):
                        shape = "source_exact_fallback"
                        _sample(samples, "source_exact_fallback", {
                            "path": path, "test": test_id, "require": req})
                    elif isinstance(req, dict) and set(req) == {"items"}:
                        shape = "presence_only"
                    elif isinstance(req, dict) and "all_items_must" in req:
                        shape = "inline_item_requirements"
                    else:
                        shape = "unrecognized_requirement"
                        _sample(samples, "unrecognized_requirement", {"path": path, "test": test_id})
                    global_counts[shape] += 1
                    by_area[area][shape] += 1
                    if "reported_elements" in test:
                        global_counts["explicit_reported_elements"] += 1
                    if "states" in test:
                        global_counts["source_exact_states"] += 1
            else:
                global_counts["invalid_assessment_mode"] += 1
                _sample(samples, "invalid_assessment_mode", {"path": path, "mode": mode})

    for path, doc in sorted(documents.items()):
        if "rule" not in doc:
            continue
        area = _category(path)
        rule = doc["rule"]
        choices = rule.get("assessment_choices") or {}
        choice_modes = {modes.get(row.get("assessment")) for row in choices.values()
                        if isinstance(row, dict)}
        if "manual" in choice_modes:
            global_counts["rules_with_manual_choice"] += 1
            by_area[area]["rules_with_manual_choice"] += 1
        if "automated" in choice_modes:
            global_counts["rules_with_automated_choice"] += 1
            by_area[area]["rules_with_automated_choice"] += 1
        if choice_modes == {"manual", "automated"}:
            global_counts["rules_with_both_choices"] += 1
            by_area[area]["rules_with_both_choices"] += 1
        if rule.get("default_assessment_choice") not in choices:
            global_counts["rule_missing_valid_default_choice"] += 1
            _sample(samples, "rule_missing_valid_default_choice", {"path": path})

    patterns = scan_patterns(documents)
    return {
        "status": "AUTHORING_REVIEW_INVENTORY_NOT_SCANNER_OR_OVAL_CONFORMANCE",
        "source_graph_sha256": graph["graph_sha256"],
        "logical_reference_counts": graph["counts"],
        "counts": dict(sorted(global_counts.items())),
        "by_area": {area: dict(sorted(counts.items()))
                    for area, counts in sorted(by_area.items())},
        "samples": samples,
        "structural_pattern_counts": patterns["counts"],
        "structural_pattern_samples": patterns["examples"],
        "review_not_auto_rewrite": sorted(patterns["high_confidence_non_growth"] +
                                          patterns["review_only_no_automatic_rewrite"]),
        "public_tool_readiness": {
            "parse_formats": "independent JSON / YAML strict loaders",
            "automatic_semantic_rewriting": False,
            "requires_native_schema_validation": True,
            "requires_compiler_and_scanner_acceptance_separately": True,
        },
    }


def review(json_archive: Path, yaml_archive: Path | None = None, *, assert_six=False):
    json_docs = read_authoring_archive(json_archive, "json")
    report = inventory(json_docs)
    report["inputs"] = {"json_sha256": sha256(json_archive.read_bytes()).hexdigest()}
    if yaml_archive is not None:
        yaml_docs = read_authoring_archive(yaml_archive, "yaml")
        yaml_report = inventory(yaml_docs)
        if (report["source_graph_sha256"] != yaml_report["source_graph_sha256"] or
                report["counts"] != yaml_report["counts"] or
                report["by_area"] != yaml_report["by_area"] or
                report["structural_pattern_counts"] != yaml_report["structural_pattern_counts"]):
            raise ValueError("JSON/YAML human-review inventory differs")
        report["inputs"]["yaml_sha256"] = sha256(yaml_archive.read_bytes()).hexdigest()
        report["inputs"]["json_yaml_review_parity"] = "PASS"
    if assert_six:
        expected = {"benchmark_documents": 6, "rule_documents": 1567,
                    "automated_tests": 1390, "source_exact_fallback": 221}
        for field, value in expected.items():
            if report["counts"].get(field) != value:
                raise ValueError(f"six-STIG review baseline changed: {field}")
        if sum(report["counts"].get(f"{x}_documents", 0)
               for x in ("assessment", "benchmark", "rule", "applicability")) != 4012:
            raise ValueError("six-STIG document population changed")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive", type=Path, required=True)
    parser.add_argument("--yaml-archive", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--assert-six", action="store_true")
    args = parser.parse_args()
    data = review(args.json_archive, args.yaml_archive, assert_six=args.assert_six)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": data["status"], "counts": data["counts"],
                      "structural_pattern_counts": data["structural_pattern_counts"],
                      "inputs": data["inputs"]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
