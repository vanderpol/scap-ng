# SCAP-NG Applicability Catalog v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `applicability` | object | 1..1 (required) | Named applicability conditions and their evaluation expression. | [/properties/applicability](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability) |
| `expression` | object | Definition | Boolean applicability expression. | [/$defs/expression](../../../proposed-schema/documentation/applicability.schema.json#/$defs/expression) |

## `/properties/applicability`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Applicability declaration identifier. | [/properties/applicability/properties/id](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/id) |
| `conditions` | object | 1..1 (required) | Map of condition names to their Assessment references. | [/properties/applicability/properties/conditions](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions) |

## `/properties/applicability/properties/conditions/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 0..1 | Assessment reference used for this applicability condition. | [/properties/applicability/properties/conditions/additionalProperties/properties/assessment](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/assessment) |
| `source` | object | 0..1 | Source identity and digest for the condition; provenance is not executable semantics. | [/properties/applicability/properties/conditions/additionalProperties/properties/source](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source) |

## `/properties/applicability/properties/conditions/additionalProperties/properties/source`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Source provenance kind, not an evaluation operator. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/kind](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/kind) |
| `id` | string | 1..1 (required) | Source platform or CPE identity. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/id](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/id) |
| `href` | string | 0..1 | Optional original component href. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/href](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/href) |
| `sha256` | string | 1..1 (required) | SHA-256 of the source platform element identity. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/sha256](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/sha256) |
| `idref` | string | 0..1 | Original XCCDF platform idref, including its leading fragment marker when present. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/idref](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/idref) |
| `expression_sha256` | string | 0..1 | SHA-256 of the normalized CPE Boolean tree when one is available. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/expression_sha256](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/expression_sha256) |
| `cpe_expression` | object | 0..1 | Normalized CPE logical-test tree retaining operator and negation semantics. | [/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/cpe_expression](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/source/properties/cpe_expression) |

## `/$defs/expression/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `condition` | string | 1..1 (required) | Catalog condition identifier. | [/$defs/expression/oneOf/0/properties/condition](../../../proposed-schema/documentation/applicability.schema.json#/$defs/expression/oneOf/0/properties/condition) |

## `/$defs/expression/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `all_of` | array | 1..1 (required) | All child expressions must be TRUE; ancestor levels use this operator to preserve inherited restrictions. | [/$defs/expression/oneOf/1/properties/all_of](../../../proposed-schema/documentation/applicability.schema.json#/$defs/expression/oneOf/1/properties/all_of) |

## `/$defs/expression/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `any_of` | array | 1..1 (required) | At least one child expression must be TRUE; same-item source platform alternatives use this operator. | [/$defs/expression/oneOf/2/properties/any_of](../../../proposed-schema/documentation/applicability.schema.json#/$defs/expression/oneOf/2/properties/any_of) |

## `/$defs/expression/oneOf/3`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `not` | object | 1..1 (required) | Boolean applicability expression. | [/$defs/expression/oneOf/3/properties/not](../../../proposed-schema/documentation/applicability.schema.json#/$defs/expression/oneOf/3/properties/not) |

## Advanced constraints

[Local constraints](../advanced/applicability.md) and [complete JSON Schema](../../../proposed-schema/documentation/applicability.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
