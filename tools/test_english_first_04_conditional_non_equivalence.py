#!/usr/bin/env python3
"""Auditor-first non-equivalence guard: preserve OVAL OR/AND decision semantics.

One intuitive if/else rewrite differs in 81 of 216 possible six-valued
guard/payload combinations. The language must preserve the original AST
unless a separately proved lowering contract is used. Research #229/#235.
"""
from measure_oval_conditional_patterns import conditional_truth_comparison

def main():
    matrix=conditional_truth_comparison()
    assert matrix["cases"]==216, matrix
    assert matrix["equal_cases"]==135, matrix
    assert matrix["mismatch_cases"]==81, matrix
    assert matrix["universally_equivalent"] is False
    assert matrix["sample_mismatches"], matrix
    print("PASS: 216 six-state conditional scenarios; 81 non-equivalent. "
          "Do not replace OVAL Boolean paths with procedural if/else.")

if __name__=="__main__":
    main()
