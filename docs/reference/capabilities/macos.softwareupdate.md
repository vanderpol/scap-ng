# macos.softwareupdate

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `macos.softwareupdate` is used to check the status of automatic software updates on MacOSX.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.softwareupdate.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is a singleton used to access automatic software update information.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item represents automatic software update information.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `schedule` | boolean | 0..1 | Whether automatic checking is enabled (true). | [/$defs/meanings/properties/schedule](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/schedule) |
| `software_title` | string | 0..1 | The title string for an available (not installed) software update. | [/$defs/meanings/properties/software_title](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/software_title) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields makes it possible to make assertions about the state of automatic software updates.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.softwareupdate.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
