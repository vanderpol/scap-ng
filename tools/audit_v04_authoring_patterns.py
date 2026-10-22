#!/usr/bin/env python3
"""Official SCAP-NG 0.4.0 authoring anti-pattern census and regression gate.

Find odd structures in the COMPLETE generated six-STIG JSON/YAML authoring
corpus, not research previews. This is a structural inventory, not an OVAL
source-identity or scanner-equivalence oracle. Genuine OVAL Set, evaluation,
and shared resource graphs must never be simplified from shape alone.

Optional pinned-baseline comparison rejects any INCREASE in high-confidence
redundancy categories. It is intentionally more general than the Bluetooth
exact-signature guard; the two independent checks complement one another.

Refs #248.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from v04_a_authoring_graph_index import read_authoring_archive, canonical_json

# Only newly introduced *strong* structural smells block canonical CI.
# A genuine original OVAL singleton Set, scoped Boolean grouping, or native
# schema-required inner capability MUST NOT become a false-positive failure.
# Every blocking hit still requires original OVAL/source review before rewriting.
HIGH_CONFIDENCE = frozenset((
    "mirrored_singleton_set_object",
    "repeated_identical_set_operand", "identical_consecutive_filters",
))
REVIEW_ONLY = frozenset((
    "singleton_set", "singleton_set_with_filters", "nested_singleton_set",
    "same_operator_boolean_nesting", "single_child_boolean",
    "redundant_inline_capability", "empty_set_operand_filters",
    "unreferenced_test", "passthrough_variable",
))
MAX_EXAMPLES = 15


def _short(path):
    return path[:-5] + ".json" if path.endswith(".yaml") else path


def _canonical(value):
    return canonical_json(value).decode("utf-8")


def scan(documents):
    counts = Counter()
    examples = defaultdict(list)
    pattern_sites = defaultdict(set)
    per_benchmark = defaultdict(Counter)
    docs = tests = 0

    def hit(code, path, assessment, test_id, route, *, extra=None):
        counts[code] += 1
        parts = path.split("/")
        benchmark = parts[1] if len(parts) > 1 else "unknown"
        per_benchmark[benchmark][code] += 1
        if code in HIGH_CONFIDENCE:
            # Audit ALL affected sites, not merely the first displayed samples.
            # Site identity and operator are part of the change detection:
            # moving an anomaly elsewhere must fail even if the total falls.
            pattern_sites[code].add(_canonical({
                "path": _short(path), "assessment": assessment,
                "test": test_id, "site": list(route), "details": extra,
            }))
        if len(examples[code]) < MAX_EXAMPLES:
            row = {"path": _short(path), "assessment": assessment,
                   "test": test_id, "site": list(route)}
            if extra:
                row["details"] = extra
            examples[code].append(row)

    for path, doc in sorted(documents.items()):
        docs += 1
        assessment = doc.get("assessment") if isinstance(doc, dict) else None
        if not isinstance(assessment, dict) or assessment.get("mode") != "automated":
            continue
        assessment_id = assessment.get("id")
        declared_tests = assessment.get("tests") or {}
        if not isinstance(declared_tests, dict):
            raise ValueError(f"{path}: invalid tests mapping")
        tests += len(declared_tests)
        referenced_tests = set()

        def walk(node, route, test_id, test_capability):
            if isinstance(node, list):
                for index, value in enumerate(node):
                    walk(value, route + (index,), test_id, test_capability)
                return
            if not isinstance(node, dict):
                return
            if "test" in node and isinstance(node["test"], str):
                referenced_tests.add(node["test"])

            # Report only real Object Set nodes, not unrelated properties
            # named "set" in the source provenance or runtime metadata.
            expression = node.get("set")
            if isinstance(expression, dict) and isinstance(expression.get("operands"), list):
                operands = expression["operands"]
                op = expression.get("operator")
                if len(operands) == 1:
                    hit("singleton_set", path, assessment_id, test_id, route + ("set",),
                        extra={"operator": op})
                    if isinstance(operands[0], dict) and operands[0].get("filters"):
                        hit("singleton_set_with_filters", path, assessment_id, test_id,
                            route + ("set",), extra={"operator": op})
                    member = operands[0] if isinstance(operands[0], dict) else {}
                    child = member.get("set")
                    if (isinstance(child, dict) and
                            isinstance(child.get("operands"), list) and
                            len(child["operands"]) == 1):
                        hit("nested_singleton_set", path, assessment_id, test_id,
                            route + ("set",), extra={"operator": op})
                    if (set(node) == {"object_title", "set"}
                            and set(member) == {"object", "filters"}
                            and isinstance(member["object"], dict)
                            and member["object"].get("object_title") == node["object_title"]):
                        hit("mirrored_singleton_set_object", path, assessment_id,
                            test_id, route, extra={"operator": op})
                serialized = [_canonical(x) for x in operands]
                if len(serialized) > len(set(serialized)):
                    hit("repeated_identical_set_operand", path, assessment_id,
                        test_id, route + ("set",), extra={"operator": op})
            filters = node.get("filters")
            if isinstance(filters, list):
                if not filters:
                    hit("empty_set_operand_filters", path, assessment_id,
                        test_id, route + ("filters",))
                for i in range(1, len(filters)):
                    if filters[i] == filters[i-1]:
                        hit("identical_consecutive_filters", path, assessment_id,
                            test_id, route + ("filters", i))
            # This does not claim Boolean aggregation can be flattened without
            # checking source OVAL and unknown/error behavior first.
            if len(node) == 1:
                key = next(iter(node))
                value = node[key]
                if key in ("all", "any") and isinstance(value, list):
                    if len(value) == 1:
                        hit("single_child_boolean", path, assessment_id, test_id, route,
                            extra={"operator": key})
                    for item in value:
                        if isinstance(item, dict) and set(item) == {key}:
                            hit("same_operator_boolean_nesting", path, assessment_id,
                                test_id, route, extra={"operator": key})
            # Nested inline objects can redundantly repeat the enclosing
            # Test capability; the base Test-level guard handles first layer.
            if ("object" in node and isinstance(node["object"], dict)
                    and test_capability is not None):
                ob = node["object"]
                if ob.get("capability") == test_capability:
                    hit("redundant_inline_capability", path, assessment_id,
                        test_id, route + ("object",))
            for name, value in node.items():
                walk(value, route + (name,), test_id, test_capability)

        for test_id, test in declared_tests.items():
            if not isinstance(test, dict):
                raise ValueError(f"{path}: invalid Test {test_id}")
            walk(test, ("assessment", "tests", test_id), test_id, test.get("capability"))
        walk(assessment.get("evaluate"), ("assessment", "evaluate"), None, None)
        for test_id in sorted(declared_tests):
            if test_id not in referenced_tests:
                hit("unreferenced_test", path, assessment_id, test_id,
                    ("assessment", "tests", test_id))
        variables = assessment.get("variables") or {}
        if isinstance(variables, dict):
            for variable_id, var in sorted(variables.items()):
                if isinstance(var, dict):
                    expression = var.get("expression")
                    if isinstance(expression, dict) and (
                        set(expression) == {"variable"} or
                        set(expression) == {"variable_component"}
                    ):
                        hit("passthrough_variable", path, assessment_id, None,
                            ("assessment", "variables", variable_id),
                            extra={"variable": variable_id})
                    walk(var, ("assessment", "variables", variable_id), None, None)
        for obj_id, obj in sorted((assessment.get("objects") or {}).items()):
            walk(obj, ("assessment", "objects", obj_id), None, None)
        for obj_id, obj in sorted((assessment.get("shared_objects") or {}).items()):
            walk(obj, ("assessment", "shared_objects", obj_id), None, None)

    return {
        "status": "STRUCTURAL_REVIEW_INVENTORY_NOT_OVAL_OR_SCANNER_PARITY",
        "documents": docs, "automated_tests": tests,
        "counts": dict(sorted(counts.items())),
        "by_benchmark": {name: dict(sorted(rows.items()))
                         for name, rows in sorted(per_benchmark.items())},
        "examples": {name: rows for name, rows in sorted(examples.items())},
        "pattern_sites": {name: sorted(rows)
                          for name, rows in sorted(pattern_sites.items())},
        "high_confidence_non_growth": sorted(HIGH_CONFIDENCE),
        "review_only_no_automatic_rewrite": sorted(REVIEW_ONLY),
        "interpretation": {
            "redundant_inline_capability":
                "Same as enclosing Test, but nested native Object schema currently REQUIRES capability; not a proven redundant authored field",
            "empty_set_operand_filters":
                "Current 0.4 native Set operand schema REQUIRES a filters array, including [] when no Filter is applied",
            "same_operator_boolean_nesting":
                "Could preserve meaningful architecture/check grouping; do not flatten without source/evaluation evidence",
            "singleton_set":
                "Might be original OVAL Set or converter-generated identity; only pinned original XML resolves it",
        },
        "original_oval_identity_checked": False,
        "scanner_runtime_equivalence_checked": False,
    }


def compare(baseline, candidate, *, restored_applicability_source=False):
    before_scope = (baseline.get("documents"), baseline.get("automated_tests"))
    after_scope = (candidate.get("documents"), candidate.get("automated_tests"))
    # The immutable October 20 baseline omits 11 source-backed Applicability
    # Assessments (15 Tests) whose 22 dangling links were fixed with the
    # SHA-pinned 0.3 source. Keep strict pattern regression checks for every
    # existing and restored path; only this reviewed scope delta is allowed.
    accepted_scope = ((4001, 1375), (4012, 1390))
    if before_scope != after_scope and not (
            restored_applicability_source and (before_scope, after_scope) == accepted_scope):
        raise ValueError("Six-STIG corpus scope changed; new baseline needs review")
    regressions = []
    for name in sorted(HIGH_CONFIDENCE):
        before = baseline["counts"].get(name, 0)
        after = candidate["counts"].get(name, 0)
        new_sites = sorted(set(candidate["pattern_sites"].get(name, [])) -
                           set(baseline["pattern_sites"].get(name, [])))
        if after > before or new_sites:
            regressions.append({"pattern": name, "baseline": before,
                                "candidate": after,
                                "new_sites": new_sites[:15],
                                "sample": candidate["examples"].get(name, [])[:4]})
    return {"status": "PASS" if not regressions else "FAIL",
            "restored_applicability_source": (before_scope, after_scope) == accepted_scope,
            "baseline_counts": baseline["counts"],
            "candidate_counts": candidate["counts"],
            "new_structural_regressions": regressions,
            "source_review_required_before_any_rewrite": True}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--archive", type=Path, required=True)
    p.add_argument("--baseline-archive", type=Path)
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--assert-six", action="store_true")
    p.add_argument("--restored-applicability-source", action="store_true",
                   help="Allow only the pinned 11-Assessment/15-Test restoration scope delta")
    args = p.parse_args()
    fmt = "yaml" if args.archive.name.endswith(".yaml.zip") else "json"
    candidate = scan(read_authoring_archive(args.archive, fmt))
    baseline = None
    if args.baseline_archive is not None:
        base_fmt = "yaml" if args.baseline_archive.name.endswith(".yaml.zip") else "json"
        baseline = scan(read_authoring_archive(args.baseline_archive, base_fmt))
    if args.assert_six and (candidate["documents"], candidate["automated_tests"]) != (4012, 1390):
        raise ValueError("Unexpected canonical 0.4.0 six-STIG authoring population")
    gate = compare(baseline, candidate,
                   restored_applicability_source=args.restored_applicability_source) if baseline is not None else None
    report = {"candidate": candidate, "comparison": gate}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n",
                           encoding="utf-8")
    print(json.dumps({
        "candidate_documents": candidate["documents"],
        "candidate_automated_tests": candidate["automated_tests"],
        "candidate_patterns": candidate["counts"],
        "baseline_patterns": baseline["counts"] if baseline else None,
        "comparison_status": gate["status"] if gate else "NOT_REQUESTED",
        "regressions": gate["new_structural_regressions"] if gate else [],
        "examples": {k: v[:3] for k, v in candidate["examples"].items()},
    }, indent=2, sort_keys=True))
    if gate is not None and gate["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
