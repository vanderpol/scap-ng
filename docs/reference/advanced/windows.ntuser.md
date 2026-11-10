# windows.ntuser — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/key) | {} | source-derived |

[/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/key): A registry key normally found in the HKCU hive to be tested.

This element describes a registry key normally found in the HKCU hive to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/name): The name of a value of a registry key.

This element describes the name of a registry key.

This element describes the name of a value of a registry key.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/sid](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/sid) | {} | source-derived |

[/$defs/meanings/properties/sid](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/sid): This field holds a string that represents the SID of a particular user.

This element holds a string that represents the SID of a particular user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/username) | {} | source-derived |

[/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/username): Name of a particular user.

`username` holds a string that represents the name of a particular user.

In Windows, user names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

For local users use: "computer name\user name".

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/account_type](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/account_type) | {"declared_values_not_new_validation_restrictions": ["local", "domain"]} | source-derived |
| [/$defs/meanings/properties/logged_on](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/logged_on) | {} | source-derived |

[/$defs/meanings/properties/logged_on](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/logged_on): If the user account is currently logged on to the computer.

HKEY_USERS: Contains all the actively loaded user profiles on the computer. https://learn.microsoft.com/en-us/troubleshoot/windows-server/performance/windows-registry-advanced-users

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/days_since_last_logon](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/days_since_last_logon) | {} | unresolved |
| [/$defs/meanings/properties/user_has_signed_into_explorer](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/user_has_signed_into_explorer) | {} | source-derived |

[/$defs/meanings/properties/user_has_signed_into_explorer](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/user_has_signed_into_explorer): If the user account has ever executed explorer.exe.

This is a practical indicator of accounts using interactive (desktop/GUI) sessions and is not set by non-interactive logon methods such as WinRM or SSH.

Content authors may use this element to exclude non-interactive users from user policy checks.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/enabled) | {} | source-derived |
| [/$defs/meanings/properties/date_modified](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/date_modified) | {} | source-derived |
| [/$defs/meanings/properties/days_since_modified](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/days_since_modified) | {} | source-derived |
| [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/filepath) | {} | source-derived |

[/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/filepath): The filepath of the ntuser.dat file.

This element describes the filepath of the ntuser.dat file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/last_write_time) | {} | source-derived |

[/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/last_write_time): The last time that the key or any of its value entries was modified.

See the RegQueryInfoKey function lpftLastWriteTime.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/type) | {"declared_values_not_new_validation_restrictions": ["binary", "dword", "dword_big_endian", "expand_string", "link", "multi_string", "none", "qword", "string", "resource_list", "full_resource_descriptor", "resource_requirements_list", ""]} | source-derived |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/type): The type field allows a test to be written against the registy type associated with the specified registry key(s).

Specifies the type of data stored by the registry key.

`type` allows a test to be written against the registy type associated with the specified registry key(s).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/value) | {} | source-derived |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/value): The value field allows a test to be written against the value held within the specified registry key(s).

`value` holds the actual value of the specified registry key.

The representation of the value as well as the associated datatype attribute depends on type of data stored in the registry key.

`value` allows a test to be written against the value held within the specified registry key(s).

This allows tools performing the evaluation to know how to perform less than and greater than operations correctly.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/key) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/key", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/key): Registry key to be collected.

`key` describes a registry key to be collected.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/name", "type_alternatives": ["null", "object"]} | source-derived |

[/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/name): Name assigned to a value associated with a specific registry key.

`name` describes the name assigned to a value associated with a specific registry key.

A .* pattern match says to collect every name under a given hive/key.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/include_default](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/include_default) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/include_default", "type_alternatives": ["boolean"], "declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/item_creation) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/properties/item_creation", "type_alternatives": ["string"], "literal_alternatives_in_referenced_shape": ["every_ntuser", "key_and_name_exist"], "declaration_only": {"type": "string", "required": true, "enum": ["key_and_name_exist", "every_ntuser"]}} | native-mapping-reviewed |

[/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/item_creation): Controls whether Items are created only for matching key/name pairs or for every relevant ntuser.dat.

For 'every_ntuser', items are created for each relavent ntuser.dat found on the system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1/additionalProperties", "type_alternatives": []} | semantic-hold |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/item): ii.

Exclude profiles for Per-Service SIDs by excluding subkeys in the format of S-1-5-80-<number*gt;-<number*gt;-<number*gt;-<number*gt;-<number*gt;

a.

Obtain a list of User Profiles from the following registry key, where each subkey is a profile that may be included in scope for this test

iii.

Include Local and Domain User SIDs by including subkeys match the format of S-1-5-21-<number*gt;-<number*gt;-<number*gt;-<number*gt;

HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\WindowsNT\CurrentVersion\ProfileList

c.

Obtain ntuser filepath from the ProfileImagePath value of 'human' profiles

Exclude profiles for LocalService, Network service etc.. by excluding subkeys in the format of S-1-5-<number*gt;

b.

Determine which user profiles are from ‘human’ users

1.

Finding Human User Profiles

2.

Gathering per user registry key data

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/require): The comparison fields define the different metadata associated with a ntuser.dat file.

This includes the key, name, type, and value.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
