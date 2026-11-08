# Draft unsigned result-package integrity manifest

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `format_version` | string | 1..1 (required) | **Unresolved description** | [/properties/format_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/format_version) |
| `result_schema_version` | string | 1..1 (required) | Version of the result serialization schema. | [/properties/result_schema_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/result_schema_version) |
| `digest_algorithm` | string | 1..1 (required) | **Unresolved description** | [/properties/digest_algorithm](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/digest_algorithm) |
| `signature_status` | string | 1..1 (required) | **Unresolved description** | [/properties/signature_status](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/signature_status) |
| `run_id` | string | 1..1 (required) | Run identifier associated with this result. | [/properties/run_id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/run_id) |
| `scan_result_ref` | string | 1..1 (required) | **Unresolved description** | [/properties/scan_result_ref](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/scan_result_ref) |
| `members` | array | 1..1 (required) | **Unresolved description** | [/properties/members](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members) |
| `evaluation_groups` | array | 1..1 (required) | **Unresolved description** | [/properties/evaluation_groups](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups) |

## `/properties/members/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/members/items/properties/id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/id) |
| `kind` | string | 1..1 (required) | Kind of result document contained in this package member. | [/properties/members/items/properties/kind](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/kind) |
| `path` | string | 1..1 (required) | **Unresolved description** | [/properties/members/items/properties/path](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/path) |
| `sha256` | string | 1..1 (required) | **Unresolved description** | [/properties/members/items/properties/sha256](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/sha256) |
| `size` | integer | 1..1 (required) | **Unresolved description** | [/properties/members/items/properties/size](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/size) |
| `schema_version` | string | 1..1 (required) | **Unresolved description** | [/properties/members/items/properties/schema_version](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/members/items/properties/schema_version) |

## `/properties/evaluation_groups/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `entry_execution_id` | string | 1..1 (required) | **Unresolved description** | [/properties/evaluation_groups/items/properties/entry_execution_id](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/entry_execution_id) |
| `target_ref` | string | 1..1 (required) | Reference to the evaluated target. | [/properties/evaluation_groups/items/properties/target_ref](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/target_ref) |
| `execution_ids` | array | 1..1 (required) | **Unresolved description** | [/properties/evaluation_groups/items/properties/execution_ids](../../../proposed-schema/documentation/result-package-manifest.schema.json#/properties/evaluation_groups/items/properties/execution_ids) |

## Advanced constraints

[Local constraints](../advanced/result-package-manifest.md) and [complete JSON Schema](../../../proposed-schema/documentation/result-package-manifest.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
