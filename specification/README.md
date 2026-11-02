# Specification — SCAP-NG 0.4 (pre-alpha)

The [0.4 schemas](../schema/README.md) define the current **machine-readable structure**. The human-readable specification is being reconciled against approved 0.4 decisions. Schema validity alone does not establish runtime behavior or compliance.

## Core concepts

| Term | Meaning |
| --- | --- |
| Benchmark | Collection of policy Rules and Profiles |
| Rule | Policy requirement; selects an Assessment |
| Assessment | Reusable instructions for evaluating a requirement |
| Test | Capability-specific check within an Assessment |
| Object | Describes the data to collect |
| `require` | Defines conditions on collected Items and fields |
| Result | Reports an evaluation outcome with supporting evidence |

## Reading a Test

1. **`capability` and `object`:** specify what to collect. Some capabilities use another permitted source, such as a Variable.
2. **`require.item_requirement`:** specifies selected-Item existence and, when applicable, how many Items must satisfy the complete condition. Native Items do not include fabricated “does not exist” records.
3. **`require.field_requirement`:** specifies the shared field existence and matching requirements. A field or group may have a schema-permitted explicit override.
4. **`require.fields`:** describes expected field values, often with compact inline YAML mappings.
5. **`evaluate`:** combines complete Test outcomes. `and`, `or`, `one`, and `xor` are distinct from Item and Field cardinalities.

Compare the [Windows Registry](../examples/windows-server-2025-lock-screen.assessment.yaml) and [Linux nosuid](../examples/linux-home-nosuid.assessment.yaml) examples.

## Worked example: Windows Registry policy

The [Windows Server 2025 Registry Assessment](../examples/windows-server-2025-lock-screen.assessment.yaml) checks a specific value without separate named OVAL States:

```yaml
capability: windows.registry
object: {hive: {equals: local_machine}, key: {equals: 'SOFTWARE\Policies\Microsoft\Windows\Personalization'}, name: {equals: NoLockScreenSlideshow}}
require:
  item_requirement: {items_found: one_or_more, items_satisfying: every}
  field_requirement: {values_found: one_or_more, values_matching: every}
  fields: {type: {equals: dword}, value: {equals: 1}}
```

In ordinary language: **look up the specified Windows Registry value; require at least one collected Item; require every selected Item to satisfy the Test; and require the relevant collected fields to exist and match the expected DWORD type and value 1**. These are authored conditions, not observations from a scan.

The four parts answer different questions:

| Authored element | Question it answers |
| --- | --- |
| `object` | Which data should be acquired? |
| `items_found` | How many Items must be found? |
| `items_satisfying` | How many selected Items must satisfy the complete Test condition? |
| `values_found` / `values_matching` | What is required of the collected field values? |
| `fields` | What values or comparisons are expected? |

**Shared requirements are not repetitive per-field settings.** The Test-level `field_requirement` applies across fields according to the language contract. Keep an explicit field-level override when a particular field intentionally differs; do not mechanically delete it. For instance, the [SYSVOL example](../examples/windows-server-2025-sysvol-permissions.assessment.yaml) explicitly requires `stderr_line: {values_found: none}`, rather than applying the shared requirement of at least one value. The [Linux `nosuid` example](../examples/linux-home-nosuid.assessment.yaml) uses `values_matching: one_or_more` for mount options, not `every`; these choices are not interchangeable.

The `evaluate` expression is a separate level: it combines complete Test outcomes, not individual Registry or mount field values. `one` means exactly one branch is true, while `xor` represents odd parity across branches. For source-specific value acquisition, advanced Variables, logical groupings and complex regular expressions, inspect the [SYSVOL example](../examples/windows-server-2025-sysvol-permissions.assessment.yaml); do not infer runtime scanner behavior from a valid authoring document.

## Inputs and outcomes

