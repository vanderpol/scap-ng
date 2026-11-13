# ios.section

Proposed documentation; frozen 0.4.1 validation is unchanged.

The section test is used to check the properties of specific output lines from a configuration section.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/ios.section.md) retain the validated encodings and any broader schema acceptance.

## Object

A section object consists of a section_command field that is the name of a section command to be tested.

The Object is used by a section test to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object/properties/filters) |
| `section_command` | string | 0..1 | The name of a section command. | [/$defs/object/properties/section_command](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object/properties/section_command) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores command that are part of a IOS configuration section.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `section_command` | string | 0..1 | The name of the section command. | [/$defs/meanings/properties/section_command](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/section_command) |
| `section_config_lines` | string | 0..1 | The value returned with all config lines of the section. | [/$defs/meanings/properties/section_config_lines](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/section_config_lines) |
| `config_line` | string | 0..1 | The value returned with one config line of the section at a time. | [/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/config_line) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the name of ths section_command and the corresponding config lines.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/ios.section.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/ios.section.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `ios-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
