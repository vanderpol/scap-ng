# Typed comparison / datatype consistency — 0.4 bounded schema correction

Date: 2026-10-28. Owner schema workstream: [#255](https://github.com/vanderpol/scap-ng/issues/255).
Converter coordination: [#251](https://github.com/vanderpol/scap-ng/issues/251).

## Observed defect

Before this correction, both the production `assessment.schema.json` and
`assessment-language.schema.json` accepted a State field containing:

```yaml
version_equals: '1.0'
datatype: string
values_found: one_or_more
values_matching: every
```

The comparison key specifies the `version` domain, but the datatype incorrectly
identifies the operand as `string`. The converter's independent typed-semantic
proof rejected this mismatch. The pre-existing
`capability-common.schema.json#/$defs/authoring_type_resolution` described a
related guard but was no longer referenced in 0.4; the 0.3 rule must not be
copied wholesale into 0.4.

## Narrow correction

The active 0.4 `assessment-language.schema.json` now shares a
`typed_comparison_datatype_consistency` guard across scalar State fields,
record-member fields and Object selectors. For each self-describing comparison
operator family (float, binary, version, IPv4, IPv6, RPM EVR, Debian EVR,
fileset revision and IOS version), a **present** explicit `datatype` must equal
that operator's native domain. A missing datatype is not rejected by this
guard. Generic scalar comparisons retain their existing type-resolution rules.

This preserves the direct converter's currently source-proved non-string
encoding: `version_equals: '1.0'` with `datatype: version` remains valid, because
the renderer explicitly includes a datatype for non-string sources and typed
arrays/Variable references. It also preserves valid explicit datatype on
ordinary string comparisons. The correction is validation-only; it does not
modify collector execution, comparison order, compiler lowering, six-state
evaluation, result status or provenance.

## Rejected alternatives and integration boundaries

- **Reject** the 0.3 `authoring_type_resolution` rule wholesale: its blanket
  typed-operator-plus-datatype prohibition would invalidate current converter
  output with correctly matching non-string datatypes.
- **Reject** interpreting `datatype: string` as an override of
  `version_equals`: that silently changes assessment meaning.
- **Reject** making every comparison field's datatype mandatory: scalar typed
  literal authoring intentionally supports unambiguous omission.
- **Do not** treat this schema guard as a scanner/runtime datatype proof.
  Capability-specific legal field types, source casts, IEEE-32/nonfinite values
  and runtime failure propagation remain independent contracts.

## Verification

New test: `tools/test_v04_typed_operator_datatype_consistency.py` checks
matching, conflicting and absent explicit datatypes for representative typed
operations, every 54 self-describing typed operator across the three active
predicate scopes, plus unaffected ordinary string equality.

Focused tests run locally with `jsonschema==4.26.0`:

```text
test_v04_typed_operator_datatype_consistency
test_v04_field_requirement_schema
test_v04_object_selector_language
test_v04_clear_cardinality_schema
40 tests; all passed

test_generate_capability_schema_v04
test_v04_schema_draft
23 tests; all passed
```

No capability mapping or generated capability schema content is changed by
this edit. Full maintained regression and exact-head hosted CI remain separate
integration gates; focused success is not a claim of full CI verification or
semantic equivalence. No 65-benchmark corpus run was made for this schema fix.
