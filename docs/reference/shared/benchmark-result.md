# SCAP-NG Benchmark Result pre-release v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Benchmark-scoped policy result for one Benchmark evaluation against one scan-level target reference. Run-wide scanner and target details are not duplicated here.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `benchmark_result` | object | 1..1 (required) | Benchmark evaluation result with its recorded policy and Rule-result entries. | [/properties/benchmark_result](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result) |

## `/properties/benchmark_result`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_schema_version` | string | 1..1 (required) | Version of the result serialization schema. | [/properties/benchmark_result/properties/result_schema_version](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/result_schema_version) |
| `run_id` | string | 1..1 (required) | Run identifier associated with this result. | [/properties/benchmark_result/properties/run_id](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/run_id) |
| `started_at` | string | 1..1 (required) | Timestamp recorded for the start of execution. | [/properties/benchmark_result/properties/started_at](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/started_at) |
| `completed_at` | null, string | 1..1 (required) | Timestamp recorded for the completion of execution. | [/properties/benchmark_result/properties/completed_at](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/completed_at) |
| `benchmark` | object | 1..1 (required) | Identity of the Benchmark being reported. | [/properties/benchmark_result/properties/benchmark](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/benchmark) |
| `effective_policy` | object | 1..1 (required) | Policy selections and Parameter bindings recorded for this evaluation. | [/properties/benchmark_result/properties/effective_policy](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy) |
| `summary` | object | 1..1 (required) | Reported outcome counters; counting and rollup policy remain separate contracts. | [/properties/benchmark_result/properties/summary](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary) |
| `rule_results` | array | 1..1 (required) | Rule-result entries associated with this Benchmark evaluation. | [/properties/benchmark_result/properties/rule_results](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/rule_results) |
| `target_ref` | string | 1..1 (required) | Reference to the scan-level target evaluated by this Benchmark Result. | [/properties/benchmark_result/properties/target_ref](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/target_ref) |

## `/properties/benchmark_result/properties/benchmark`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the Benchmark being reported. | [/properties/benchmark_result/properties/benchmark/properties/id](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/benchmark/properties/id) |
| `version` | integer, string | 1..1 (required) | Version of the Benchmark being reported. | [/properties/benchmark_result/properties/benchmark/properties/version](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/benchmark/properties/version) |
| `package_digest` | null, string | 0..1 | Digest recorded for the Benchmark package. | [/properties/benchmark_result/properties/benchmark/properties/package_digest](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/benchmark/properties/package_digest) |

## `/properties/benchmark_result/properties/effective_policy`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `profile` | null, string | 1..1 (required) | Profile identifier recorded for this evaluation. | [/properties/benchmark_result/properties/effective_policy/properties/profile](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/profile) |
| `tailoring` | null, object | 1..1 (required) | Tailoring information recorded for this evaluation. | [/properties/benchmark_result/properties/effective_policy/properties/tailoring](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/tailoring) |
| `selected_rules` | array | 1..1 (required) | Rule identifiers recorded as selected. | [/properties/benchmark_result/properties/effective_policy/properties/selected_rules](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/selected_rules) |
| `disabled_rules` | array | 1..1 (required) | Rule identifiers recorded as disabled. | [/properties/benchmark_result/properties/effective_policy/properties/disabled_rules](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/disabled_rules) |
| `check_selectors` | object | 1..1 (required) | Assessment-choice selections recorded for the Rules. | [/properties/benchmark_result/properties/effective_policy/properties/check_selectors](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/check_selectors) |
| `parameters` | object | 1..1 (required) | Effective Parameter bindings recorded for the evaluation. | [/properties/benchmark_result/properties/effective_policy/properties/parameters](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/parameters) |
| `organizational_inputs` | object | 1..1 (required) | Run-local registry of effective Organizational Input assertions used by the run. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs) |

## `/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `parameter` | string | 1..1 (required) | Identifier of the Parameter supplied by this binding. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/parameter](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/parameter) |
| `value` | See schema | Conditional (at most 1) | Value supplied for the Parameter; redaction is specified separately. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/value](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/value) |
| `source` | string | 1..1 (required) | Source category recorded for the supplied policy value. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/source](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/source) |
| `input_set` | null, object | 0..1 | Identity of the Organizational Input Set recorded for the binding. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set) |
| `provenance` | object | 1..1 (required) | Source and collection context for this evidence. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/provenance](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/provenance) |
| `scope` | null, object | 0..1 | Scope metadata recorded for this policy binding. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/scope](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/scope) |
| `effective_from` | null, string | 0..1 | Timestamp from which this declaration applies. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/effective_from](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/effective_from) |
| `expires_at` | null, string | 0..1 | Timestamp at which this declaration expires. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/expires_at](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/expires_at) |
| `redacted` | boolean | 0..1 | Whether this value was redacted from reported evidence. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/redacted](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/redacted) |

## `/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 0..1 | Identifier of the supplying Organizational Input Set. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set/properties/id](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set/properties/id) |
| `version` | integer, string | 0..1 | Version of the supplying Organizational Input Set. | [/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set/properties/version](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/effective_policy/properties/organizational_inputs/additionalProperties/properties/input_set/properties/version) |

## `/properties/benchmark_result/properties/summary`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `total` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/total](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/total) |
| `pass` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/pass](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/pass) |
| `fail` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/fail](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/fail) |
| `not_applicable` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/not_applicable](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/not_applicable) |
| `not_evaluated` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/not_evaluated](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/not_evaluated) |
| `error` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/error](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/error) |
| `unknown` | integer | 1..1 (required) | **Unresolved description** | [/properties/benchmark_result/properties/summary/properties/unknown](../../../proposed-schema/documentation/benchmark-result.schema.json#/properties/benchmark_result/properties/summary/properties/unknown) |

## Advanced constraints

[Local constraints](../advanced/benchmark-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/benchmark-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
