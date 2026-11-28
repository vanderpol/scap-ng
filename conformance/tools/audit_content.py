#!/usr/bin/env python3
"""Reconcile specification inventory and native test-content coverage."""
from __future__ import annotations

import argparse
from collections import Counter
import json

from oval_source_audit import scan_xml
from runner import CONFORMANCE, load

REPORT = CONFORMANCE / "content-coverage.json"

# Paths in these sections locate the exact rows in existing generated ledgers.
# The witnesses retain the evidence scope recorded in their source ledgers.
DETAILS = {
    "canonical_schema": "schema-coverage.json#/specification",
    "schema_properties": "schema-coverage.json#/property_groups",
    "schema_constraints": "schema-coverage.json#/constraints",
    "canonical_operators_and_functions": "schema-coverage.json#/operator_inventory",
    "schema_enum_const_matches": "qualification/schema-value-occurrences.json#/occurrences",
    "capability_constraints": "coverage-audit.json#/capability_constraints",
    "comparison_operators": "coverage-audit.json#/operators",
    "cardinalities": "coverage-audit.json#/cardinalities",
    "variable_functions": "coverage-audit.json#/variable_functions",
    "set_filters": "coverage-audit.json#/set_filter_semantics",
    "applicability": "coverage-audit.json#/applicability",
    "organizational_input_guards": "coverage-audit.json#/input_guards",
    "approved_decisions": "coverage-audit.json#/approved_normative_decisions",
    "native_content_suites": "suite-index.json#/suites",
    "oval_5_12_3_source": "oval-source-coverage.json#/oval_5_12_3_tests",
    "oval_6_0_esxi_source": "oval-source-coverage.json#/oval_6_0_esxi_tests",
    "consumer_observations": "qualification/coverage.json#/qualification",
}


def pointer_value(reference):
    filename, _, fragment = reference.partition("#")
    value = load(CONFORMANCE / filename)
    for segment in fragment.removeprefix("/").split("/") if fragment else ():
        value = value[segment.replace("~1", "/").replace("~0", "~")]
    return value


def field_datatypes(capability, items):
    """Reconcile mapping field/datatype pairs with typed fixture data."""
    fields = {}
    for item in items:
        if item["capability"] != capability:
            continue
        for field, evidence in item.get("fields", {}).items():
            values = evidence if isinstance(evidence, list) else [evidence]
            for value in values:
                if isinstance(value, dict) and "value" in value:
                    fields.setdefault(field, set()).add(value["datatype"])
    return fields


def supplemental_datatypes():
    equality_path = "exact-equality/exact-equality.assessment.yaml"
    equality = load(CONFORMANCE / equality_path)["assessment"]
    literals = [
        equality["variables"][test["variable"]]["expression"]["literal"]
        for test in equality["tests"].values()
        if test["capability"] == "variable.value"
    ]
    result_path = "result-evidence/owner.result.yaml"
    result = load(CONFORMANCE / result_path)["assessment_result"]
    items = [row["item"] for test in result["tests"] for row in test["per_item_results"]]
    return {
        "unix.file": (result_path, field_datatypes("unix.file", items)),
        "variable.value": (equality_path, {"value": {literal["datatype"] for literal in literals}}),
    }


def oval_source_counts(oval):
    baseline = oval["oval_5_12_3_native_capability_counts"]
    supplemental = Counter()
    covered = set()
    paths = sorted((CONFORMANCE / "oval-self-assertion").rglob("*.xml"))
    for path in paths:
        document, tests = scan_xml(path.read_bytes())
        supplemental["definitions"] += len(document["ids"]["definitions"])
        supplemental["tests"] += len(document["ids"]["tests"])
        for name, _ in tests:
            covered.update(
                row["capability"] for row in oval["oval_5_12_3_tests"][name]["mappings"]
                if row["status"] == "supported"
            )
    missing = set(baseline["missing_source_test"])
    return {
        "mapped": baseline["mapped"],
        "with_source_test_before": baseline["with_source_test"],
        "with_source_test_after": baseline["with_source_test"] + len(covered & missing),
        "missing_source_test_after": sorted(missing - covered),
        "supplemental_xml_files": len(paths),
        "definitions_before": oval["self_assertion_counts"]["definitions"],
        "definitions_after": oval["self_assertion_counts"]["definitions"] + supplemental["definitions"],
        "tests_before": oval["self_assertion_counts"]["tests"],
        "tests_after": oval["self_assertion_counts"]["tests"] + supplemental["tests"],
    }


