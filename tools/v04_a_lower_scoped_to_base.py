#!/usr/bin/env python3
"""#232/#239: reversible 0.4-A research shorthand -> base Assessment source.

This is an explicitly bounded *authoring syntax lowering* step, not a scanner,
a normative grammar decision, runtime semantics proof, or official bundle.
Only pinned 0.4-A scoped candidate Automated Assessments are transformed.
All other native documents stay byte-for-byte equivalent as parsed JSON.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path

from v04_a_authoring_graph_index import (
    canonical_json, graph_index, read_authoring_archive,
)
from research_04_scoped_state_require import compact, expand


def lower_one(doc):
    if not isinstance(doc, dict) or set(doc) != {"assessment"}:
        raise ValueError("expected one native Assessment")
    src = doc["assessment"]
    if not isinstance(src, dict) or src.get("mode") != "automated":
        raise ValueError("only automated scoped Assessments are eligible")
    spec = src.get("specification")
    if spec != {"id": "scap-ng.pre-alpha.assessment", "version": "0.4.0"}:
        raise ValueError("scoped Assessment requires declared pre-alpha 0.4.0")
    tests = src.get("tests")
    if not isinstance(tests, dict) or not tests:
        raise ValueError("scoped Assessment requires named Tests")
    staged = deepcopy(doc)
    for test_id, test in staged["assessment"]["tests"].items():
        if not isinstance(test, dict):
            raise ValueError(f"{test_id}: invalid Test")
        if "require" in test or "collected_items_require" not in test:
            raise ValueError(f"{test_id}: mixed or missing Test requirement grammar")
        requirement = test["collected_items_require"]
        if not isinstance(requirement, str) or not requirement:
            raise ValueError(f"{test_id}: invalid collected_items_require")
        test["require"] = test.pop("collected_items_require")
    # Expand the experimentally scoped scalar State fields into the already
    # versioned 0.4-A base State grammar. Independent Test Item requirements
    # and nested Windows record requirements remain untouched.
    staged = expand(staged)
    for test_id, test in staged["assessment"]["tests"].items():
        if "collected_items_require" in test or "state_fields_require" in test:
            raise ValueError(f"{test_id}: unlowered scoped grammar remains")
    # Exact source-shape inversion, not scanner semantic equivalence.
    inverse, _ = compact(staged)
    for test in inverse["assessment"]["tests"].values():
        if "collected_items_require" in test or "require" not in test:
            raise ValueError("unexpected inversely compacted Test grammar")
        test["collected_items_require"] = test.pop("require")
    if inverse != doc:
        raise ValueError("nonreversible scoped source or noncanonical shorthand")
    if doc == staged:
        raise ValueError("expected explicit scoped source lowering")
    return staged


def lower_all(documents, *, validate_base=True):
    if not isinstance(documents, dict) or not documents:
        raise ValueError("empty authoring inputs")
    staged = {}
    counters = Counter()
    validator = None
    if validate_base:
        from validate_native_json_schemas import build_validators
        schema_dir = Path(__file__).resolve().parents[1] / "schema/v0.4.0"
        validator = build_validators(schema_dir)["assessment.schema.json"]
    for path, doc in sorted(documents.items()):
        if not isinstance(doc, dict) or len(doc) != 1:
            raise ValueError(f"{path}: invalid native document")
        kind, content = next(iter(doc.items()))
        if kind != "assessment" or not isinstance(content, dict) or content.get("mode") != "automated":
            staged[path] = deepcopy(doc)
            counters["untouched_documents"] += 1
            continue
        try:
            converted = lower_one(doc)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"{path}: {exc}") from exc
        if validator is not None:
            errors = list(validator.iter_errors(converted))
            if errors:
                first = sorted(errors, key=lambda e: (list(map(str,e.absolute_path)),e.message))[0]
                raise ValueError(f"{path}: base 0.4-A schema invalid at "
                                 f"{list(first.absolute_path)!r}: {first.message}")
        staged[path] = converted
        counters["lowered_automated_assessments"] += 1
        counters["validated_base_assessments"] += int(validator is not None)
        counters["lowered_tests"] += len(converted["assessment"]["tests"])
    # Strictly preserve graph identities/edges. The only permitted syntax
    # changes are within automated Assessment documents.
    before = graph_index(documents)
    after = graph_index(staged)
    if before["counts"] != after["counts"] or len(before["nodes"]) != len(after["nodes"]):
        raise ValueError("source graph reference identity changed")
    for path, doc in documents.items():
        if path not in staged:
            raise ValueError("source path omitted")
        if not (doc.get("assessment", {}).get("mode") == "automated"):
            if canonical_json(doc) != canonical_json(staged[path]):
                raise ValueError("nonautomated source mutated: " + path)
    result = {
        "status": "REVERSIBLE_0.4_A_AUTHORING_LOWERING_NOT_COMPILATION",
        "source_graph_sha256": before["graph_sha256"],
        "lowered_graph_sha256": after["graph_sha256"],
        "source_counts": before["counts"],
        "lowered_counts": after["counts"],
        "counters": dict(sorted(counters.items())),
        "all_automated_sources_reversible": True,
        "base_schema_validation": "PASS" if validate_base else "NOT_PERFORMED",
        "approved_0_4_syntax": False,
        "native_bundle_compiled": False,
        "scanner_conformance_proven": False,
    }
    return staged, result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json-archive", required=True)
    parser.add_argument("--yaml-archive")
    parser.add_argument("--report-json")
    parser.add_argument("--expect-six-stig", action="store_true")
    args = parser.parse_args(argv)
    lowered, result = lower_all(read_authoring_archive(args.json_archive, "json"))
    if args.yaml_archive:
        from_yaml, yresult = lower_all(read_authoring_archive(args.yaml_archive, "yaml"))
        if yresult != result or graph_index(from_yaml)["graph_sha256"] != graph_index(lowered)["graph_sha256"]:
            raise ValueError("YAML versus JSON lowered A graph differs")
        result["yaml_json_agree"] = True
    if args.expect_six_stig:
        if (result["counters"]["lowered_automated_assessments"] != 872
                or result["counters"]["lowered_tests"] != 1375
                or result["source_counts"]["documents"] != 4001
                or result["source_counts"]["rule_choice_links"] != 2958):
            raise ValueError("six-STIG lowering counts differ from pinned source")
        result["pinned_corpus_check"] = "PASS"
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    print(output, end="")
    if args.report_json:
        Path(args.report_json).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
