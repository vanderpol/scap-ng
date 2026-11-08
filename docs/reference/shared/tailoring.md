# SCAP-NG Tailoring v0.4.0 strawman

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

External local-policy modification bound to an exact Benchmark publication. This pre-release schema describes the policy-resolution structure; evaluation semantics are defined in the specification.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `tailoring` | object | 1..1 (required) | **Unresolved description** | [/properties/tailoring](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring) |

## `/properties/tailoring`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Stable logical identity of this Tailoring artifact. | [/properties/tailoring/properties/id](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/id) |
| `version` | integer, string | 1..1 (required) | Tailoring version/revision. | [/properties/tailoring/properties/version](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/version) |
| `purpose` | string | 1..1 (required) | Human-readable reason the Tailoring exists. | [/properties/tailoring/properties/purpose](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/purpose) |
| `benchmark` | object | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/benchmark](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/benchmark) |
| `profile` | null, string | 1..1 (required) | Optional publisher Profile resolved before this Tailoring. | [/properties/tailoring/properties/profile](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/profile) |
| `extends` | null, string | 1..1 (required) | Optional parent Tailoring identity/path; cycles are semantically invalid. | [/properties/tailoring/properties/extends](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/extends) |
| `enabled_rules` | array | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/enabled_rules](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/enabled_rules) |
| `disabled_rules` | array | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/disabled_rules](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/disabled_rules) |
| `group_operations` | array | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/group_operations](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/group_operations) |
| `check_selectors` | object | 1..1 (required) | Rule ID to published Assessment/check selector. | [/properties/tailoring/properties/check_selectors](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/check_selectors) |
| `provenance` | object | 1..1 (required) | Source and collection context for this evidence. | [/properties/tailoring/properties/provenance](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance) |

## `/properties/tailoring/properties/benchmark`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/benchmark/properties/id](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/benchmark/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/benchmark/properties/version](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/benchmark/properties/version) |

## `/properties/tailoring/properties/group_operations/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `group` | string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/group_operations/items/properties/group](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/group_operations/items/properties/group) |
| `selected` | boolean | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/group_operations/items/properties/selected](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/group_operations/items/properties/selected) |
| `justification` | null, string | 0..1 | **Unresolved description** | [/properties/tailoring/properties/group_operations/items/properties/justification](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/group_operations/items/properties/justification) |

## `/properties/tailoring/properties/provenance`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organization` | null, object, string | 1..1 (required) | Organization associated with this declaration. | [/properties/tailoring/properties/provenance/properties/organization](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/organization) |
| `created_by` | null, object, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/provenance/properties/created_by](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/created_by) |
| `created_at` | null, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/provenance/properties/created_at](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/created_at) |
| `modified_by` | null, object, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/provenance/properties/modified_by](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/modified_by) |
| `modified_at` | null, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/provenance/properties/modified_at](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/modified_at) |
| `authorized_by` | null, object, string | 1..1 (required) | Identity recorded as authorizing the action. | [/properties/tailoring/properties/provenance/properties/authorized_by](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/authorized_by) |
| `authorized_at` | null, string | 1..1 (required) | Timestamp recorded for the authorization. | [/properties/tailoring/properties/provenance/properties/authorized_at](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/authorized_at) |
| `authorization_reference` | null, string | 1..1 (required) | Reference documenting the authorization. | [/properties/tailoring/properties/provenance/properties/authorization_reference](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/authorization_reference) |
| `authorization_status` | null, string | 1..1 (required) | **Unresolved description** | [/properties/tailoring/properties/provenance/properties/authorization_status](../../../proposed-schema/documentation/tailoring.schema.json#/properties/tailoring/properties/provenance/properties/authorization_status) |

## Advanced constraints

[Local constraints](../advanced/tailoring.md) and [complete JSON Schema](../../../proposed-schema/documentation/tailoring.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
