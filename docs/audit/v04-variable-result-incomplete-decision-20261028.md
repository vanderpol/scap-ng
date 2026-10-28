# Variable-result incomplete status: bounded 0.4 decision (2026-10-28)

**Issue:** [#255](https://github.com/vanderpol/scap-ng/issues/255). **Owner decision:** approved in the SCAP-NG project conversation, 2026-10-28. **Scope:** schema representation only; scanner, interpreter, converter and specification promotion not authorized by this decision.

## Source-backed problem and objective

The existing 0.4 [collection-result](../../schema/v0.4.0/collection-result.schema.json) explicitly allows `status: incomplete`; [variable-result](../../schema/v0.4.0/variable-result.schema.json) previously did not. A Variable derived from an incompletely acquired Object may nevertheless contain known observed typed values. Encoding such a Variable as `complete` would assert unproved population completeness; `zero_values` would falsely assert a complete empty stream; `unknown` or `error` alone cannot preserve the distinction between a partial known stream and an entirely unavailable result.

OVAL's original collection and results contracts distinguish incomplete acquisition and known observed Items. See [OVAL System Characteristics](https://oval-community-guidelines.readthedocs.io/en/latest/oval-schema-documentation/oval-system-characteristics-schema.html) and [OVAL Results](https://oval-community-guidelines.readthedocs.io/en/base/oval-schema-documentation/oval-results-schema.html). This schema change does **not** independently establish OVAL-to-NG evaluation equivalence.

## Approved representation

Add `incomplete` to Variable-result `status` enumeration, keeping existing required `id`, `datatype`, `status`, `cardinality`, `values`, and `item_refs`. Keep typed values and optional `provenance`/`diagnostics` unchanged. `cardinality: zero|one|many` with `incomplete` describes **observed** values, not a proved full population. Duplicate observed values and the empty string remain distinct observations.

Examples of structurally admissible combinations:

| Status | Observed typed values | Cardinality | Meaning |
| --- | --- | --- | --- |
| `incomplete` | `[]` | `zero` | No value observed, total population not proved empty |
| `incomplete` | one typed `""` | `one` | One known empty-string value; others may be absent |
| `incomplete` | two typed `"a"` values | `many` | Two observed occurrences; total population not proved complete |

The regression suite verifies those three shapes, retained earlier statuses, invalid status and malformed typed values, and required-field preservation. These are representation tests, **not** runtime function evaluations.

## Alternatives and compatibility

- **Leave status absent:** cannot label incomplete population distinctly; rejected.
- **Coerce to `unknown`/`error`:** loses known-partial/diagnostic distinction; rejected as a general representation rule.
- **Reuse `zero_values` or `complete`:** can manufacture a definitive empty or complete result; rejected.
- **Define function-specific propagation truth tables now:** deferred pending independent OVAL source-backed tests and explicit review, including `count`, `unique`, `merge`, split, aggregation and non-Boolean/error precedence; not implicit in approval.

This is an additive status enum option for 0.4 result consumers; existing documents remain valid. Consumers that currently assume a closed status switch must recognize or reject `incomplete` explicitly, not silently map it to success. No production collector, converter or evaluator emission was altered. Full runtime conformance remains unproved.

**Verification:** `PYTHONPATH=/tmp/scap-ng-schema-deps-20261028:tools python -m unittest test_v04_variable_result_incomplete test_v04_typed_operator_datatype_consistency test_v04_variable_function_expression_contract`; 18 tests passed locally on the proposed schema tree. Hosted CI at the published commit must be checked separately.
