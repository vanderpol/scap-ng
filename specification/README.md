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

## Inputs and outcomes

An optional Input may be **omitted**; that is not the same as an explicitly supplied empty value. Consumers of optional Inputs require an explicit `input_provided` guard. The [Input example](../examples/windows-optional-organizational-input.assessment.yaml) shows a `not_evaluated` fallback when the organization has not supplied the expected value.

`not_evaluated` documents inability to evaluate a branch; `not_applicable` indicates a different, reasoned outcome. Neither is a substitute for a failed check or collection error. Result rollups and scanner-runtime conformance must be established by their applicable semantic and Result contracts, not inferred from these examples.

## Authority and remaining work

Use the [generated schema reference](../docs/generated/schema-reference.md) for structural details and the [capability catalog](../docs/generated/capability-catalog.md) for supported selectors. The editor may hide **explicitly serialized** defaults using pinned schema metadata; it must not invent scanner-side defaults or rewrite source on open/save.

Detailed evaluation truth tables, applicability/Result rollups, case sensitivity, manual and shared Assessment semantics, packaging and any residual legacy vocabulary require separate reconciliation. Older 0.3 research and proposed 0.5 features are **not** automatically part of 0.4. See [provenance](../docs/PROVENANCE.md).
