#!/usr/bin/env python3
"""Research #235: audit English-first named sources, variables, and cycles.

Read-only classification, NOT source/scanner semantic proof. Missing and cyclic
references are surfaced as findings; no automatic replacement is permitted.
"""
import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import zipfile

SET_OPS = frozenset({"union", "difference", "intersection", "complement"})
PINNED = "03d64157ee295b81defe6f96cf7a3123410010ef4422d76bf5b7bb3ddbf30c9d"


def analyze_references(document):
    """Audit complete compact experimental Assessment, not descriptive names."""
    sources = document.get("sources", {})
    variables = document.get("metadata", {}).get("variables", {})
    checks = document.get("checks", {})
    if not all(isinstance(v, dict) for v in (sources, variables, checks)):
        raise ValueError("sources, variables and checks must be mappings")
    names = {"source": set(sources), "variable": set(variables)}
    dependencies = {f"{kind}:{name}": set()
                    for kind, ids in names.items() for name in ids}
    dependencies.update({"check:" + name: set() for name in checks})
    missing, malformed = [], []
    counts = Counter()

    def report_ref(kind, name, owner, path):
        counts[kind + "_references"] += 1
        if not isinstance(name, str) or not name:
            malformed.append(f"{path}: {kind} ID is not a nonempty string")
            return
        if name not in names[kind]:
            missing.append(f"{path}: {kind}:{name}")
            return
        if owner in dependencies:
            dependencies[owner].add(f"{kind}:{name}")

    def embedded_values(node, owner, path, include_objects=False):
        """Only variable: is universally a reference; object: within expressions."""
        if isinstance(node, list):
            for i, value in enumerate(node):
                embedded_values(value, owner, f"{path}[{i}]", include_objects)
        elif isinstance(node, dict):
            for key, value in node.items():
                here = f"{path}.{key}"
                if key == "variable" and isinstance(value, str):
                    report_ref("variable", value, owner, here)
                elif key == "object" and include_objects and isinstance(value, str):
                    report_ref("source", value, owner, here)
                else:
                    embedded_values(value, owner, here, include_objects)

    def inspect_source(node, owner, path):
        if not isinstance(node, dict):
            malformed.append(f"{path}: source must be a mapping")
            return
        if set(node) == {"source"}:
            report_ref("source", node["source"], owner, path + ".source")
            return
        if "for_each_source" in node:
            each = node["for_each_source"]
            if not isinstance(each, dict) or "in" not in each:
                malformed.append(f"{path}.for_each_source: missing in")
            else:
                report_ref("source", each["in"], owner, path + ".for_each_source.in")
        if "collect" in node:
            embedded_values(node["collect"], owner, path + ".collect")
        if "where" in node:
            # user.home_dir is an Item field binding, not a named collection.
            embedded_values(node["where"], owner, path + ".where")
        for op in SET_OPS & set(node):
            operands = node[op]
            if not isinstance(operands, list) or not operands:
                malformed.append(f"{path}.{op}: operands must be a nonempty list")
                continue
            for i, operand in enumerate(operands):
                target = f"{path}.{op}[{i}]"
                if not isinstance(operand, dict) or "from" not in operand:
                    malformed.append(target + ": missing from")
                    continue
                ref = operand["from"]
                if isinstance(ref, str):
                    report_ref("source", ref, owner, target + ".from")
                elif isinstance(ref, dict):
                    inspect_source(ref, owner, target + ".from")
                else:
                    malformed.append(target + ".from: unsupported operand reference")
                for key in ("include_if", "exclude_if", "ordered_filters"):
                    if key in operand:
                        embedded_values(operand[key], owner, target + "." + key)

    for name, node in sources.items():
        inspect_source(node, "source:" + name, "sources." + name)
    for name, value in variables.items():
        if not isinstance(value, dict):
            malformed.append(f"variables.{name}: variable must be a mapping")
            continue
        embedded_values(value.get("expression", {}), "variable:" + name,
                        "variables." + name + ".expression", include_objects=True)
    for name, check in checks.items():
        if not isinstance(check, dict):
            malformed.append(f"checks.{name}: check must be a mapping")
            continue
        owner = "check:" + name
        if "from" in check:
            report_ref("source", check["from"], owner, f"checks.{name}.from")
        if "gather" in check:
            inspect_source(check["gather"], owner, f"checks.{name}.gather")
        for field in ("collect", "where", "input_from"):
            if field in check:
                embedded_values(check[field], owner, f"checks.{name}.{field}")

    cycles = set()
    state, stack = {}, []
    def walk(node):
        state[node] = 1
        stack.append(node)
        for neighbor in sorted(dependencies[node]):
            if state.get(neighbor) == 1:
                cycle = stack[stack.index(neighbor):] + [neighbor]
                cycles.add(" -> ".join(cycle))
            elif state.get(neighbor, 0) == 0:
                walk(neighbor)
        stack.pop()
        state[node] = 2
    for node in sorted(dependencies):
        if state.get(node, 0) == 0:
            walk(node)

    # Longest prerequisite chain exposes authoring/dependency complexity.
    # A cycle is a separate diagnostic; never assign it a fictional depth.
    memo = {}
    def longest_path(node):
        if node in memo:
            return memo[node]
        tail = max((longest_path(other) for other in sorted(dependencies[node])),
                   key=len, default=[])
        memo[node] = [node] + tail
        return memo[node]
    longest = (max((longest_path(node) for node in sorted(dependencies)),
                   key=len, default=[])) if not cycles else []

    return {"counts": {**dict(counts), "named_sources": len(sources),
                       "named_variables": len(variables),
                       "dependency_edges": sum(map(len, dependencies.values()))},
            "missing": sorted(set(missing)), "malformed": sorted(set(malformed)),
            "cycles": sorted(cycles),
            "max_dependency_depth": max(0, len(longest) - 1),
            "longest_chain": longest}


