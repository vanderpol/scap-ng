# windows.regkeyeffectiverights — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/hive) | {"declared_values_not_new_validation_restrictions": ["classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"]} | source-derived |

[/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/hive): The hive of a registry key on the machine from which to retrieve the SACL.

The hive that the registry key belongs to.

This element specifies the hive of a registry key on the machine from which to retrieve the SACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key) | {} | source-derived |

[/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key): A registry key on the machine from which to retrieve the SACL.

This element describes a registry key to be gathered.

This element specifies a registry key on the machine from which to retrieve the SACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) | {} | source-derived |

[/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid): Unique SID that associated a user, group, system, or program (such as a Windows service).

`trustee_sid` specifies the SID that associated a user, group, system, or program (such as a Windows service).

`trustee_sid` is the unique SID that associated a user, group, system, or program (such as a Windows service).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) | {} | source-derived |

[/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_name): The trustee name associated with this particular DACL.

This element specifies the trustee name associated with this particular DACL.

In Windows, trustee names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

For local trustee names use: "computer name\trustee name".

For built-in accounts on the system, use the trustee name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) | {} | source-derived |
| [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) | {} | source-derived |

[/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control): The right to read the information in the object's Security Descriptor, not including the information in the SACL.

The right to read the information in the object's security descriptor, not including the information in the SACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) | {} | source-derived |

[/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac): The right to modify the DACL in the object's Security Descriptor.

The right to modify the DACL in the object's security descriptor.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) | {} | source-derived |

[/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner): The right to change the owner in the object's Security Descriptor.

The right to change the owner in the object's security descriptor.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) | {} | source-derived |
| [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_read) | {} | source-derived |
| [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_write) | {} | source-derived |
| [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) | {} | source-derived |
| [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_all) | {} | source-derived |
| [/$defs/meanings/properties/key_query_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_query_value) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_set_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_set_value) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_create_sub_key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_sub_key) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_enumerate_sub_keys](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_enumerate_sub_keys) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_notify](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_notify) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_create_link](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_link) | {} | native-name-proposal |
| [/$defs/meanings/properties/key_wow64_64key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_64key) | {} | unresolved |
| [/$defs/meanings/properties/key_wow64_32key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_32key) | {} | unresolved |
| [/$defs/meanings/properties/key_wow64_res](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_res) | {} | unresolved |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object): The Object is used by a registry key effective rights test to define the objects used to evalutate against the specified state.

An Object is defined as a combination of a Windows registry and trustee SID.

The key field represents the registry key to be evaluated while the trustee SID represents the account (SID) to check effective rights of.

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/hive) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/hive", "type_alternatives": ["object"], "declared_values_not_new_validation_restrictions": ["classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"]} | source-derived |

[/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/hive): The hive that the registry key belongs to.

This is restricted to a specific set of values: HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_CURRENT_USER_LOCAL_SETTINGS,HKEY_LOCAL_MACHINE, and HKEY_USERS.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/key) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/key", "type_alternatives": ["null", "object"]} | source-derived |

[/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/key): Registry key to be collected.

`key` describes a registry key to be collected.

A .* pattern match says to collect every key under a given hive.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/trustee_sid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/properties/trustee_sid", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/trustee_sid): Unique SID associated with a user, group, system, or program (such as a Windows service).

`trustee_sid` identifies a unique SID associated with a user, group, system, or program (such as a Windows service).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1/additionalProperties", "type_alternatives": []} | semantic-hold |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/item): This item stores the effective rights of a registry key that a discretionary access control list (DACL) structure grants to a specified trustee.

The trustee's effective rights are determined checking all access-allowed and access-denied access control entries (ACEs) in the DACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