def build():
    inventory = load(CONFORMANCE / "schema-coverage.json")
    manifest = load(CONFORMANCE / "manifest.json")
    occurrences = load(CONFORMANCE / "qualification/schema-value-occurrences.json")
    oval = load(CONFORMANCE / "oval-source-coverage.json")
    aggregate = load(CONFORMANCE / "coverage-audit.json")
    index = load(CONFORMANCE / "suite-index.json")
    if {data["schema_commit"] for data in (inventory, manifest, occurrences, aggregate, index)} != {inventory["schema_commit"]}:
        raise ValueError("Coverage sources disagree on the canonical schema pin")
    for reference in DETAILS.values():
        pointer_value(reference)
    vectors = {row["capability"]: row for row in manifest["capabilities"]}
    if vectors.keys() != {row["capability"] for row in inventory["capabilities"]}:
        raise ValueError("Native capability suite disagrees with canonical mappings")

    counts = {scope: Counter() for scope in ("active", "experimental")}
    capabilities = {scope: {} for scope in counts}
    supplemental = supplemental_datatypes()
    for spec in inventory["capabilities"]:
        capability = spec["capability"]
        scope = "experimental" if spec["status"] == "experimental" else "active"
        witness = vectors[capability]
        fixture = load(CONFORMANCE / witness["fixture"])
        typed = field_datatypes(capability, (
            item for details in fixture["variants"].values() for item in details.get("items", [])
        ))
        targeted_path, targeted = supplemental.get(capability, (None, {}))
        missing = {}
        supplemental_matches = {}
        counters = counts[scope]
        counters["capabilities"] += 1
        for field, datatypes in spec["field_datatypes"].items():
            seen = typed.get(field, set())
            absent = set(datatypes) - seen
            newly_matched = absent & targeted.get(field, set())
            if newly_matched:
                supplemental_matches[field] = sorted(newly_matched)
            if still_missing := absent - newly_matched:
                missing[field] = sorted(still_missing)
            counters["declared_field_datatypes"] += len(datatypes)
            counters["typed_baseline_fixture_matches"] += len(datatypes) - len(absent)
            counters["typed_indexed_fixture_matches"] += len(datatypes) - len(absent) + len(newly_matched)
        capabilities[scope][capability] = {
            "mapping": spec["source_path"],
            "assessment": witness["assessment"],
            "fixture": witness["fixture"],
            "expected": witness["expected"],
            "missing_datatypes_from_indexed_fixtures": missing,
        }

        if supplemental_matches:
            capabilities[scope][capability]["supplemental_datatypes"] = {
                "source": targeted_path, "fields": supplemental_matches,
            }

    comparison = inventory["operator_inventory"]["comparison"]
    return {
        "format": "scap-ng-specification-to-test-content-1",
        "schema_commit": inventory["schema_commit"],
        "schema_family_sha256": inventory["schema_family_sha256"],
        "excluded": {
            "for_each": "Deferred to 0.5.0 consideration. PR #130 remains outside this goal.",
            "oval_5_12_3_esx": "Deprecated source Tests excluded. OVAL 6.0 ESXi is tracked separately.",
        },
        "detailed_ledgers": DETAILS,
        "counts": {
            "inventory": inventory["counts"],
            "mapped_capability_content": {scope: dict(rows) for scope, rows in counts.items()},
            "enum_const": occurrences["coverage"],
            "oval_5_12_3_sources": oval_source_counts(oval),
            "oval_6_0_esxi_dispositions": dict(Counter(
                row["status"] for row in oval["oval_6_0_esxi_tests"].values()
            )),
        },
        "capabilities": capabilities,
        "interpretation": {
            "typed_baseline_fixture_matches": "A mapping datatype appears with a value in its baseline capability fixture. "
                                              "It may lack an independently checked operation or boundary and "
                                              "does not include targeted supplemental fixtures.",
            "typed_indexed_fixture_matches": "Also includes typed evidence in supplemental suites linked to these rows. "
                                             "Only explicitly indexed supplemental suites enter this measure.",
            "schema_enum_const_matches": occurrences["interpretation"],
            "schema_properties_and_constraints": "Complete source inventory. Per-occurrence exercised and rejected "
                                                 "coverage remains open beyond the linked enum and const audit.",
        },
        "new_independent_witnesses": {
            "exact_integer_string_equality": "exact-equality/expected.json",
            "complete_result_evidence": "result-evidence/expected.json",
            "variable_function_boundaries": "function-boundaries/expected.json",
        },
        "remaining": {
            "field_datatype_combinations": "Use each capability row's missing_datatypes_from_indexed_fixtures "
                                          "and reconcile it with supplemental typed outcome manifests.",
            "operator_semantics": {
                "exact_integer_and_string_equality": "exact-equality/expected.json",
                "other_operator_families_require_separate_review": sorted(set(comparison) - {"equals"}),
                "note": "The canonical operator list includes inherited surface names. "
                        "Use comparison_operators for the accepted spelling and existing structural witnesses. "
                        "A shared operator template does not establish every admitted operand, field or boundary.",
            },
            "unmatched_schema_values": "Use the enum and const ledger's reachable values without a matching scope. "
                                       "Author valid boundary cases or expected rejections for the exact schema locations.",
            "outcomes_held_by_specification": [
                "docs/contracts/0.4-semantic-holds.md",
                "docs/DOCUMENTATION-CONTRACT-DECISIONS.md#item-materialization-and-projection",
                "https://github.com/vanderpol/scap-ng/pull/135",
                "https://github.com/vanderpol/scap-ng/pull/136",
            ],
            "consumer_issues": [
                "https://github.com/vanderpol/scap-ng-tools/issues/127",
                "https://github.com/vanderpol/scap-ng-tools/issues/128",
                "https://github.com/vanderpol/scap-ng-ri/issues/196",
                "https://github.com/vanderpol/scap-ng-ri/issues/202",
                "https://github.com/vanderpol/scap-ng-ri/issues/305",
                "https://github.com/vanderpol/scap-ng-ri/issues/309",
                "https://github.com/vanderpol/scap-ng-vscode/issues/75",
            ],
            "native_or_source_issues": [
                "https://github.com/vanderpol/scap-ng/issues/132",
                "https://github.com/vanderpol/scap-ng/issues/133",
            ],
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = build()
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not REPORT.is_file() or REPORT.read_text(encoding="utf-8") != rendered:
            raise SystemExit("Specification-to-test-content matrix is stale")
    else:
        REPORT.write_text(rendered, encoding="utf-8")
    print(json.dumps(result["counts"]["mapped_capability_content"], sort_keys=True))
