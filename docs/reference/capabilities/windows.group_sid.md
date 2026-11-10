# windows.group_sid

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.group_sid` allows the different users and subgroups, that directly belong to specific groups (identified by SID), to be tested.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.group_sid.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/object/properties/filters) |
| `group_sid` | string | 0..1 | SID of a particular group. | [/$defs/object/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/object/properties/group_sid) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Windows Item allows the different users and subgroups, that directly belong to specific groups (identified by SID), to be collected.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `group_sid` | string | 0..1 | SID of a particular group. | [/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group_sid) |
| `user_sid` | string | 0..1 | SID of a particular user. | [/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user_sid) |
| `subgroup_sid` | string | 0..1 | SID of particular subgroup in the specified group. | [/$defs/meanings/properties/subgroup_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup_sid) |
| `group` | string | 0..1 | A string the represents the name of a particular group. | [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group) |
| `user` | string | 0..1 | A string that represents the name of a particular user. | [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user) |
| `subgroup` | string | 0..1 | A string that represents the name of a particular subgroup in the specified group. | [/$defs/meanings/properties/subgroup](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.group_sid.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
