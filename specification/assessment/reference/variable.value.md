# Variable value assessment — `variable.value`

**Status:** working 0.1.0 direct-Variable capability; draft 0.2.0 expressions and
reporting apply when the Assessment selects that draft specification. Full
Variable/comparator execution conformance remains open.

## Purpose and source

Use this capability to compare values produced by a named Variable. A Test
references `variable: <local-variable-id>` directly; it does not require an
Object whose only purpose is to point at that Variable. The reference must resolve
to a named Variable in the same Assessment. `object` is invalid for this Test.

The Variable may be constant, external, or derived through supported functions
and typed Object/Variable dataflow. Its own source graph remains meaningful:
direct Test binding does not erase named resource Objects, embedded sources,
filters, Sets, or intermediate Variable dependencies used to compute values.
Object and State capabilities in that source graph remain independently typed.

The [native mapping](../../../schema/v0.1.0/capability-mappings/variable.value.json)
adapts OVAL 5.12.3 `variable_test`, `variable_object`, `variable_state`, and
`variable_item`. Native `variable_object -> var_ref` indirection and the State's
redundant source-Variable identity check are removed. Source identities remain
in migration provenance; expected values and typed value multiplicity remain
part of evaluation.

## State and Item field reference

| Native field | Allowed datatypes | Cardinality and meaning | OVAL field |
| --- | --- | --- | --- |
| `value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | Variable-produced typed values; canonical Item `fields.value` is an array of typed values. | `value` |

The State compares `field: value` with an explicit datatype, operation, expected
literal or Variable reference, `match`, and `existence`. A State must use
`variable.value`; an unrelated capability cannot be silently substituted.
`record` is not in this reviewed capability's allowed datatype set.

Datatype validity does not mean every comparison operation is meaningful for
every type. Typed operation compatibility and the [shared aggregation contract](shared-behavior.md)
remain applicable. If the expected value references a multi-valued Variable,
preserve `variable_match` before entity `match`. `states_match` combines multiple
States independently from those inner quantifiers, and Test `match` combines
the per-Item results.

## Zero values, status, and results

Variables are typed value collections with zero/one/many cardinality and status.
An empty string is one string value, not a zero-value Variable. Do not invent
replacement values to hide zero cardinality or a resolution failure.

For the native direct `variable.value` Test, a referenced Variable that resolves
successfully but produces **zero values SHALL produce the technical outcome
`error` before State/value comparison**. This follows the pinned OVAL 5.12.3
Variable contract, which requires an analysis error when a Variable returns no
value. Removing the legacy `variable_object` wrapper SHALL NOT turn that source
error into Object absence, an empty successful Item set, Boolean false, unknown,
or not-applicable.

This direct-Test rule is deliberately narrower than every possible Variable use
inside an Object-selection graph. Object collection semantics remain governed by
the applicable Object/capability contract. A State entity that references a
zero-valued Variable likewise cannot perform its comparison and produces error at
that comparison layer. Missing Variable references remain invalid authored
content rather than runtime zero cardinality.

Evaluators SHALL preserve the distinction among:
- zero values: resolved Variable with no values → `error`;
- one empty string value for datatype string: one ordinary value;
- failed/errored Variable resolution: `error` with the underlying diagnostic;
- unavailable/indeterminate source where the finalized capability contract yields
  `unknown`: `unknown`, not zero values;
- one or many resolved values: continue normal typed comparison and aggregation.

Independent conformance fixtures SHALL cover zero/one/many values for constant,
external, and derived Variables where those source forms can legitimately produce
the cardinality. See [Variable semantics §5](../../../research/iterations/003/design/assessment-evaluation-semantics.md)
and #128/#131.

Test `existence` and `match` remain explicit structural fields. Missing Variable
references are invalid content. Runtime resolution errors/unknowns are distinct
from a correctly computed value that fails its State. Conditional scheduling
must not treat a Variable itself as a Boolean guard: use a Test whose comparison
produces the normalized technical outcome.

Draft 0.2.0 `reported_elements` may request `all`, `compared`, or an array using
the known field name `value`. Reporting does not change Variable evaluation,
comparison, or canonical evidence. Sensitive compared values still require
`redact_result: true`; an explicit field request does not override redaction.
There are no approved resolved user/group name additions for this capability.

## Example and validation evidence

[Conditional Assessment](../../../tests/assessment-results-0.2.0/content/conditional.assessment.yaml)
defines a Boolean constant Variable `guard`, a `variable.value` State comparing
to true, and a direct-Variable Test. Its main expression invokes ownership only
when that Test returns true; the false branch explicitly returns N/A.

[The six-case expected results](../../../tests/assessment-results-0.2.0/expected-results/cases.json)
document the scheduling oracle: true invokes ownership and yields its false
result for UID 1001; false yields the authored N/A; the other four guard outcomes
propagate without ownership execution. Those cases supply normalized Test
outcomes through a callback. They prove expression/result scheduling and recorded
consistency, not live evaluation of all six outcomes from a constant Variable.

From the repository root, run:

```sh
python tools/test_generate_variable_value_capability_schema.py
python tools/test_oval_result_truth_tables.py
python tools/test_conditional_integration.py
python tools/test_assessment_results_v02.py
```

The capability tests reject artificial Object binding and unresolved Variables,
restrict State fields, and validate direct source shapes. Shared tests exercise
quantifier/status rules and the expression helper. Additional independently
justified constant/external/derived zero/one/many values, datatype/operation
boundaries, failed resolution, redaction, and real source-graph execution remain.

## Provenance

Source contracts are the vendored OVAL 5.12.3
[independent definition schema](../../../third_party/scap-1.4-schemas/oval_5.12.3/independent-definitions-schema.xsd)
and [independent Item schema](../../../third_party/scap-1.4-schemas/oval_5.12.3/independent-system-characteristics-schema.xsd).
The publisher's retained extension in that baseline does not expand this
capability's reviewed field contract. Native direct binding follows the working
owner decisions and mapping. [Source ledger](sources.json) records exact byte
pins. Classification: Adapted source semantics, Common native explanatory text,
Evidence/Audit validation and coverage claims.
