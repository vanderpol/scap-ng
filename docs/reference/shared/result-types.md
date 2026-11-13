# Draft shared result types 0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Reusable structural types for SCAP-NG result schemas. Runtime truth/aggregation semantics are defined by the specification and conformance tests, not by JSON Schema alone.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `technical_outcome` | string | Definition | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/$defs/technical_outcome](../../../proposed-schema/documentation/result-types.schema.json#/$defs/technical_outcome) |
| `assessment_purpose` | string | Definition | Purpose label distinguishing assessment and applicability evaluations. | [/$defs/assessment_purpose](../../../proposed-schema/documentation/result-types.schema.json#/$defs/assessment_purpose) |
| `assessment_class` | string | Definition | Defines what technical truth means. | [/$defs/assessment_class](../../../proposed-schema/documentation/result-types.schema.json#/$defs/assessment_class) |
| `completeness` | object | Definition | **Unresolved description** | [/$defs/completeness](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness) |
| `typed_value` | object | Definition | A typed scalar or record result value. | [/$defs/typed_value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value) |
| `bounded_evidence` | object | Definition | Reported evidence limits and failure counts; counting policy remains a separate contract. | [/$defs/bounded_evidence](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence) |

## `/$defs/completeness`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `logical_complete` | boolean | 1..1 (required) | **Unresolved description** | [/$defs/completeness/properties/logical_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/logical_complete) |
| `population_complete` | boolean | 1..1 (required) | **Unresolved description** | [/$defs/completeness/properties/population_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/population_complete) |
| `evidence_complete` | boolean | 1..1 (required) | **Unresolved description** | [/$defs/completeness/properties/evidence_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/evidence_complete) |
| `stop_reason` | null, string | 0..1 | **Unresolved description** | [/$defs/completeness/properties/stop_reason](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/stop_reason) |

## `/$defs/typed_value`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `datatype` | string | 1..1 (required) | Datatype used to interpret the value; payload validation and conversion rules are separate constraints. | [/$defs/typed_value/properties/datatype](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/datatype) |
| `value` | See schema | Conditional (at most 1) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/typed_value/properties/value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/value) |
| `status` | string | 1..1 (required) | Distinguishes an existing value from absence, an error, or a value that was not collected. | [/$defs/typed_value/properties/status](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/status) |
| `redacted` | boolean | 0..1 | Indicates that the value was intentionally omitted from the reported evidence. | [/$defs/typed_value/properties/redacted](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/redacted) |

## `/$defs/bounded_evidence`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `observed_failures` | integer | 1..1 (required) | **Unresolved description** | [/$defs/bounded_evidence/properties/observed_failures](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/observed_failures) |
| `actual_failures` | integer, string | 1..1 (required) | **Unresolved description** | [/$defs/bounded_evidence/properties/actual_failures](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/actual_failures) |
| `maximum` | integer | 1..1 (required) | **Unresolved description** | [/$defs/bounded_evidence/properties/maximum](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/maximum) |
| `returned` | integer | 1..1 (required) | **Unresolved description** | [/$defs/bounded_evidence/properties/returned](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/returned) |
| `truncated_population` | boolean | 1..1 (required) | **Unresolved description** | [/$defs/bounded_evidence/properties/truncated_population](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/truncated_population) |
| `stop_reason` | null, string | 0..1 | **Unresolved description** | [/$defs/bounded_evidence/properties/stop_reason](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/stop_reason) |

## Advanced constraints

[Local constraints](../advanced/result-types.md) and [complete JSON Schema](../../../proposed-schema/documentation/result-types.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
