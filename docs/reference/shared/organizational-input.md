# SCAP-NG Organizational Input Set v0.4.0 draft

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Supplies organizational values for Parameters delegated by a Benchmark publisher.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organizational_input` | object | 1..1 (required) | **Unresolved description** | [/properties/organizational_input](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input) |

## `/properties/organizational_input`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/id](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/version](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/version) |
| `purpose` | string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/purpose](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/purpose) |
| `benchmark` | object | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/benchmark](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/benchmark) |
| `intended_scope` | null, object | 0..1 | Descriptive intended scope only. | [/properties/organizational_input/properties/intended_scope](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/intended_scope) |
| `values` | object | 1..1 (required) | Parameter ID to supplied typed value. | [/properties/organizational_input/properties/values](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/values) |
| `value_provenance` | object | 0..1 | Optional per-Parameter provenance when values have different authorities or sources. | [/properties/organizational_input/properties/value_provenance](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance) |
| `effective_from` | null, string | 0..1 | Timestamp from which this declaration applies. | [/properties/organizational_input/properties/effective_from](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/effective_from) |
| `expires_at` | null, string | 0..1 | Timestamp at which this declaration expires. | [/properties/organizational_input/properties/expires_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/expires_at) |
| `provenance` | object | 1..1 (required) | Source and collection context for this evidence. | [/properties/organizational_input/properties/provenance](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance) |

## `/properties/organizational_input/properties/benchmark`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/benchmark/properties/id](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/benchmark/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/benchmark/properties/version](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/benchmark/properties/version) |

## `/properties/organizational_input/properties/intended_scope`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organization` | null, object, string | 0..1 | Organization associated with this declaration. | [/properties/organizational_input/properties/intended_scope/properties/organization](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/intended_scope/properties/organization) |
| `organizational_unit` | null, string | 0..1 | Organizational unit associated with this declaration. | [/properties/organizational_input/properties/intended_scope/properties/organizational_unit](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/intended_scope/properties/organizational_unit) |
| `system_or_environment` | null, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/intended_scope/properties/system_or_environment](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/intended_scope/properties/system_or_environment) |
| `description` | null, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/intended_scope/properties/description](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/intended_scope/properties/description) |

## `/properties/organizational_input/properties/value_provenance/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organization` | null, object, string | 0..1 | Organization associated with this declaration. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/organization](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/organization) |
| `supplied_by` | null, object, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/supplied_by](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/supplied_by) |
| `supplied_at` | null, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/supplied_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/supplied_at) |
| `authority_basis` | null, object, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authority_basis](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authority_basis) |
| `authorization_reference` | null, string | 0..1 | Reference documenting the authorization. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorization_reference](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorization_reference) |
| `authorized_by` | null, object, string | 0..1 | Identity recorded as authorizing the action. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorized_by](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorized_by) |
| `authorized_at` | null, string | 0..1 | Timestamp recorded for the authorization. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorized_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/authorized_at) |
| `source_system` | null, object, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/source_system](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/source_system) |
| `intended_scope` | null, object | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/intended_scope](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/intended_scope) |
| `effective_from` | null, string | 0..1 | Timestamp from which this declaration applies. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/effective_from](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/effective_from) |
| `expires_at` | null, string | 0..1 | Timestamp at which this declaration expires. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/expires_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/expires_at) |
| `contact` | null, object | 0..1 | Contact information for the responsible party. | [/properties/organizational_input/properties/value_provenance/additionalProperties/properties/contact](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/value_provenance/additionalProperties/properties/contact) |

## `/properties/organizational_input/properties/provenance`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organization` | null, object, string | 1..1 (required) | Organization associated with this declaration. | [/properties/organizational_input/properties/provenance/properties/organization](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/organization) |
| `supplied_by` | object, string | 1..1 (required) | Person, service, or authoritative system that supplied the Input Set. | [/properties/organizational_input/properties/provenance/properties/supplied_by](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/supplied_by) |
| `supplied_at` | string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/provenance/properties/supplied_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/supplied_at) |
| `source_system` | null, object, string | 0..1 | **Unresolved description** | [/properties/organizational_input/properties/provenance/properties/source_system](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/source_system) |
| `authorized_by` | null, object, string | 0..1 | Identity recorded as authorizing the action. | [/properties/organizational_input/properties/provenance/properties/authorized_by](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/authorized_by) |
| `authorized_at` | null, string | 0..1 | Timestamp recorded for the authorization. | [/properties/organizational_input/properties/provenance/properties/authorized_at](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/authorized_at) |
| `authorization_reference` | null, string | 0..1 | Reference documenting the authorization. | [/properties/organizational_input/properties/provenance/properties/authorization_reference](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/authorization_reference) |
| `authorization_status` | null, string | 1..1 (required) | **Unresolved description** | [/properties/organizational_input/properties/provenance/properties/authorization_status](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/authorization_status) |
| `contact` | null, object | 0..1 | Contact information for the responsible party. | [/properties/organizational_input/properties/provenance/properties/contact](../../../proposed-schema/documentation/organizational-input.schema.json#/properties/organizational_input/properties/provenance/properties/contact) |

## Advanced constraints

[Local constraints](../advanced/organizational-input.md) and [complete JSON Schema](../../../proposed-schema/documentation/organizational-input.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