An optional Input may be **omitted**; that is not the same as an explicitly supplied empty value. Consumers of optional Inputs require an explicit `input_provided` guard. The [Input example](../examples/windows-optional-organizational-input.assessment.yaml) shows a `not_evaluated` fallback when the organization has not supplied the expected value.

`not_evaluated` documents inability to evaluate a branch; `not_applicable` indicates a different, reasoned outcome. Neither is a substitute for a failed check or collection error. Result rollups and scanner-runtime conformance must be established by their applicable semantic and Result contracts, not inferred from these examples.

## Reading results without confusing them with policy

SCAP-NG separates **technical evaluation** from the **policy interpretation** of that evaluation:

| Layer | What it describes | Source schema |
| --- | --- | --- |
| Test Result | Observed data and evaluation for an individual Test | [Test Result](../schema/test-result.schema.json) |
| Assessment Result | The Assessment invocation, technical outcome, reason, completeness and supporting Test/collection data | [Assessment Result](../schema/assessment-result.schema.json) |
| Rule Result | Policy-facing evaluation of a Rule that consumes an Assessment | [Rule Result](../schema/rule-result.schema.json) |
| Benchmark Result | Effective policy selection, Rule Results and summary counters for a target | [Benchmark Result](../schema/benchmark-result.schema.json) |

The [shared Result types](../schema/result-types.schema.json) declare **six technical outcomes**: `true`, `false`, `error`, `unknown`, `not_evaluated`, and `not_applicable`. A technical `true` is **not by itself** a policy `pass`: the consuming Rule determines policy meaning. `Informational` is not a seventh technical truth value.

The Assessment Result requires a concise human-readable `summary` alongside `outcome` and three separate completeness flags: `logical_complete`, `population_complete`, and `evidence_complete`. Do not replace those distinctions with a generic "passed" label. The Benchmark Result structurally requires counters for `total`, `pass`, `fail`, `not_applicable`, `not_evaluated`, `error`, and `unknown`. Reporting those fields does **not** establish the policies for counting, denominators or rollups.

The Result schemas define *permitted data structures*. They do **not** settle runtime truth propagation, early-stop behavior, error precedence, completeness qualifications, policy rollup, or percentage denominators. Those require explicit normative rules and conformance tests before a scanner or editor claims definitive execution behavior. An authoring preview is not a live Result.

## Known compatibility gap: Organizational Input use locations

The [native Assessment grammar](../schema/assessment.schema.json) rejects named Test `state` and `states` structures. The [Rule schema](../schema/rule.schema.json) nevertheless currently requires `test`, `state`, and `state_slot` in each `organizational_input_requirements.*[].uses[]` entry. The [Assessment Result schema](../schema/assessment-result.schema.json) also retains optional `state_slot` fields for consumed organizational Inputs and related reasons.

This **is a real pre-alpha structural mismatch**, not permission to reintroduce OVAL States in native Assessments or to manufacture placeholders. Its purpose and consumer compatibility are not yet reconciled. The exact follow-up and required migration/conformance review are tracked in [Issue #8](https://github.com/vanderpol/scap-ng/issues/8). Until that contract is resolved, the [optional Input example](../examples/windows-optional-organizational-input.assessment.yaml) demonstrates Assessment-level presence handling only; it does **not** claim to demonstrate a complete Rule dependency-map integration.

## Authority and remaining work

Use the [generated schema reference](../docs/generated/schema-reference.md) for structural details and the [capability catalog](../docs/generated/capability-catalog.md) for supported selectors. The editor may hide **explicitly serialized** defaults using pinned schema metadata; it must not invent scanner-side defaults or rewrite source on open/save.

Detailed evaluation truth tables, applicability/Result rollups, case sensitivity, manual and shared Assessment semantics, packaging and any residual legacy vocabulary require separate reconciliation. Older 0.3 research and proposed 0.5 features are **not** automatically part of 0.4. See [provenance](../docs/PROVENANCE.md).
