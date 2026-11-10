# windows.user_sid — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user_sid) | {} | source-derived |

[/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user_sid): SID of a particular user.

A string the represents the SID of a particular user.

`user_sid` holds a string that represents the SID of a particular user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/enabled) | {} | source-derived |

[/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/enabled): This field holds a boolean value that specifies whether the particular user account is enabled or not.

A boolean that represents whether the particular user is enabled or not.

This element holds a boolean value that specifies whether the particular user account is enabled or not.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group_sid) | {} | source-derived |

[/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group_sid): A string the represents the SID of a particular group.

A string that represents the SID of a particular group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/last_logon](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/last_logon) | {} | source-derived |
| [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user) | {} | source-derived |

[/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user): A string the represents the name of a particular user.

In Windows, user names are case-insensitive.

For local users use: "computer_name\user_name".

For built-in accounts on the system, use the user name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group) | {} | source-derived |

[/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group): A string that represents the name of a particular group.

In Windows, group names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

For local groups use: "computer name\group name".

For built-in accounts on the system, use the group name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/full_name](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/full_name) | {} | source-derived |
| [/$defs/meanings/properties/comment](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/comment) | {} | source-derived |
| [/$defs/meanings/properties/password_age_days](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/password_age_days) | {} | source-derived |

[/$defs/meanings/properties/password_age_days](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/password_age_days): The number of full days that have elapsed since the password was last changed.

The number of days that have elapsed since the password was last changed.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object/properties/user_sid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
