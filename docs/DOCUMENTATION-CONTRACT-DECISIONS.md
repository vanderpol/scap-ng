# Remaining documentation contract decisions

These are engineering questions, not adopted language semantics. Field
annotations remain authoritative in the proposed JSON Schemas; no behavior is
implemented by this packet. Exact pointers and any bounded draft wording are in
[the generated gap ledger](reference/gaps.jsonl).

The ledger retains 148 shared-node description gaps: 48 in the explicitly
inactive function-call migration schema, 27 in the older type-resolution helper
not referenced by the Assessment schema, and 73 in declared schema contexts.
The last group includes existing holds and repeated constraint copies; it is
not a count of 73 separate decisions. Abbreviated schema pointers below are
relative to `proposed-schema/documentation/`. Eight capability field routes additionally
represent four unresolved native field meanings.

## Existing holds

Preserve the nine semantic decisions and withheld foreach recorded in PR #41.
The approved descriptions remain unchanged. In particular, do not resolve
ONE/XOR truth tables, transformation casting/status propagation, Variable
datatype promises, generic typed payload consistency, or the broader Benchmark
contract by copying legacy behavior or interpreting schema acceptance as runtime
proof. The original editorial receipts remain the decision authority.

## Completeness flags and counters

Representative pointers:

- `assessment-result.schema.json#/properties/assessment_result/properties/logical_complete`
- `assessment-result.schema.json#/properties/assessment_result/properties/population_complete`
- `assessment-result.schema.json#/properties/assessment_result/properties/evidence_complete`
- `rule-result.schema.json#/properties/finding_counts`
- `test-result.schema.json#/properties/item_summary`
- `result-types.schema.json#/$defs/bounded_evidence`
- `benchmark-result.schema.json#/properties/benchmark_result/properties/summary`

Alternatives include defining each counter over evaluated, observed, retained,
or complete-population records. These populations can differ. A Rule-instance
count and a unique-Rule count can also differ. Merely having nonnegative integer
fields does not choose a counting policy or an aggregation rule.

Recommend distinct contracts for logical evaluation, collected population, and
retained evidence, with explicit counting populations and truncation witnesses.
Preserve the existing structural rule requiring `actual_violations: unknown`
when `population_complete` is false. Do not equate unknown totals with zero or
infer completeness from a pass/fail outcome. Calculation and rollup descriptions
should wait for the relevant native contract.

## Item materialization and projection

Representative pointers:

- `item-materialization.schema.json#/properties/available_count`
- `item-materialization.schema.json#/properties/included_count`
- `item-materialization.schema.json#/properties/omitted_count`
- `item-report.schema.json#/properties/item_report/properties/items/items/properties/selection`
- `assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/materialized`

Alternatives include counting all available source Items, consumed Items, or
retained/materialized Items. Projection has a separate question: which authority
makes an element required, and how do intentionally omitted elements differ
from unavailable source data or collection errors?

Recommend separate collection, evaluation-use, and retention/projection
contracts. Define the `materialized` flag explicitly: whether it records an
inline value, retained evidence, or another state. Preserve the current
redaction prohibition on including a redacted value. No missing/error inference
or new count equation is introduced here.

## Provision-trace metadata

Representative pointers:

- `expression-invocation.schema.json#/properties/trace/items/properties/source`
- `expression-invocation.schema.json#/properties/trace/items/properties/source_ref`
- `expression-invocation.schema.json#/properties/trace/items/properties/follow_up`

The fields could describe binding provenance, execution provenance, or a
follow-up evaluation reference. A generic string type does not establish the
reference namespace or the meaning of each label.

Recommend documenting the native producer contract and independently expected
trace witnesses before assigning those meanings. Keep the current invocation
trace distinct from the older expression-result trace: their field sets differ.
Input provision remains distinct from value truthiness and nonemptiness.

## Package entry points and size units

Exact pointers:

- `package-manifest.schema.json#/properties/entrypoint`
- `package-manifest.schema.json#/$defs/object_record/properties/size`
- `result-package-manifest.schema.json#/properties/members/items/properties/size`

For `entrypoint`, alternatives are a logical document ID or a stored member
path. Recommend a logical ID consistent with the existing manifest root
statement that logical IDs are authoritative and paths are storage bindings.
The field's string shape alone does not settle this choice.

For `size`, alternatives include stored-member byte length or the length of a
normalized/logical representation. Recommend explicitly identifying the exact
stored representation and defining the size and digest inputs consistently.
No byte unit is silently asserted in the reference. This is a documentation
question; no packaging, release preparation or artifact transfer is performed.

## Four capability field meanings

Exact owners, shared by Item and Require:

- `capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/days_since_last_logon`
- `capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_64key`
- `capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_32key`
- `capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_res`

NTUSER alternatives include legacy profile-load-time age with active-session
normalization, or a native logon-event observation. Recommend specifying the
native observation, time basis and active-session treatment before adopting a
meaning. For the WOW64 fields, view-selection/access-mask flags and granted
effective rights are different concepts. Recommend deciding their native
representation explicitly. Existing validation and source provenance remain
unchanged while the descriptions are withheld.
