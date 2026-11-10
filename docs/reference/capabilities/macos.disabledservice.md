# macos.disabledservice

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `macos.disabledservice` is used to check the status of daemons/agents disabled via the launchd service, via the command 'launchctl print-disabled system'.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.disabledservice.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `macos.disabledservice` to define the service domain to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking a launchd domain for disabled services.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `label` | string | 0..1 | The name of the service disabled in the domain. | [/$defs/meanings/properties/label](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/label) |
| `disabled` | boolean | 0..1 | The actual status of the service as indicated by the output of the 'launchctl print-disabled <domain>' command. | [/$defs/meanings/properties/disabled](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/disabled) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define a value used to evaluate the result of a specific Object item.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.disabledservice.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
