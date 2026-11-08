# linux.apparmorstatus

Proposed documentation; frozen 0.4.0 validation is unchanged.

The AppArmor Status Test is used to check properties representing the counts of profiles and processes as per the results of the "apparmor_status" or "aa-status" command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.apparmorstatus.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by an apparmorstatus test to define the different information about the current AppArmor polciy.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The AppArmor Status Item displays various information about the current AppArmor policy.

This item maps the counts of profiles and processes as per the results of the "apparmor_status" or "aa-status" command.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `loaded_profiles_count` | integer | 0..1 | Displays the number of loaded profiles | [/$defs/meanings/properties/loaded_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/loaded_profiles_count) |
| `enforce_mode_profiles_count` | integer | 0..1 | Displays the number of profiles in enforce mode | [/$defs/meanings/properties/enforce_mode_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/enforce_mode_profiles_count) |
| `complain_mode_profiles_count` | integer | 0..1 | Displays the number of profiles in complain mode | [/$defs/meanings/properties/complain_mode_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/complain_mode_profiles_count) |
| `processes_with_profiles_count` | integer | 0..1 | Displays the number of processes which have profiles defined | [/$defs/meanings/properties/processes_with_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/processes_with_profiles_count) |
| `enforce_mode_processes_count` | integer | 0..1 | Displays the number of processes in enforce mode | [/$defs/meanings/properties/enforce_mode_processes_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/enforce_mode_processes_count) |
| `complain_mode_processes_count` | integer | 0..1 | Displays the number of processes in complain mode | [/$defs/meanings/properties/complain_mode_processes_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/complain_mode_processes_count) |
| `unconfined_processes_with_profiles_count` | integer | 0..1 | Displays the number of processes which are unconfined but have a profile defined | [/$defs/meanings/properties/unconfined_processes_with_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/unconfined_processes_with_profiles_count) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.apparmorstatus.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
