# Canonical Variable function replay

The original Assessment asserted that each observed value must equal
every expected operand. That condition fails for distinct operands under
[Model A](../../docs/contracts/0.4-evaluation.md). At the recorded
baseline, RI returned false for nine Tests whose independent manifest
requires true. The separate alias interaction returned false for both
Tests, including the leaf expected to pass. Its intended cardinality
failure had zero matching values before the correction.

Each multivalue Test now requires every observed value to match exactly
one expected value. A companion Test checks an exact document-order
sequence using `merge` and a delimiter outside the expected values.
Together the two checks detect unexpected values, reordering, duplicates
and missing values. The original independent expected values are unchanged.

The current [RI receipt](ri-receipt.json) records 24 true direct Test
evaluations and 20 paired projection controls. A reordered, duplicate or
short projection can pass membership and fails the sequence check. Empty,
absent, incomplete and error sources retain diagnostics without a
technical outcome. Collection inputs are supplied through the public RI
evaluator API. The corrected alias interaction reports one true and one false leaf,
with both values matching before the intended existence requirement
rejects the latter. Whole-Assessment rollup and host acquisition remain open.

```sh
python conformance/tools/replay_variable_functions.py --check \
  --ri /path/to/pinned/scap-ng-ri
```

The [Studio receipt](studio-receipt.json) checks the same revised
Assessment bytes with the exact-pin pack through model open/save,
scalar edit, reopen and undo.
