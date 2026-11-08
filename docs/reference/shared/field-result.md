# Native 0.4 field comparison Result

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Supplied field observations bound to a native require predicate and an exact retained Item/record; never an OVAL State/entity reference.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `field` | string | 1..1 (required) | **Unresolved description** | [/properties/field](../../../proposed-schema/documentation/field-result.schema.json#/properties/field) |
| `require_ref` | string | 1..1 (required) | Canonical RFC6901 location in the owning Assessment; semantic validation must resolve it to a requirement node of this Test. | [/properties/require_ref](../../../proposed-schema/documentation/field-result.schema.json#/properties/require_ref) |
| `record_ref` | string | 0..1 | Canonical RFC6901 pointer into the retained Item to this exact typed record instance, including array index when multivalued. | [/properties/record_ref](../../../proposed-schema/documentation/field-result.schema.json#/properties/record_ref) |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/outcome](../../../proposed-schema/documentation/field-result.schema.json#/properties/outcome) |
| `operation` | string | Conditional (at most 1) | **Unresolved description** | [/properties/operation](../../../proposed-schema/documentation/field-result.schema.json#/properties/operation) |
| `datatype` | string | 0..1 | Datatype used to interpret the value; payload validation and conversion rules are separate constraints. | [/properties/datatype](../../../proposed-schema/documentation/field-result.schema.json#/properties/datatype) |
| `values_found` | string | Conditional (at most 1) | State field/record existence cardinality. | [/properties/values_found](../../../proposed-schema/documentation/field-result.schema.json#/properties/values_found) |
| `values_matching` | string | Conditional (at most 1) | Consistent 0.4 authoring cardinality vocabulary. 'every' means all relevant results satisfy the specified comparison; source OVAL lexical values belong in provenance only. | [/properties/values_matching](../../../proposed-schema/documentation/field-result.schema.json#/properties/values_matching) |
| `value_match` | string | 0..1 | Consistent 0.4 authoring cardinality vocabulary. 'every' means all relevant results satisfy the specified comparison; source OVAL lexical values belong in provenance only. | [/properties/value_match](../../../proposed-schema/documentation/field-result.schema.json#/properties/value_match) |
| `requirement_ref` | string | Conditional (at most 1) | Canonical RFC6901 location in the owning Assessment; semantic validation must resolve it to a requirement node of this Test. | [/properties/requirement_ref](../../../proposed-schema/documentation/field-result.schema.json#/properties/requirement_ref) |
| `variable_refs` | array | 0..1 | References to Variables used by the comparison. | [/properties/variable_refs](../../../proposed-schema/documentation/field-result.schema.json#/properties/variable_refs) |
| `input_refs` | array | 0..1 | References to Inputs used by the comparison. | [/properties/input_refs](../../../proposed-schema/documentation/field-result.schema.json#/properties/input_refs) |
| `observed_values` | array | 1..1 (required) | Values reported as observed for this comparison. | [/properties/observed_values](../../../proposed-schema/documentation/field-result.schema.json#/properties/observed_values) |
| `expected_values` | array | Conditional (at most 1) | Values supplied as comparison operands. | [/properties/expected_values](../../../proposed-schema/documentation/field-result.schema.json#/properties/expected_values) |
| `comparison_results` | array | 0..1 | Recorded results of the individual comparisons. | [/properties/comparison_results](../../../proposed-schema/documentation/field-result.schema.json#/properties/comparison_results) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/reason](../../../proposed-schema/documentation/field-result.schema.json#/properties/reason) |
| `evidence_refs` | array | Conditional (at most 1) | References to the evidence supporting this result. | [/properties/evidence_refs](../../../proposed-schema/documentation/field-result.schema.json#/properties/evidence_refs) |
| `observation_complete` | boolean | 1..1 (required) | Explicit provider observation coverage for this field/record member. | [/properties/observation_complete](../../../proposed-schema/documentation/field-result.schema.json#/properties/observation_complete) |

## `/properties/comparison_results/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/comparison_results/items/properties/outcome](../../../proposed-schema/documentation/field-result.schema.json#/properties/comparison_results/items/properties/outcome) |
| `observed_value` | object | 0..1 | A typed scalar or record result value. | [/properties/comparison_results/items/properties/observed_value](../../../proposed-schema/documentation/field-result.schema.json#/properties/comparison_results/items/properties/observed_value) |
| `expected_value` | object | 0..1 | A typed scalar or record result value. | [/properties/comparison_results/items/properties/expected_value](../../../proposed-schema/documentation/field-result.schema.json#/properties/comparison_results/items/properties/expected_value) |

## Advanced constraints

[Local constraints](../advanced/field-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/field-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
