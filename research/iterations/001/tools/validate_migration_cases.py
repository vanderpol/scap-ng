#!/usr/bin/env python3
"""Validate iteration 001 OVAL migration case YAML and basic case structure."""
from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path("research/iterations/001/prototypes/oval-migration-cases")


def main() -> int:
    errors: list[str] = []
    yaml_files = sorted(ROOT.rglob("*.yaml"))

    if not yaml_files:
        errors.append(f"no YAML files found under {ROOT}")

    parsed = {}
    for path in yaml_files:
        try:
            parsed[path] = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"{path}: YAML parse failure: {exc}")

    for path, doc in parsed.items():
        rel = path.relative_to(ROOT)
        if doc is None:
            errors.append(f"{rel}: empty YAML document")
            continue

        if "results" in rel.parts:
            outcome = doc.get("outcome")
            if outcome not in {
                "pass", "fail", "not_applicable", "not_evaluated",
                "indeterminate", "error"
            }:
                errors.append(f"{rel}: invalid/missing result outcome {outcome!r}")

            if outcome == "fail" and "explanation" not in doc:
                errors.append(f"{rel}: Fail result lacks structured explanation")

            if outcome == "error" and "reason" not in doc:
                errors.append(f"{rel}: Error result lacks structured reason")

        if rel.name == "assessment.yaml":
            if "assessment" not in doc:
                errors.append(f"{rel}: expected top-level assessment")

        if rel.name == "rule.yaml":
            if "rule" not in doc:
                errors.append(f"{rel}: expected top-level rule")

    case_dirs = [
        p for p in ROOT.iterdir()
        if p.is_dir() and not p.name.startswith(".")
    ]
    for case in case_dirs:
        if not (case / "source.yaml").exists():
            # Families may have source.yaml but every current case should.
            errors.append(f"{case.relative_to(ROOT)}: missing source.yaml")
        if not (case / "results").exists():
            errors.append(f"{case.relative_to(ROOT)}: missing results directory")

    if errors:
        print("\n".join(f"ERROR: {e}" for e in errors), file=sys.stderr)
        return 1

    print(f"OK: parsed {len(yaml_files)} YAML files across {len(case_dirs)} migration cases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
