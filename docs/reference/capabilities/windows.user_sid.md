# windows.user_sid

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.user_sid` is used to check information about Windows users.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.user_sid.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object represents a set of users on a Windows system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object/properties/filters) |
| `user_sid` | string | 0..1 | SID of a particular user. | [/$defs/object/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object/properties/user_sid) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The windows Item allows the different groups (identified by SID) that a user belongs to be collected.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `user_sid` | string | 0..1 | SID of a particular user. | [/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user_sid) |
| `enabled` | boolean | 0..1 | This field holds a boolean value that specifies whether the particular user account is enabled or not. | [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/enabled) |
| `group_sid` | string | 0..1 | A string the represents the SID of a particular group. | [/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group_sid) |
| `last_logon` | integer | 0..1 | The date and time when the last logon occurred. | [/$defs/meanings/properties/last_logon](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/last_logon) |
| `user` | string | 0..1 | A string the represents the name of a particular user. | [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user) |
| `group` | string | 0..1 | A string that represents the name of a particular group. | [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group) |
| `full_name` | string | 0..1 | A string that contains the full name of the user. | [/$defs/meanings/properties/full_name](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/full_name) |
| `comment` | string | 0..1 | A string that contains a comment to associate with the user account. | [/$defs/meanings/properties/comment](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/comment) |
| `password_age_days` | integer | 0..1 | The number of full days that have elapsed since the password was last changed. | [/$defs/meanings/properties/password_age_days](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/password_age_days) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields enumerates the different groups (identified by SID) that a Windows user might belong to.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.user_sid.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
