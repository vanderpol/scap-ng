# esx.host_service

Proposed documentation; frozen 0.4.1 validation is unchanged.

Inspect service configuration and state on an ESXi host.

This retained experimental mapping comes from the separate pinned 6.0 new-Test source; it has no corresponding 5.12.3 declaration. Its source contracts remain in the engineering ledger.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/esx.host_service.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/object/properties/filters) |
| `service_name` | string | 0..1 | Host service name. | [/$defs/object/properties/service_name](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/object/properties/service_name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `service_name` | string | 0..1 | Host service name. | [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_name) |
| `service_label` | string | 0..1 | Descriptive information regarding the service. | [/$defs/meanings/properties/service_label](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_label) |
| `service_policy` | string | 0..1 | The activation policy for the host service. | [/$defs/meanings/properties/service_policy](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_policy) |
| `service_running` | boolean | 0..1 | True if the service is currently running; false otherwise. | [/$defs/meanings/properties/service_running](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_running) |
| `service_required` | boolean | 0..1 | True if the service is required to be running on the host; false otherwise. | [/$defs/meanings/properties/service_required](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_required) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/esx.host_service.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 6.0 new tests only, commit `5afcf590fb5d334687bfdc47f98716424cdb7f3d`, `esx-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **experimental**.
