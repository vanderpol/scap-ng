# windows.group_sid — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group_sid) | {} | source-derived |

[/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group_sid): SID of a particular group.

A string the represents the SID of a particular group.

`group_sid` holds a string that represents the SID of a particular group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user_sid) | {} | source-derived |

[/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user_sid): SID of a particular user.

A string that represents the SID of a particular user.

`user_sid` holds a string that represents the SID of a particular user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/subgroup_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup_sid) | {} | source-derived |

[/$defs/meanings/properties/subgroup_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup_sid): SID of particular subgroup in the specified group.

A string that represents the SID of a particular subgroup.

`subgroup_sid` holds a string that represents the SID of particular subgroup in the specified group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group) | {} | source-derived |

[/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/group): A string the represents the name of a particular group.

For local groups use: "computer name\group name".

For built-in accounts on the system, use the group name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user) | {} | source-derived |

[/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/user): A string that represents the name of a particular user.

In Windows, user names are case-insensitive.

For local users use: "computer name\user name".

For built-in accounts on the system, use the user name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/subgroup](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup) | {} | source-derived |

[/$defs/meanings/properties/subgroup](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/meanings/properties/subgroup): A string that represents the name of a particular subgroup in the specified group.

In Windows, group names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/object/properties/group_sid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.group_sid.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
