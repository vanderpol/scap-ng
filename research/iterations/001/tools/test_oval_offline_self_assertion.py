#!/usr/bin/env python3
"""Run focused OVAL Self-Assertion cases through the offline variable_test evaluator."""
from pathlib import Path
import argparse
import importlib.util

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("offline_eval", HERE / "oval_offline_variable_test.py")
offline = importlib.util.module_from_spec(spec)
spec.loader.exec_module(offline)

CASES = [
    "ind-def_variable_test.xml",
    "oval_check_enumeration_entity.xml",
    "oval_check_enumeration_object_state.xml",
    "oval_check_enumeration_variable_values.xml",
    "oval_existence_enumeration.xml",
    "oval-def_arithmetic_function.xml",
    "oval-def_begin_function.xml",
    "oval-def_concat_function.xml",
    "oval-def_end_function.xml",
    "oval-def_escape_regex_function.xml",
    "oval-def_globtoregex_test.xml",
    "oval-def_literal_component.xml",
    "oval-def_local_variable.xml",
    "oval-def_merge.xml",
    "oval-def_object_component.xml",
    "oval-def_regex_capture_function.xml",
    "oval-def_split_function.xml",
    "oval-def_substring_function.xml",
    "oval-def_variable_component.xml",
]

ap = argparse.ArgumentParser()
ap.add_argument("agnostic_root", type=Path)
args = ap.parse_args()

failures = []
total_defs = 0
for name in CASES:
    result = offline.evaluate_file(args.agnostic_root / name)
    total_defs += len(result)
    bad = {k: v for k, v in result.items() if v != "true"}
    if bad:
        failures.append((name, bad))
    else:
        print(f"PASS: {name}: {len(result)} definition(s) true")

if failures:
    for name, bad in failures:
        print(f"FAIL: {name}: {bad}")
    raise SystemExit(1)

print(f"PASS: {len(CASES)} focused Self-Assertion files, {total_defs} definitions true offline")
