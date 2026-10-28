# Canonical Variable-function migration: staged checkpoint

Status: **approved design direction, partial implementation; no production grammar switch**.
Owner approval in the SCAP-NG project discussion on 2026-10-28 is recorded
in [#255](https://github.com/vanderpol/scap-ng/issues/255). Converter work remains
tracked by [#251](https://github.com/vanderpol/scap-ng/issues/251).

## Implemented without changing current output

- `schema/v0.4.0/variable-function-expression.schema.json` validates the single
  canonical `function: {name, arguments, options}` envelope, including the 13
  original function names, recursive arguments, arity and typed option subsets.
  It is intentionally **not yet referenced** by `assessment.schema.json`.
- `tools/v04_variable_function_migration.py` is a pure, fail-closed, reversible
  migration of the four emitted legacy forms: `concat`, `regex_capture`, `merge`
  and `unique`. It preserves typed and existing shorthand literal leaves.
- `AssessmentConverter(..., canonical_variable_functions=True)` is an opt-in
  migration probe. The default remains the existing source-proved grammar.
- `ExpandedNative.function` independently decodes those four canonical calls;
  it does not import or trust the converter's migration helper.

## Evidence and limits

Focused contract, source-backed Variable and expanded source-proof suites total
**35 passing tests** at this checkpoint. Existing fixture migrations retain
their original expression trees after inverse translation. The opt-in
source-backed tests compare the independent source terms and compiled Test and
result instructions. Changing the Variable authoring grammar necessarily changes
the Assessment source hash; it must not be described as a byte-identical bundle.

These tests do **not** establish execution of function calls, scanner results,
general six-state parity, or all 13 function implementations. The nine remaining
original functions stay unsupported by the converter. Float/IEEE-32 (#218),
Variable-result incomplete status, dynamic acquisition fan-out, and generic
Test-level `all_exist` remain separate decisions.

## Safe integration boundary

1. Preserve frozen historical source/proof packets and current default output.
2. Add independent proofs for the remaining OVAL functions and exact status,
   collection, cast and aggregation semantics before enabling their emission.
3. Coordinate an explicit versioned upgrader and a single canonical grammar;
   do not accept both function payload families permanently.
4. Switch production authoring validation, converter and compiler together,
   comparing exact original source terms and maintaining failure identities.
5. Run maintained regression and hosted gates against the pinned integration
   SHA before claiming an accepted 0.4 grammar baseline.