def self_test():
    doc = {"metadata": {"variables": {
             "command": {"expression": {"concat": [
                 {"literal": "shell "},
                 {"values": {"object": "users", "field": "username"}}]}}}},
           "sources": {
             "users": {"inspect": "unix.password",
                       "where": {"username": {"matches_regex": ".*"}}},
             "filtered": {"inspect": "unix.password", "difference": [
                 {"from": "users", "exclude_if": [{"user_id": {"less_than": 1000}}]}]},
             "files": {"inspect": "unix.file", "union": [
                 {"from": {"inspect": "unix.file", "for_each_source":
                           {"item": "user", "in": "filtered"},
                           "where": {"directory": {"from": "user.home_dir"}}},
                  "exclude_if": [{"type": {"is": "directory"}}]}]},
             "shell": {"inspect": "independent.shellcommand",
                       "collect": {"command": {"variable": "command"}}}},
           "checks": {"one": {"inspect": "unix.file", "from": "files"},
                      "two": {"inspect": "independent.shellcommand", "from": "shell"}}}
    healthy = analyze_references(doc)
    if any(healthy[field] for field in ("missing", "malformed", "cycles")):
        raise AssertionError("healthy graph failed: " + repr(healthy))
    if healthy["counts"].get("source_references") != 5:
        raise AssertionError("missing iteration, Set, or expression source references")
    broken = deepcopy(doc)
    broken["sources"]["files"]["union"][0]["from"]["for_each_source"]["in"] = "lost"
    if not any("source:lost" in m for m in analyze_references(broken)["missing"]):
        raise AssertionError("missing foreach reference undetected")
    cyclic = deepcopy(doc)
    cyclic["sources"]["users"]["for_each_source"] = {"item": "user", "in": "files"}
    if not analyze_references(cyclic)["cycles"]:
        raise AssertionError("collection cycle undetected")
    cyclic = deepcopy(doc)
    cyclic["metadata"]["variables"]["command"]["expression"] = {"variable": "command"}
    if not analyze_references(cyclic)["cycles"]:
        raise AssertionError("variable cycle undetected")
    cyclic = deepcopy(doc)
    cyclic["sources"]["users"]["collect"] = {"command": {"variable": "command"}}
    if not analyze_references(cyclic)["cycles"]:
        raise AssertionError("mixed dependency cycle undetected")
    native = deepcopy(doc)
    native["checks"]["three"] = {"inspect": "windows.passwordpolicy"}
    if any(analyze_references(native)[field] for field in ("missing", "malformed", "cycles")):
        raise AssertionError("built-in Objectless check wrongly rejected")
    return True


def audit_corpus(archive):
    """Evaluate only the supported research ASTs; classify every unsupported file."""
    import yaml
    from research_english_first_04_complex import to_human
    from research_english_first_04_compact_layout import compact, expand

    if hashlib.sha256(Path(archive).read_bytes()).hexdigest() != PINNED:
        raise ValueError("archive SHA-256 changed; refusing unpinned content")
    counts = Counter()
    findings = []
    failures = []
    deep_examples = []
    with zipfile.ZipFile(archive) as zipped:
        if zipped.testzip():
            raise ValueError("source archive CRC mismatch")
        for path in sorted(zipped.namelist()):
            if not (path.startswith("authoring/") and "/assessments/" in path
                    and path.endswith(".yaml")):
                continue
            assessment = (yaml.safe_load(zipped.read(path)) or {}).get("assessment") or {}
            if assessment.get("mode") != "automated" or not assessment.get("tests"):
                continue
            counts["automated_assessments"] += 1
            try:
                human = to_human(assessment)
                compacted = compact(human)
                if expand(compacted) != human:
                    raise AssertionError("inversion changed source")
            except (ValueError, TypeError, KeyError, AttributeError, AssertionError) as err:
                counts["unsupported_assessments"] += 1
                if len(failures) < 30:
                    failures.append({"path": path, "reason": str(err)[:240]})
                continue
            counts["audited_assessments"] += 1
            report = analyze_references(compacted)
            deep_examples.append({"path": path,
                                  "depth": report["max_dependency_depth"],
                                  "longest_chain": report["longest_chain"]})
            for key, value in report["counts"].items():
                counts[key] += value
            if any(report[key] for key in ("missing", "malformed", "cycles")):
                counts["assessments_with_reference_findings"] += 1
                if len(findings) < 60:
                    findings.append({"path": path, **report})
    if counts["automated_assessments"] != 872:
        raise AssertionError("pinned six-STIG denominator unexpected")
    if counts["audited_assessments"] < 865:
        raise AssertionError("compact grammar regression")
    return {"status": "REFERENCE CLASSIFICATION ONLY, NOT SCANNER CONFORMANCE",
            "counts": dict(counts), "findings": findings,
            "deepest_dependency_examples": sorted(deep_examples,
                key=lambda row: (-row["depth"], row["path"]))[:12],
            "unsupported_examples": failures, "source_sha256": PINNED}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive")
    parser.add_argument("--output")
    args = parser.parse_args()
    self_test()
    if args.archive:
        result = audit_corpus(args.archive)
        if args.output:
            Path(args.output).write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS: missing, cyclic, mixed, nested and Objectless reference guards")


if __name__ == "__main__":
    main()
