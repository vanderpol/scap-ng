#!/usr/bin/env python3
"""Read-only source-backed census of English-first grammar bottlenecks.

Counts distinct automated Assessment files and their named Test nodes from
the immutable r3 release, NOT Rule or per-benchmark occurrences. No rewrites.
Research #235. Unknown source shapes are visible, not silently accepted.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import zipfile

import yaml

PINNED_SHA256 = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"
LOGICAL_KEYS = {"and", "or", "not", "all", "any", "one", "odd"}
RESERVED = {"require", "record", "value_match", "datatype", "redact_result"}
EXAMPLES_LIMIT = 4


def source_object(assessment, test):
    obj = test.get("object")
    if isinstance(obj, str):
        obj = (assessment.get("shared_objects") or {}).get(obj)
        return obj, "shared_reference"
    if isinstance(obj, dict):
        return obj, "inline"
    return None, "missing_or_unusual"


def collect_details(obj):
    if not isinstance(obj, dict):
        return "unresolved", [], 0, False
    root_types = [k for k in ("select", "collect", "set", "for_each") if k in obj]
    if not root_types:
        return "other", root_types, 0, False
    primary = "+".join(root_types)
    def recurse(node):
        if not isinstance(node, (dict, list)):
            return (0, False)
        if isinstance(node, list):
            vals = [recurse(item) for item in node]
            return sum(x[0] for x in vals), any(x[1] for x in vals)
        c = int("for_each" in node)
        dynamic = "variable" in node and isinstance(node.get("variable"), str)
        for k, v in node.items():
            if k == "for_each":
                continue
            nc, nd = recurse(v)
            c += nc
            dynamic |= nd
        return c, dynamic
    loops, variable = recurse(obj)
    return primary, root_types, loops, variable


def state_features(states):
    result = Counter()
    source_comparators = Counter()
    def walk(node):
        if isinstance(node, list):
            for item in node:
                walk(item)
            return
        if not isinstance(node, dict):
            return
        if len(node) == 1:
            name, sub = next(iter(node.items()))
            if name in LOGICAL_KEYS:
                result["logical_group_nodes"] += 1
                walk(sub)
                return
        for key, body in node.items():
            if key in LOGICAL_KEYS and isinstance(body, (list, dict)):
                result["logical_group_nodes"] += 1
                walk(body)
                continue
            if key == "record":
                result["record_nodes"] += 1
                walk(body)
                continue
            if key == "fields":
                result["record_field_maps"] += 1
                walk(body)
                continue
            if key in RESERVED or key in {"reported_elements", "states_match"}:
                continue
            if isinstance(body, dict):
                operation_keys = sorted(k for k in body if k not in RESERVED and k not in LOGICAL_KEYS and k != "fields")
                if "record" in body:
                    result["record_wrapped_fields"] += 1
                    walk(body)
                elif len(operation_keys) == 1 and not isinstance(body[operation_keys[0]], dict):
                    result["simple_field_predicates"] += 1
                    source_comparators[operation_keys[0]] += 1
                else:
                    result["complex_field_predicates"] += 1
                    walk(body)
            elif isinstance(body, list):
                walk(body)
    walk(states)
    return result, source_comparators


def evaluate_stats(node):
    if not isinstance(node, dict) or len(node) != 1:
        return Counter({"invalid_evaluate_nodes": 1})
    op, val = next(iter(node.items()))
    if op == "test":
        return Counter({"test_refs": 1})
    result = Counter({f"evaluate_{op}": 1})
    kids = [val] if op == "not" else val if isinstance(val, list) else []
    if not kids:
        result["invalid_evaluate_nodes"] += 1
    for c in kids:
        result.update(evaluate_stats(c))
    return result


def inspect(archive):
    digest = hashlib.sha256(Path(archive).read_bytes()).hexdigest()
    if digest != PINNED_SHA256:
        raise ValueError(f"r3 asset digest mismatch: {digest} expected {PINNED_SHA256}")
    counts, caps, object_shapes, by_capability = Counter(), Counter(), Counter(), defaultdict(Counter)
    status, operators, field_reqs, item_reqs = Counter(), Counter(), Counter(), Counter()
    examples, cases = defaultdict(list), []
    def add_sample(category, path, test_id):
        if len(examples[category]) < EXAMPLES_LIMIT:
            examples[category].append({"source": path, "test_id": test_id})
    with zipfile.ZipFile(archive) as z:
        if z.testzip():
            raise ValueError("Corrupted archive")
        paths = sorted(p for p in z.namelist() if p.startswith("authoring/")
                       and "/assessments/" in p and p.endswith(".yaml"))
        for path in paths:
            doc = yaml.safe_load(z.read(path))
            ass = (doc or {}).get("assessment") or {}
            tests = ass.get("tests") or {}
            if ass.get("mode") != "automated" or not isinstance(tests, dict) or not tests:
                continue
            counts["automated_documents"] += 1
            eval_stats = evaluate_stats(ass.get("evaluate"))
            for k, v in eval_stats.items():
                counts[k] += v
            if eval_stats["invalid_evaluate_nodes"]:
                add_sample("invalid_evaluate", path, "<evaluate>")
            for test_id, test in tests.items():
                counts["named_tests"] += 1
                cap = test.get("capability") or "<missing>"
                caps[cap] += 1
                obj, origin = source_object(ass, test)
                shape, rootkeys, loops, variable = collect_details(obj)
                object_shapes[shape] += 1
                by_capability[cap][shape] += 1
                status[origin] += 1
                if "collect" in rootkeys:
                    counts["collect_object_tests"] += 1
                    add_sample("collect_command", path, test_id)
                if "select" in rootkeys:
                    counts["select_object_tests"] += 1
                if "set" in rootkeys:
                    counts["set_object_tests"] += 1
                    add_sample("set_operator", path, test_id)
                if loops:
                    counts["for_each_target_tests"] += 1
                    add_sample("for_each", path, test_id)
                if variable:
                    counts["object_uses_variable"] += 1
                    add_sample("object_variable", path, test_id)
                if obj is None:
                    counts["unresolved_or_unusual_objects"] += 1
                    add_sample("unresolved_object", path, test_id)
                if not isinstance(test.get("test_title"), str) or not test.get("test_title"):
                    counts["missing_title"] += 1
                if "states" not in test:
                    counts["state_free_tests"] += 1
                    add_sample("state_free", path, test_id)
                else:
                    counts["state_bearing_tests"] += 1
                states = test.get("states") or []
                if isinstance(states, list) and len(states) > 1:
                    counts["multiple_state_alternatives"] += 1
                feat, op = state_features(states)
                operators.update(op)
                if feat["record_nodes"]:
                    counts["record_tests"] += 1
                    add_sample("record", path, test_id)
                if feat["logical_group_nodes"]:
                    counts["state_logic_tests"] += 1
                    add_sample("state_logic", path, test_id)
                if feat["complex_field_predicates"]:
                    counts["complex_state_fields_tests"] += 1
                if feat["simple_field_predicates"] and not feat["complex_field_predicates"] and not feat["record_nodes"]:
                    counts["simple_scalar_tests"] += 1
                item_reqs[test.get("collected_items_require", "<missing>")] += 1
                for name, val in feat.items():
                    counts[name] += val
                def find_field_reqs(n):
                    if isinstance(n, list):
                        for c in n: find_field_reqs(c)
                    elif isinstance(n, dict):
                        if "require" in n:
                            field_reqs[str(n["require"])] += 1
                        if "state_fields_require" in n:
                            field_reqs["scoped: "+str(n["state_fields_require"])] += 1
                        for k, v in n.items():
                            if k not in {"require", "state_fields_require"}: find_field_reqs(v)
                find_field_reqs(states)
                if "state_fields_require" in test:
                    field_reqs["scoped: "+str(test["state_fields_require"])] += 1
                cases.append({"source": path, "test_id": test_id, "capability": cap,
                              "collection": shape, "object_origin": origin,
                              "for_each": bool(loops), "dynamic_object": variable,
                              "records": bool(feat["record_nodes"]),
                              "state_logic": bool(feat["logical_group_nodes"]),
                              "state_alternatives": len(states) if isinstance(states, list) else -1,
                              "item_requirement": test.get("collected_items_require"),
                              "has_state": "states" in test})
    if counts["named_tests"] != sum(caps.values()) or counts["named_tests"] != sum(object_shapes.values()):
        raise AssertionError("Test population split not exhaustive")
    if counts["named_tests"] != 1375 or counts["automated_documents"] != 872:
        raise AssertionError(f"Pinned source cardinalities changed: {counts}")
    return {
        "status": "SOURCE-STRUCTURE-ONLY - no syntax or scan semantics approved",
        "asset_sha256": digest,
        "scope": "872 unique automated Assessment documents; 1375 named Test nodes",
        "counts": dict(counts),
        "object_shape": dict(object_shapes.most_common()),
        "object_origin": dict(status.most_common()),
        "capability": dict(caps.most_common()),
        "capability_collection_cross_tab": {k: dict(v.most_common()) for k, v in by_capability.items()},
        "item_requirements": dict(item_reqs.most_common()),
        "field_requirements": dict(field_reqs.most_common()),
        "comparators": dict(operators.most_common()),
        "sample_sources": dict(examples),
        "test_ledger": cases,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--archive", required=True)
    p.add_argument("--output")
    args = p.parse_args()
    report = inspect(args.archive)
    if args.output:
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "counts": report["counts"],
        "object_shape": report["object_shape"],
        "object_origin": report["object_origin"],
        "item_requirements_top": list(report["item_requirements"].items())[:15],
        "field_requirements_top": list(report["field_requirements"].items())[:12],
        "comparator_top": list(report["comparators"].items())[:20],
        "capability_top": list(report["capability"].items())[:20],
        "source_examples": {k: v[:2] for k, v in report["sample_sources"].items()},
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
