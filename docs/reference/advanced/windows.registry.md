# windows.registry — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/hive) | {"declared_values_not_new_validation_restrictions": ["classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"]} | native-mapping-reviewed |

[/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/hive): Registry hive containing the key.

The hive that the registry key belongs to.

This is restricted to a specific set of values: HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_CURRENT_USER_LOCAL_SETTINGS, HKEY_LOCAL_MACHINE, and HKEY_USERS.

This is restricted to a specific set of values: HKEY_CLASSES_ROOT, HKEY_CURRENT_CONFIG, HKEY_CURRENT_USER, HKEY_CURRENT_USER_LOCAL_SETTINGS,HKEY_LOCAL_MACHINE, and HKEY_USERS.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/key) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/key): Key path relative to the hive.

This element describes a registry key to be gathered.

`key` describes a registry key to be collected.

A .* pattern match says to collect every key under a given hive.

This element describes a registry key to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/name) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/name): Registry value name.

This element describes the name of a registry key.

`name` describes the name assigned to a value associated with a specific registry key.

A .* pattern match says to collect every name under a given hive/key.

This element describes the name of a value of a registry key.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/last_write_time) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/last_write_time): Last recorded write time for the key.

The last time that the key or any of its value entries were modified.

See the RegQueryInfoKey function lpftLastWriteTime.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/type) | {"declared_values_not_new_validation_restrictions": ["binary", "dword", "dword_big_endian", "expand_string", "link", "multi_string", "none", "qword", "string", "resource_list", "full_resource_descriptor", "resource_requirements_list"]} | native-mapping-reviewed |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/type): Native registry value kind.

Specifies the type of data stored by the registry key.

`type` allows a test to be written against the registy type associated with the specified registry key(s).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/value) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/value): Data stored in the registry value.

`value` holds the actual value of the specified registry key.

The representation of the value as well as the associated datatype attribute depends on type of data stored in the registry key.

DWORD and QWORD values represnt unsigned 32-bit and 64-bit integers, respectively.

`value` allows a test to be written against the value held within the specified registry key(s).

This allows tools performing the evaluation to know how to perform less than and greater than operations correctly.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/expanded_value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/expanded_value) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/expanded_value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/expanded_value): Registry string after environment-variable expansion.

For registry values of type REG_EXPAND_SZ, this field contains the expanded value.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/hive) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/hive", "type_alternatives": ["object"], "declared_values_not_new_validation_restrictions": ["classes_root", "current_config", "current_user", "current_user_local_settings", "local_machine", "users"]} | native-mapping-reviewed |
| [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/key) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/key", "type_alternatives": ["null", "object"]} | native-mapping-reviewed |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/properties/name", "type_alternatives": ["null", "object"]} | native-mapping-reviewed |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1/additionalProperties", "type_alternatives": []} | semantic-hold |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/require): The comparison fields define the different metadata associated with a Windows registry key.

This includes the hive, key, name, type, and value.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
