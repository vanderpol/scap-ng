#!/usr/bin/env python3
"""Conformance checks for first-class SCAP-NG existence semantics."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CASES = (
    ROOT
    / "research"
    / "iterations"
    / "002"
    / "examples"
    / "conformance"
    / "existence-state-cases.yaml"
)

spec = importlib.util.spec_from_file_location("converter", HERE / "scap14_to_scapng.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def evaluate(expected: str, observed_count: int) -> tuple[str, str]:
    if expected == "none":
        return (
            ("pass", "expected_absence")
            if observed_count == 0
            else ("fail", "unexpected_existence")
        )
    if expected == "one_or_more":
        return (
            ("pass", "expected_existence")
            if observed_count >= 1
            else ("fail", "required_item_missing")
        )
    raise ValueError(f"unsupported expected existence value: {expected}")


doc = yaml.safe_load(CASES.read_text(encoding="utf-8"))
for case in doc["cases"]:
    actual = evaluate(case["expected_existence"], case["observed_count"])
    expected = (case["expected_outcome"], case["expected_reason"])
    assert actual == expected, (case["id"], actual, expected)

# SCAP 1.4 migration must carry OVAL test-level existence semantics without
# substituting a default or collapsing distinct source values.
for value in (
    "all_exist",
    "any_exist",
    "at_least_one_exists",
    "none_exist",
    "only_one_exists",
):
    node = mod.test_node(
        {
            "id": f"test-{value}",
            "type": "example_test",
            "namespace": "example",
            "check": "all",
            "check_existence": value,
            "state_operator": "AND",
            "objects": [],
            "states": [],
            "other": [],
        }
    )
    assert node["check_existence"] == value, node

print("PASS: NG existence truth table and OVAL check_existence preservation")
