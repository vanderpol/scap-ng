# SCAP-NG declared CPE identity v0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

A lossless source CPE identity declared by a Benchmark platform. This metadata is not an applicability decision or a CPE matching result.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `value` | string | 1..1 (required) | Exact source CPE spelling, including escaping and packed-edition syntax; no normalization or matching is implied. | [/properties/value](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/value) |
| `binding` | string | 1..1 (required) | CPE naming binding used by the source value. | [/properties/binding](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/binding) |
| `source` | object | 1..1 (required) | Immutable source provenance for the declared identity. | [/properties/source](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source) |

## `/properties/source`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Source provenance kind; it does not authorize executable matching. | [/properties/source/properties/kind](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/kind) |
| `id` | string | 1..1 (required) | Source CPE/platform identity associated with this declaration. | [/properties/source/properties/id](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/id) |
| `idref` | string | 0..1 | Original source identifier or reference, when present. | [/properties/source/properties/idref](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/idref) |
| `href` | string | 0..1 | Original source component location, when present. | [/properties/source/properties/href](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/href) |
| `sha256` | string | 1..1 (required) | SHA-256 of the source identity element or preserved source provenance record. | [/properties/source/properties/sha256](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/sha256) |

## Advanced constraints

[Local constraints](../advanced/cpe-identity.md) and [complete JSON Schema](../../../proposed-schema/documentation/cpe-identity.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
