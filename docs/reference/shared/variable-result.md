# SCAP-NG Variable Result draft v0.4.0 strawman

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Resolved runtime Variable value set with explicit datatype, cardinality, status, and provenance.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the Variable being reported. | [/properties/id](../../../proposed-schema/documentation/variable-result.schema.json#/properties/id) |
| `variable_title` | null, string | 0..1 | Human-readable title of the reported Variable. | [/properties/variable_title](../../../proposed-schema/documentation/variable-result.schema.json#/properties/variable_title) |
| `datatype` | string | 1..1 (required) | OVAL-compatible Variable results are not record-typed; records are collected Item/entity structures. | [/properties/datatype](../../../proposed-schema/documentation/variable-result.schema.json#/properties/datatype) |
| `status` | string | 1..1 (required) | Completeness/evaluation status of the resolved Variable value set. 'incomplete' explicitly preserves a partial known value stream; values and cardinality describe only observed values, not a proved total population. | [/properties/status](../../../proposed-schema/documentation/variable-result.schema.json#/properties/status) |
| `cardinality` | string | 1..1 (required) | Reported size class of the Variable value set. | [/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/properties/cardinality) |
| `values` | array | 1..1 (required) | Values reported for the Variable. | [/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/properties/values) |
| `source` | null, string | 0..1 | Source label associated with the reported Variable values. | [/properties/source](../../../proposed-schema/documentation/variable-result.schema.json#/properties/source) |
| `provenance` | object | 0..1 | Source and collection context for this evidence. | [/properties/provenance](../../../proposed-schema/documentation/variable-result.schema.json#/properties/provenance) |
| `diagnostics` | array | 0..1 | Diagnostic entries associated with this result. | [/properties/diagnostics](../../../proposed-schema/documentation/variable-result.schema.json#/properties/diagnostics) |
| `item_refs` | array | 1..1 (required) | Local Items consumed while producing this Variable, including intermediate extraction/filter/selection use. | [/properties/item_refs](../../../proposed-schema/documentation/variable-result.schema.json#/properties/item_refs) |

## Advanced constraints

[Local constraints](../advanced/variable-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/variable-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
