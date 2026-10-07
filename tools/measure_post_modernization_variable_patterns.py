#!/usr/bin/env python3
"""Classify Variables that survive the proven 0.3 modernization census.

Research only. This tool applies the same exact/reversible presentation and
Observation/foreach transforms as the full corpus census, then describes the
remaining Variable graphs. It performs no new rewrite.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from measure_full_modernization_census import (
    apply_observation,
    build_observation_plan,
    classify,
    evaluate_metrics,
    load_assessments,
    promote_to_research_03,
    residual_reasons,
)
from measure_residual_complexity_patterns import (
    FUNCTION_KEYS,
    expression_variable_kind,
    walk,
)
from research_inline_private_components import inline_private, reexpand, first_difference
from scap_upconvert_v003.foreach_modernization import modernize_foreach_v1


def exact_variable_refs(value: Any, variable_id: str, path=()):
    if isinstance(value, dict):
        if set(value) == {"variable"} and value.get("variable") == variable_id:
            yield path
        for key, child in value.items():
            yield from exact_variable_refs(child, variable_id, path + (str(key),))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from exact_variable_refs(child, variable_id, path + (str(index),))


def consumer_context(path: tuple[str, ...]) -> str:
    """Classify the semantic consumer, including components localized under Tests."""
    if not path:
        return "other"

    root = path[0]
    if root == "variables":
        return "variable"
    if root == "states":
        return "state"
    if root == "objects":
        # A Filter-local State can live lexically inside an Object after the
        # locality transform; classify by semantic consumer rather than root.
        tail = path[2:] if len(path) > 2 else ()
        if "state" in tail or "states" in tail:
            return "state"
        return "object"
    if root == "tests":
        # Consumer-local authoring places private Objects and States beneath
        # the Test. Do not collapse their Variable references into "test".
        tail = path[2:] if len(path) > 2 else ()
        if "states" in tail or "state" in tail:
            return "state"
        if "object" in tail or "objects" in tail:
            return "object"
        return "test"
    if root == "evaluate":
        return "evaluate"
    if root == "observations":
        return "observation"
    return root


def semantic_variable_kind(variable: dict) -> str:
    source_kind = variable.get("kind")
    if source_kind == "external":
        return "external_input"
    if source_kind == "constant":
        return "constant_literal"
    if source_kind == "local":
        return expression_variable_kind(variable)
    return "unknown_" + str(source_kind or "kind")


STATIC_FUNCTION_KEYS = {
    "arithmetic", "begin", "concat", "count", "end", "escape_regex",
    "glob_to_regex", "merge", "regex_capture", "split", "substring",
    "unique", "values", "variable_component",
}


def compile_time_static_variables(variables: dict) -> dict[str, bool]:
    """Classify Variables whose complete dependency closure is source-time static.

    This is deliberately conservative research classification. Constants are
    static. Local Variables are static only when their expression contains no
    Object/Observation/external/runtime source, uses only known deterministic
    expression forms, and every referenced Variable is itself static.
    """
    memo: dict[str, bool] = {}
    visiting: set[str] = set()

    def expression_static(value: Any) -> bool:
        if value is None or isinstance(value, (str, int, float, bool)):
            return True
        if isinstance(value, list):
            return all(expression_static(child) for child in value)
        if not isinstance(value, dict):
            return False

        if set(value) == {"variable"}:
            ref = value.get("variable")
            return isinstance(ref, str) and variable_static(ref)

        # Structured runtime bindings such as Observation exports are not
        # compile-time static Variable references.
        if "observation" in value or "assessment" in value or "input" in value:
            return False
        if "object" in value or "object_values" in value or "object_component" in value:
            return False

        semantic_function_keys = set(value) & FUNCTION_KEYS
        if semantic_function_keys - STATIC_FUNCTION_KEYS:
            return False

        return all(expression_static(child) for child in value.values())

    def variable_static(variable_id: str) -> bool:
        if variable_id in memo:
            return memo[variable_id]
        if variable_id in visiting:
            memo[variable_id] = False
            return False
        payload = variables.get(variable_id)
        if not isinstance(payload, dict):
            memo[variable_id] = False
            return False

        visiting.add(variable_id)
        kind = payload.get("kind")
        if kind == "constant":
            result = True
        elif kind == "external":
            result = False
        elif kind == "local":
            result = expression_static(payload.get("expression"))
        else:
            result = False
        visiting.remove(variable_id)
        memo[variable_id] = result
        return result

    return {
        variable_id: variable_static(variable_id)
        for variable_id in variables
    }


def expression_functions(variable: dict) -> Counter:
    counts = Counter()
    expression = variable.get("expression")
    if expression is None:
        return counts
    for node in walk(expression):
        if isinstance(node, dict):
            for key in node:
                if key in FUNCTION_KEYS:
                    counts[key] += 1
    return counts


def dependency_edges(variables: dict) -> list[tuple[str, str]]:
    edges = []
    for consumer_id, payload in variables.items():
        if not isinstance(payload, dict):
            continue
        for producer_id in variables:
            if producer_id == consumer_id:
                continue
            if any(exact_variable_refs(payload, producer_id)):
                edges.append((consumer_id, producer_id))
    return sorted(set(edges))


def longest_chain(variables: dict, edges: list[tuple[str, str]]) -> int:
    deps = defaultdict(set)
    for consumer, producer in edges:
        deps[consumer].add(producer)
    memo = {}
    visiting = set()

    def depth(node: str) -> int:
        if node in memo:
            return memo[node]
        if node in visiting:
            return 0
        visiting.add(node)
        value = 1
        if deps.get(node):
            value = 1 + max(depth(child) for child in deps[node])
        visiting.remove(node)
        memo[node] = value
        return value

    return max((depth(node) for node in variables), default=0)


def fanout_bucket(value: int) -> str:
    if value == 0:
        return "0"
    if value == 1:
        return "1"
    if value == 2:
        return "2"
    if value <= 5:
        return "3-5"
    return "6+"


def analyze_remaining_variables(assessment: dict, foreach_report: dict) -> dict:
    variables = assessment.get("variables") or {}
    review_by_variable = {}
    for row in foreach_report.get("review_required") or []:
        variable = row.get("variable")
        if variable:
            review_by_variable[variable] = sorted(set(row.get("reasons") or []))

    rows = []
    expression_kinds = Counter()
    source_kinds = Counter()
    function_counts = Counter()
    consumer_contexts = Counter()
    fanouts = Counter()
    reused = 0
    chained = 0
    static_map = compile_time_static_variables(variables)
    static_variables = 0
    static_constants = 0
    static_locals = 0
    static_multiple_consumers = 0
    static_single_consumer = 0
    static_single_consumer_contexts = Counter()
    static_context_signatures = Counter()
    static_consumer_contexts = Counter()

    for variable_id, payload in sorted(variables.items()):
        if not isinstance(payload, dict):
            continue
        search_surface = {
            key: value for key, value in assessment.items()
            if key != "variables"
        }
        refs = list(exact_variable_refs(search_surface, variable_id))
        variable_refs = []
        for other_id, other_payload in variables.items():
            if other_id == variable_id:
                continue
            variable_refs.extend(
                ("variables", other_id) + path
                for path in exact_variable_refs(other_payload, variable_id)
            )
        refs.extend(variable_refs)
        contexts = Counter(consumer_context(path) for path in refs)
        funcs = expression_functions(payload)
        source_kind = str(payload.get("kind") or "unknown")
        kind = semantic_variable_kind(payload)
        source_kinds[source_kind] += 1
        expression_kinds[kind] += 1
        function_counts.update(funcs)
        consumer_contexts.update(contexts)
        fanouts[fanout_bucket(len(refs))] += 1
        if len(refs) >= 2:
            reused += 1
        if contexts.get("variable", 0):
            chained += 1

        is_static = bool(static_map.get(variable_id))
        if is_static:
            static_variables += 1
            static_consumer_contexts.update(contexts)
            if source_kind == "constant":
                static_constants += 1
            elif source_kind == "local":
                static_locals += 1
            signature = "+".join(sorted(contexts)) if contexts else "unreferenced"
            static_context_signatures[signature] += 1
            if len(refs) >= 2:
                static_multiple_consumers += 1
            elif len(refs) == 1:
                static_single_consumer += 1
                static_single_consumer_contexts.update(contexts)

        rows.append({
            "variable_id": variable_id,
            "kind": kind,
            "source_kind": source_kind,
            "datatype": payload.get("datatype"),
            "consumer_count": len(refs),
            "consumer_contexts": dict(contexts),
            "function_counts": dict(funcs),
            "foreach_v1_refusal_reasons": review_by_variable.get(variable_id, []),
            "compile_time_static": is_static,
        })

    edges = dependency_edges(variables)
    return {
        "variables": len(rows),
        "source_kind_counts": dict(source_kinds),
        "expression_kind_counts": dict(expression_kinds),
        "function_counts": dict(function_counts),
        "consumer_context_counts": dict(consumer_contexts),
        "fanout_bucket_counts": dict(fanouts),
        "variables_with_multiple_consumers": reused,
        "variables_consumed_by_variables": chained,
        "compile_time_static_variables": static_variables,
        "compile_time_static_constants": static_constants,
        "compile_time_static_locals": static_locals,
        "compile_time_static_variables_with_multiple_consumers": static_multiple_consumers,
        "compile_time_static_single_consumer_variables": static_single_consumer,
        "compile_time_static_single_consumer_context_counts": dict(static_single_consumer_contexts),
        "compile_time_static_context_signature_counts": dict(static_context_signatures),
        "compile_time_static_consumer_context_counts": dict(static_consumer_contexts),
        "runtime_variables": len(rows) - static_variables,
        "variable_dependency_edges": len(edges),
        "max_variable_chain_depth": longest_chain(variables, edges),
        "rows": rows,
    }


def pattern_signature(analysis: dict) -> str:
    return json.dumps({
        "expression_kinds": analysis["expression_kind_counts"],
        "function_names": sorted(analysis["function_counts"]),
        "fanout_buckets": analysis["fanout_bucket_counts"],
        "has_variable_chaining": analysis["variables_consumed_by_variables"] > 0,
        "chain_depth": analysis["max_variable_chain_depth"],
    }, sort_keys=True, separators=(",", ":"))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--label", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--top", type=int, default=25)
    args = p.parse_args()

    all_rows = load_assessments(args.root)
    plan, observation_summary, observation_errors = build_observation_plan(all_rows)

    assessments = []
    expression_kinds = Counter()
    source_kinds = Counter()
    function_counts = Counter()
    consumer_contexts = Counter()
    fanout_buckets = Counter()
    refusal_reasons = Counter()
    patterns = defaultdict(list)
    variable_total = 0
    complex_variable_rules = 0
    multiple_consumers = 0
    variable_chained = 0
    dependency_edges_total = 0
    max_chain_depth = 0
    compile_time_static_total = 0
    compile_time_static_constants = 0
    compile_time_static_locals = 0
    compile_time_static_multiple_consumers = 0
    compile_time_static_single_consumer = 0
    compile_time_static_single_contexts = Counter()
    compile_time_static_signatures = Counter()
    compile_time_static_contexts = Counter()
    runtime_variables = 0

    for index, source_row in enumerate(all_rows):
        if source_row["kind"] != "rule":
            continue

        original = source_row["doc"]
        working = original
        planned = plan.get(index)
        if planned is not None:
            kind, observation, _ = planned
            extracted, restored, _ = apply_observation(kind, working, observation)
            if restored != working:
                detail = first_difference(working, restored) or "unknown difference"
                raise ValueError(
                    f"Observation round-trip mismatch: {source_row['relative_path']}: {detail}"
                )
            working = extracted

        foreach_input = promote_to_research_03(working)
        foreach_doc, foreach_report = modernize_foreach_v1(
            foreach_input, enabled=True
        )
        rendered, identity = inline_private(
            foreach_doc,
            inline_private_set_operands=True,
            inline_private_filtered_set_operands=True,
            inline_state_consumers=True,
            inline_variable_object_consumers=True,
        )
        expanded = reexpand(rendered, identity)
        if expanded != foreach_doc:
            detail = first_difference(foreach_doc, expanded) or "unknown difference"
            raise ValueError(
                f"Locality round-trip mismatch: {source_row['relative_path']}: {detail}"
            )

        evalm = evaluate_metrics(source_row["path"], rendered)
        category = classify(
            rendered,
            identity,
            evalm,
            observation_applied=planned is not None,
            foreach_applied=int(
                foreach_report["stats"].get("rewrites_applied", 0) or 0
            ),
        )
        if category != "meaningfully_complex":
            continue
        if not (rendered["assessment"].get("variables") or {}):
            continue

        complex_variable_rules += 1
        analysis = analyze_remaining_variables(
            rendered["assessment"], foreach_report
        )
        variable_total += analysis["variables"]
        source_kinds.update(analysis["source_kind_counts"])
        expression_kinds.update(analysis["expression_kind_counts"])
        function_counts.update(analysis["function_counts"])
        consumer_contexts.update(analysis["consumer_context_counts"])
        fanout_buckets.update(analysis["fanout_bucket_counts"])
        multiple_consumers += analysis["variables_with_multiple_consumers"]
        variable_chained += analysis["variables_consumed_by_variables"]
        dependency_edges_total += analysis["variable_dependency_edges"]
        compile_time_static_total += analysis["compile_time_static_variables"]
        compile_time_static_constants += analysis["compile_time_static_constants"]
        compile_time_static_locals += analysis["compile_time_static_locals"]
        compile_time_static_multiple_consumers += analysis[
            "compile_time_static_variables_with_multiple_consumers"
        ]
        compile_time_static_single_consumer += analysis[
            "compile_time_static_single_consumer_variables"
        ]
        compile_time_static_single_contexts.update(
            analysis["compile_time_static_single_consumer_context_counts"]
        )
        compile_time_static_signatures.update(
            analysis["compile_time_static_context_signature_counts"]
        )
        compile_time_static_contexts.update(
            analysis["compile_time_static_consumer_context_counts"]
        )
        runtime_variables += analysis["runtime_variables"]
        max_chain_depth = max(
            max_chain_depth, analysis["max_variable_chain_depth"]
        )
        for row in analysis["rows"]:
            refusal_reasons.update(row["foreach_v1_refusal_reasons"])

        signature = pattern_signature(analysis)
        patterns[signature].append({
            "assessment_id": rendered["assessment"].get("id"),
            "path": source_row["relative_path"],
            "residual_reasons": residual_reasons(
                rendered, identity, evalm
            ),
            "variable_analysis": analysis,
        })

    ranked = sorted(patterns.items(), key=lambda kv: (-len(kv[1]), kv[0]))
    top_patterns = []
    for signature, members in ranked[:args.top]:
        exemplar = members[0]["variable_analysis"]
        top_patterns.append({
            "count": len(members),
            "percent_of_complex_variable_rules": (
                round(100.0 * len(members) / complex_variable_rules, 2)
                if complex_variable_rules else 0.0
            ),
            "signature": json.loads(signature),
            "examples": [
                {
                    "assessment_id": row["assessment_id"],
                    "residual_reasons": row["residual_reasons"],
                }
                for row in members[:10]
            ],
        })

    report = {
        "format": "scap-ng-post-modernization-variable-census-0.1",
        "status": "research_only_not_accepted_design",
        "label": args.label,
        "complex_rules_with_variables": complex_variable_rules,
        "remaining_variables": variable_total,
        "source_kind_counts": dict(source_kinds),
        "expression_kind_counts": dict(expression_kinds),
        "function_counts": dict(function_counts),
        "consumer_context_counts": dict(consumer_contexts),
        "fanout_bucket_counts": dict(fanout_buckets),
        "variables_with_multiple_consumers": multiple_consumers,
        "variables_consumed_by_variables": variable_chained,
        "compile_time_static_variables": compile_time_static_total,
        "compile_time_static_constants": compile_time_static_constants,
        "compile_time_static_locals": compile_time_static_locals,
        "compile_time_static_variables_with_multiple_consumers": compile_time_static_multiple_consumers,
        "compile_time_static_single_consumer_variables": compile_time_static_single_consumer,
        "compile_time_static_single_consumer_context_counts": dict(compile_time_static_single_contexts),
        "compile_time_static_context_signature_counts": dict(compile_time_static_signatures),
        "compile_time_static_consumer_context_counts": dict(compile_time_static_contexts),
        "runtime_variables": runtime_variables,
        "variable_dependency_edges": dependency_edges_total,
        "max_variable_chain_depth": max_chain_depth,
        "foreach_v1_refusal_reason_counts": dict(refusal_reasons),
        "unique_variable_pattern_signatures": len(patterns),
        "pattern_signature_counts": [
            {
                "signature": json.loads(signature),
                "count": len(members),
            }
            for signature, members in ranked
        ],
        "top_patterns": top_patterns,
        "observation_plan": observation_summary,
        "observation_candidate_errors": observation_errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        key: report[key] for key in (
            "label",
            "complex_rules_with_variables",
            "remaining_variables",
            "source_kind_counts",
            "expression_kind_counts",
            "function_counts",
            "fanout_bucket_counts",
            "variables_with_multiple_consumers",
            "variables_consumed_by_variables",
            "compile_time_static_variables",
            "compile_time_static_constants",
            "compile_time_static_locals",
            "compile_time_static_single_consumer_variables",
            "compile_time_static_variables_with_multiple_consumers",
            "runtime_variables",
            "max_variable_chain_depth",
            "unique_variable_pattern_signatures",
        )
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
