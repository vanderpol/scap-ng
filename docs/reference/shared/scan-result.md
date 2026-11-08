# SCAP-NG Scan Result pre-release v0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Run-level index for one scanner execution. Detailed Benchmark and Assessment results remain normalized package members referenced by identity/path.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `scan_result` | object | 1..1 (required) | **Unresolved description** | [/properties/scan_result](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result) |

## `/properties/scan_result`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_schema_version` | string | 1..1 (required) | Version of the result serialization schema. | [/properties/scan_result/properties/result_schema_version](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/result_schema_version) |
| `run_id` | string | 1..1 (required) | Run identifier associated with this result. | [/properties/scan_result/properties/run_id](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/run_id) |
| `started_at` | string | 1..1 (required) | Timestamp recorded for the start of execution. | [/properties/scan_result/properties/started_at](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/started_at) |
| `completed_at` | null, string | 0..1 | Timestamp recorded for the completion of execution. | [/properties/scan_result/properties/completed_at](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/completed_at) |
| `scanner` | object | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/scanner](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/scanner) |
| `targets` | array | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/targets](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/targets) |
| `benchmark_results` | array | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/benchmark_results](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results) |
| `assessment_result_refs` | array | 0..1 | **Unresolved description** | [/properties/scan_result/properties/assessment_result_refs](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/assessment_result_refs) |
| `signature_status` | null, string | 0..1 | **Unresolved description** | [/properties/scan_result/properties/signature_status](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/signature_status) |

## `/properties/scan_result/properties/targets/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/targets/items/properties/id](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/targets/items/properties/id) |
| `identifiers` | array | 0..1 | **Unresolved description** | [/properties/scan_result/properties/targets/items/properties/identifiers](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/targets/items/properties/identifiers) |
| `hostname` | null, string | 0..1 | **Unresolved description** | [/properties/scan_result/properties/targets/items/properties/hostname](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/targets/items/properties/hostname) |
| `addresses` | array | 0..1 | **Unresolved description** | [/properties/scan_result/properties/targets/items/properties/addresses](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/targets/items/properties/addresses) |

## `/properties/scan_result/properties/benchmark_results/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `benchmark_result_ref` | string | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/benchmark_result_ref](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/benchmark_result_ref) |
| `benchmark_id` | string | 1..1 (required) | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/benchmark_id](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/benchmark_id) |
| `benchmark_version` | integer, null, string | 0..1 | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/benchmark_version](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/benchmark_version) |
| `target_ref` | string | 1..1 (required) | Reference to the evaluated target. | [/properties/scan_result/properties/benchmark_results/items/properties/target_ref](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/target_ref) |
| `profile_id` | null, string | 0..1 | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/profile_id](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/profile_id) |
| `tailoring_id` | null, string | 0..1 | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/tailoring_id](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/tailoring_id) |
| `summary` | object | 0..1 | **Unresolved description** | [/properties/scan_result/properties/benchmark_results/items/properties/summary](../../../proposed-schema/documentation/scan-result.schema.json#/properties/scan_result/properties/benchmark_results/items/properties/summary) |

## Advanced constraints

[Local constraints](../advanced/scan-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/scan-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
