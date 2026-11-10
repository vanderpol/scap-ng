# macos.gatekeeper

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `macos.gatekeeper` is used to check the status of Gatekeeper and any unsigned applications that have been granted execute permission.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.gatekeeper.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is a singleton used to access information about Gatekeeper.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking the settings of the Gatekeeper.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `enabled` | boolean | 0..1 | The status of Gatekeeper assessments. | [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json#/$defs/meanings/properties/enabled) |
| `require_developer_id` | boolean | 0..1 | The status of Gatekeeper enforcement of app developer id. | [/$defs/meanings/properties/require_developer_id](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json#/$defs/meanings/properties/require_developer_id) |
| `unlabeled` | string | 0..1 | The path to an unsigned application folder to which Gatekeeper has granted execute permission. | [/$defs/meanings/properties/unlabeled](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json#/$defs/meanings/properties/unlabeled) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields makes it possible to make assertions about Gatekeeper's operational status and unsigned applications that have been granted execute permission.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.gatekeeper.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.gatekeeper.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
