# Native 0.4 requirement Result

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Technical observation at one native Test/group/record/field location; record_ref preserves per-record correlation. Source OVAL identities belong only in migration provenance.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `require_ref` | string | 1..1 (required) | Canonical RFC6901 location in the owning Assessment; semantic validation must resolve it to a requirement node of this Test. | [/properties/require_ref](../../../proposed-schema/documentation/require-result.schema.json#/properties/require_ref) |
| `record_ref` | string | 0..1 | Canonical RFC6901 pointer into the retained Item to this exact typed record instance, including array index when multivalued. | [/properties/record_ref](../../../proposed-schema/documentation/require-result.schema.json#/properties/record_ref) |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/outcome](../../../proposed-schema/documentation/require-result.schema.json#/properties/outcome) |
| `operator` | string | 0..1 | **Unresolved description** | [/properties/operator](../../../proposed-schema/documentation/require-result.schema.json#/properties/operator) |
| `records_found` | string | 0..1 | State field/record existence cardinality. | [/properties/records_found](../../../proposed-schema/documentation/require-result.schema.json#/properties/records_found) |
| `records_matching` | string | 0..1 | Consistent 0.4 authoring cardinality vocabulary. 'every' means all relevant results satisfy the specified comparison; source OVAL lexical values belong in provenance only. | [/properties/records_matching](../../../proposed-schema/documentation/require-result.schema.json#/properties/records_matching) |
| `field_results` | array | 1..1 (required) | Field observations associated with this result. | [/properties/field_results](../../../proposed-schema/documentation/require-result.schema.json#/properties/field_results) |
| `require_results` | array | 0..1 | Nested Require observations associated with this result. | [/properties/require_results](../../../proposed-schema/documentation/require-result.schema.json#/properties/require_results) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/reason](../../../proposed-schema/documentation/require-result.schema.json#/properties/reason) |
| `evidence_refs` | array | Conditional (at most 1) | References to the evidence supporting this result. | [/properties/evidence_refs](../../../proposed-schema/documentation/require-result.schema.json#/properties/evidence_refs) |
| `observation_complete` | boolean | 0..1 | Explicit supplied completeness for record absence; never inferred from missing retained values. | [/properties/observation_complete](../../../proposed-schema/documentation/require-result.schema.json#/properties/observation_complete) |

## Advanced constraints

[Local constraints](../advanced/require-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/require-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
