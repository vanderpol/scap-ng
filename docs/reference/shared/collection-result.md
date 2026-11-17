# SCAP-NG Object Collection Result pre-release v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Records an Object's collection outcome and supporting Item references.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of this Object collection result. | [/properties/id](../../../proposed-schema/documentation/collection-result.schema.json#/properties/id) |
| `object_title` | null, string | 0..1 | Human-readable title for the Object. | [/properties/object_title](../../../proposed-schema/documentation/collection-result.schema.json#/properties/object_title) |
| `capability` | string | 1..1 (required) | Capability responsible for collecting or interpreting this resource. | [/properties/capability](../../../proposed-schema/documentation/collection-result.schema.json#/properties/capability) |
| `status` | string | 1..1 (required) | Reports the outcome of collecting an Object’s Items. | [/properties/status](../../../proposed-schema/documentation/collection-result.schema.json#/properties/status) |
| `item_refs` | array | 1..1 (required) | Identifies the Items retained or referenced by this collection result. | [/properties/item_refs](../../../proposed-schema/documentation/collection-result.schema.json#/properties/item_refs) |
| `logical_complete` | boolean, null | 0..1 | **Unresolved description** | [/properties/logical_complete](../../../proposed-schema/documentation/collection-result.schema.json#/properties/logical_complete) |
| `population_complete` | boolean, null | Conditional (at most 1) | **Unresolved description** | [/properties/population_complete](../../../proposed-schema/documentation/collection-result.schema.json#/properties/population_complete) |
| `stop_reason` | null, string | Conditional (at most 1) | Reason recorded for stopping Object collection. | [/properties/stop_reason](../../../proposed-schema/documentation/collection-result.schema.json#/properties/stop_reason) |
| `source_execution_ref` | null, string | 0..1 | Reference to the source execution whose evidence is used. | [/properties/source_execution_ref](../../../proposed-schema/documentation/collection-result.schema.json#/properties/source_execution_ref) |
| `diagnostics` | array | Conditional (at most 1) | Diagnostic entries associated with this result. | [/properties/diagnostics](../../../proposed-schema/documentation/collection-result.schema.json#/properties/diagnostics) |

## Advanced constraints

[Local constraints](../advanced/collection-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/collection-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
