# Draft invocation-linked Assessment Results transport

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Development transport of per-invocation artifacts; not a replacement result package or Benchmark Result.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `entry_execution_id` | string | 1..1 (required) | Identifier recorded for the entry Assessment execution. | [/properties/entry_execution_id](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/entry_execution_id) |
| `target_ref` | string | 1..1 (required) | Reference to the evaluated target. | [/properties/target_ref](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/target_ref) |
| `assessment_results` | array | 1..1 (required) | Assessment-result records carried by this result set. | [/properties/assessment_results](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/assessment_results) |

## Advanced constraints

[Local constraints](../advanced/assessment-result-set.md) and [complete JSON Schema](../../../proposed-schema/documentation/assessment-result-set.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
