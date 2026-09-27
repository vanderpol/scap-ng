#!/usr/bin/env python3
"""Regression tests for OVAL 5.12.3 six-state result algebra."""
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("oval_ir",HERE/"oval_semantic_ir.py")
oval_ir=importlib.util.module_from_spec(spec)
spec.loader.exec_module(oval_ir)

# Negation only flips Boolean results.
assert oval_ir.oval_negate_result("true")=="false"
assert oval_ir.oval_negate_result("false")=="true"
for value in ("error","unknown","not_evaluated","not_applicable"):
    assert oval_ir.oval_negate_result(value)==value

# AND precedence: false > error > unknown > not evaluated > true > NA.
assert oval_ir.oval_combine_results("AND",["true","not_applicable"])=="true"
assert oval_ir.oval_combine_results("AND",["unknown","true"])=="unknown"
assert oval_ir.oval_combine_results("AND",["error","unknown"])=="error"
assert oval_ir.oval_combine_results("AND",["false","error"])=="false"
assert oval_ir.oval_combine_results("AND",["not_applicable"])=="not_applicable"

# OR precedence: true > error > unknown > not evaluated > false > NA.
assert oval_ir.oval_combine_results("OR",["false","not_applicable"])=="false"
assert oval_ir.oval_combine_results("OR",["unknown","false"])=="unknown"
assert oval_ir.oval_combine_results("OR",["error","unknown"])=="error"
assert oval_ir.oval_combine_results("OR",["true","error"])=="true"
assert oval_ir.oval_combine_results("OR",["not_applicable"])=="not_applicable"

# ONE and XOR edge cases from the schema tables.
assert oval_ir.oval_combine_results("ONE",["true","false"])=="true"
assert oval_ir.oval_combine_results("ONE",["true","true","error"])=="false"
assert oval_ir.oval_combine_results("ONE",["false","unknown"])=="false"
assert oval_ir.oval_combine_results("ONE",["unknown","not_applicable"])=="unknown"
assert oval_ir.oval_combine_results("XOR",["true","false","true"])=="false"
assert oval_ir.oval_combine_results("XOR",["true","false","false"])=="true"
assert oval_ir.oval_combine_results("XOR",["true","unknown"])=="unknown"
assert oval_ir.oval_combine_results("XOR",["not_applicable"])=="not_applicable"

print("PASS: OVAL six-state AND/OR/ONE/XOR and negation semantics preserved")
