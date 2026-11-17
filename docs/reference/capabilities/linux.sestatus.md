# linux.sestatus

Proposed documentation; frozen 0.4.1 validation is unchanged.

Inspects SELinux configuration and status fields.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.sestatus.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a sestatus test to define the different information about the current SEStatus polciy.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The SEStatus Item displays various information about the current SEStatus policy.

This item maps the counts of profiles and processes as per the results of the "sestatus" command.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `selinux_status` | string | 0..1 | Indicates whether SELinux module itself is enabled or disabled on your system. | [/$defs/meanings/properties/selinux_status](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/selinux_status) |
| `current_mode` | string | 0..1 | Current SELinux enforcement mode. | [/$defs/meanings/properties/current_mode](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/current_mode) |
| `mode_from_config_file` | string | 0..1 | SELinux enforcement mode selected in the configuration file. | [/$defs/meanings/properties/mode_from_config_file](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/mode_from_config_file) |
| `loaded_policy_name` | string | 0..1 | Displays what type of SELinux policy is currently loaded. | [/$defs/meanings/properties/loaded_policy_name](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/loaded_policy_name) |
| `policy_from_config_file` | string | 0..1 | Policy type selected in the SELinux configuration file. | [/$defs/meanings/properties/policy_from_config_file](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/policy_from_config_file) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.sestatus.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
