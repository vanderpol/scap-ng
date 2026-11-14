# asa.line

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `asa.line` is used to check the properties of specific output lines from a SHOW command, such as SHOW RUNNING-CONFIG.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/asa.line.md) retain the validated encodings and any broader schema acceptance.

## Object

A line object consists of a show_subcommand field that is the name of a SHOW sub-command to be tested.

The Object is used by `asa.line` to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/asa.line.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/asa.line.schema.json#/$defs/object/properties/filters) |
| `show_subcommand` | string | 0..1 | The name of a SHOW sub-command. | [/$defs/object/properties/show_subcommand](../../../proposed-schema/documentation/capabilities/asa.line.schema.json#/$defs/object/properties/show_subcommand) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores the configuration information associated with the evaluation of a SHOW sub-command on Cisco ASA.

This includes the name of ths sub-command and the corresponding config line.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `show_subcommand` | string | 0..1 | The name of the SHOW sub-command. | [/$defs/meanings/properties/show_subcommand](../../../proposed-schema/documentation/capabilities/asa.line.schema.json#/$defs/meanings/properties/show_subcommand) |
| `config_line` | string | 0..1 | The value returned by the specified SHOW sub-command. | [/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/asa.line.schema.json#/$defs/meanings/properties/config_line) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/asa.line.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/asa.line.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `asa-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
