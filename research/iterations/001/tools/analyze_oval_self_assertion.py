#!/usr/bin/env python3
"""Run the OVAL Community Self-Assertion corpus through the SCAP-NG semantic importer.

This is a language-conformance inventory, not an OVAL results evaluator and not
production STIG migration evidence. It verifies that standalone OVAL documents
can be parsed without dependency loss and inventories semantics that still need
exact evaluator/native-lowering support.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import Counter, defaultdict
from pathlib import Path


HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("oval_semantic_ir", HERE / "oval_semantic_ir.py")
oval_ir = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)


def iter_xml(root: Path):
    yield from sorted(p for p in root.rglob("*.xml") if p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("root", type=Path, help="OVAL_Test_Content directory or one platform subdirectory")
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--fail-on-unresolved", action="store_true")
    args = ap.parse_args()

    files = []
    parse_failures = []
    unresolved_files = []
    resolution_status = Counter()
    plan_modes = Counter()
    functions = Counter()
    elements = Counter()
    operations = Counter()
    checks = Counter()
    existence = Counter()
    namespaces = Counter()
    by_directory = defaultdict(lambda: {"files": 0, "parse_failures": 0, "unresolved": 0})

    xml_files = list(iter_xml(args.root))
    for path in xml_files:
        rel = path.relative_to(args.root).as_posix()
        directory = rel.split("/", 1)[0] if "/" in rel else "."
        by_directory[directory]["files"] += 1

        try:
            ir = oval_ir.parse(path)
        except Exception as exc:
            parse_failures.append({"path": rel, "error": f"{type(exc).__name__}: {exc}"})
            by_directory[directory]["parse_failures"] += 1
            continue

        unresolved = ir.get("unresolved_references", [])
        if unresolved:
            unresolved_files.append({"path": rel, "references": unresolved})
            by_directory[directory]["unresolved"] += 1

        for status in ir.get("variable_resolution", {}).values():
            resolution_status[status.get("status", "unknown")] += 1
        for plan in ir.get("variable_evaluation_plans", {}).values():
            plan_modes[plan.get("mode", "unknown")] += 1
            expr = plan.get("expression")
            if isinstance(expr, dict):
                stack = [expr]
                while stack:
                    node = stack.pop()
                    op = node.get("op")
                    if op:
                        functions[op] += 1
                    stack.extend(x for x in node.get("args", []) if isinstance(x, dict))

        features = ir.get("features", {})
        elements.update(features.get("elements", {}))
        namespaces.update(features.get("namespaces", {}))
        attrs = features.get("attributes", {})
        operations.update(attrs.get("operation", {}))
        checks.update(attrs.get("check", {}))
        existence.update(attrs.get("check_existence", {}))

        files.append({
            "path": rel,
            "sha256": ir["source"]["sha256"],
            "definitions": len(ir.get("definitions", [])),
            "tests": len(ir.get("tests", [])),
            "objects": len(ir.get("objects", [])),
            "states": len(ir.get("states", [])),
            "variables": len(ir.get("variables", [])),
            "unresolved_reference_count": len(unresolved),
            "variable_resolution_status": dict(sorted(Counter(
                x.get("status", "unknown")
                for x in ir.get("variable_resolution", {}).values()
            ).items())),
        })

    report = {
        "format": "scap-ng-oval-self-assertion-conformance-inventory-0.1",
        "scope": args.root.as_posix(),
        "role": "language_conformance_not_migration_evidence",
        "xml_files_discovered": len(xml_files),
        "xml_files_parsed": len(files),
        "parse_failure_count": len(parse_failures),
        "unresolved_reference_file_count": len(unresolved_files),
        "parse_failures": parse_failures,
        "unresolved_reference_files": unresolved_files,
        "variable_resolution_status": dict(sorted(resolution_status.items())),
        "variable_evaluation_plan_modes": dict(sorted(plan_modes.items())),
        "variable_expression_operations": dict(sorted(functions.items())),
        "oval_elements": dict(sorted(elements.items())),
        "entity_operations": dict(sorted(operations.items())),
        "test_checks": dict(sorted(checks.items())),
        "check_existence": dict(sorted(existence.items())),
        "namespaces": dict(sorted(namespaces.items())),
        "by_directory": dict(sorted(by_directory.items())),
        "files": files,
        "gate": {
            "parse_complete": not parse_failures,
            "dependency_complete": not unresolved_files,
            "semantic_equivalence_claimed": False,
            "note": (
                "Parsing/dependency closure is only the first gate. Exact OVAL evaluator "
                "semantics require feature-specific conformance and differential tests."
            ),
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(json.dumps({
        "files": len(xml_files),
        "parsed": len(files),
        "parse_failures": len(parse_failures),
        "unresolved_reference_files": len(unresolved_files),
        "variable_resolution_status": report["variable_resolution_status"],
        "plan_modes": report["variable_evaluation_plan_modes"],
    }, indent=2, sort_keys=True))

    if parse_failures:
        return 1
    if args.fail_on_unresolved and unresolved_files:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
