# SCAP-NG Applicability Catalog v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `applicability` | object | 1..1 (required) | Named applicability conditions and their evaluation expression. | [/properties/applicability](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability) |

## `/properties/applicability`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Applicability declaration identifier. | [/properties/applicability/properties/id](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/id) |
| `conditions` | object | 1..1 (required) | Map of condition names to their Assessment references. | [/properties/applicability/properties/conditions](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions) |

## `/properties/applicability/properties/conditions/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 1..1 (required) | Assessment reference used for this applicability condition. | [/properties/applicability/properties/conditions/additionalProperties/properties/assessment](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/assessment) |

## Advanced constraints

[Local constraints](../advanced/applicability.md) and [complete JSON Schema](../../../proposed-schema/documentation/applicability.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
