#!/usr/bin/env python3
"""Validate iteration 001 prototype YAML and result conventions."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

MIGRATION_ROOT = Path("research/iterations/001/prototypes/oval-migration-cases")
FULL_ROOT = Path("research/iterations/001/prototypes/full-benchmarks")

VALID_OUTCOMES = {
    "pass", "fail", "not_applicable", "not_evaluated", "indeterminate", "error"
}


def load_yaml_files(root: Path, errors: list[str]) -> dict[Path, object]:
    parsed = {}
    for path in sorted(root.rglob("*.yaml")):
        try:
            parsed[path] = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path}: YAML parse failure: {exc}")
    return parsed


def validate_result(path: Path, doc: dict, errors: list[str]) -> None:
    if "root_cause" in doc or "root_causes" in doc:
        errors.append(f"{path}: obsolete root_cause/root_causes field; use explanation")

    if "outcome" in doc:
        outcome = doc.get("outcome")
        if outcome not in VALID_OUTCOMES:
            errors.append(f"{path}: invalid result outcome {outcome!r}")
        if outcome == "fail" and doc.get("method") != "manual" and "explanation" not in doc:
            errors.append(f"{path}: automated Fail result lacks structured explanation")
        if outcome == "error" and "reason" not in doc:
            errors.append(f"{path}: Error result lacks structured reason")

    for rr in doc.get("rule_results", []) if isinstance(doc, dict) else []:
        outcome = rr.get("outcome")
        if outcome not in VALID_OUTCOMES:
            errors.append(f"{path}: rule {rr.get('rule')} has invalid outcome {outcome!r}")
        if "root_cause" in rr or "root_causes" in rr:
            errors.append(
                f"{path}: rule {rr.get('rule')} uses obsolete root_cause/root_causes"
            )
        if outcome == "fail" and rr.get("method") != "manual" and "explanation" not in rr:
            errors.append(
                f"{path}: automated Fail rule {rr.get('rule')} lacks explanation"
            )
        if outcome == "error" and "reason" not in rr:
            errors.append(f"{path}: Error rule {rr.get('rule')} lacks reason")


def main() -> int:
    errors: list[str] = []

    migration = load_yaml_files(MIGRATION_ROOT, errors)
    full = load_yaml_files(FULL_ROOT, errors)

    if not migration:
        errors.append(f"no YAML files found under {MIGRATION_ROOT}")
    if not full:
        errors.append(f"no YAML files found under {FULL_ROOT}")

    for path, doc in migration.items():
        rel = path.relative_to(MIGRATION_ROOT)
        if doc is None:
            errors.append(f"{rel}: empty YAML document")
            continue
        if "results" in rel.parts:
            validate_result(path, doc, errors)
        if rel.name == "assessment.yaml" and "assessment" not in doc:
            errors.append(f"{rel}: expected top-level assessment")
        if rel.name == "rule.yaml" and "rule" not in doc:
            errors.append(f"{rel}: expected top-level rule")

    case_dirs = [
        p for p in MIGRATION_ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ]
    for case in case_dirs:
        if not (case / "source.yaml").exists():
            errors.append(f"{case.relative_to(MIGRATION_ROOT)}: missing source.yaml")
        if not (case / "results").exists():
            errors.append(f"{case.relative_to(MIGRATION_ROOT)}: missing results directory")

    for path, doc in full.items():
        if doc is None:
            errors.append(f"{path}: empty YAML document")
            continue
        if "/results/" in path.as_posix():
            validate_result(path, doc, errors)

    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors), file=sys.stderr)
        return 1

    print(
        f"OK: parsed {len(migration)} migration-case YAML files across "
        f"{len(case_dirs)} cases and {len(full)} full-benchmark YAML files"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
