# windows.fileeffectiverights — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/full_path): Absolute path for a file on the machine.

Specifies the absolute path to a file on the machine from which the DACL was retrieved.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/directory) | {} | source-derived |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/directory): Directory component of the absolute path to a file on the machine.

This element specifies the absolute path to a file on the machine from which the DACL was retrieved.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/name): Name of the file.

The name of the file.

The other items associated with this item would then reflect the values associated with the directory.

`name` specifies the name of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) | {} | source-derived |

[/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid): Unique SID that associated a user, group, system, or program (such as a Windows service).

`trustee_sid` specifies the SID that associated a user, group, system, or program (such as a Windows service).

`trustee_sid` is the unique SID that associated a user, group, system, or program (such as a Windows service).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) | {} | source-derived |

[/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/trustee_name): The trustee name associated with this particular DACL.

This element specifies the trustee name associated with this particular DACL.

In Windows, trustee names are case-insensitive.

As a result, it is recommended that the case-insensitive operations are used for this field.

For local trustee names use: "computer name\trustee name".

For built-in accounts on the system, use the trustee name without a domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) | {} | source-derived |
| [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) | {} | source-derived |

[/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control): The right to read the information in the object's Security Descriptor, not including the information in the SACL.

The right to read the information in the object's security descriptor, not including the information in the SACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) | {} | source-derived |

[/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac): The right to modify the DACL in the object's Security Descriptor.

The right to modify the DACL in the object's security descriptor.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) | {} | source-derived |

[/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner): The right to change the owner in the object's Security Descriptor.

The right to change the owner in the object's security descriptor.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/standard_synchronize](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_synchronize) | {} | source-derived |

[/$defs/meanings/properties/standard_synchronize](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/standard_synchronize): The right to use the object for synchronization.

This enables a thread to wait until the object is in the signaled state.

Some object types do not support this access right.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) | {} | source-derived |
| [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_read) | {} | source-derived |
| [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_write) | {} | source-derived |
| [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) | {} | source-derived |
| [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/generic_all) | {} | source-derived |
| [/$defs/meanings/properties/file_read_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_data) | {} | source-derived |

[/$defs/meanings/properties/file_read_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_data): Effective right to read data from the file, or if a directory, grants the right to list the contents of the directory.

Grants the right to read data from the file

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_write_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_data) | {} | source-derived |

[/$defs/meanings/properties/file_write_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_data): Effective right to write data to the file, or if a directory, grants the right to add a file to the directory.

Grants the right to write data to the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_append_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_append_data) | {} | source-derived |

[/$defs/meanings/properties/file_append_data](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_append_data): Effective right to append data to the file, or if a directory, grants the right to add a sub-directory to the directory.

Grants the right to append data to the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_read_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_ea) | {} | source-derived |

[/$defs/meanings/properties/file_read_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_ea): Effective right to read extended attributes.

Grants the right to read extended attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_write_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_ea) | {} | source-derived |

[/$defs/meanings/properties/file_write_ea](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_ea): Effective right to write extended attributes.

Grants the right to write extended attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_execute) | {} | source-derived |

[/$defs/meanings/properties/file_execute](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_execute): Effective right to execute a file, or if a directory, the right to traverse the directory.

Grants the right to execute a file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_delete_child](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_delete_child) | {} | source-derived |
| [/$defs/meanings/properties/file_read_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_attributes) | {} | source-derived |

[/$defs/meanings/properties/file_read_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_read_attributes): Effective right to read file, or directory, attributes.

Grants the right to read file attributes.

Grants the right to read file, or directory, attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/file_write_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_attributes) | {} | source-derived |

[/$defs/meanings/properties/file_write_attributes](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/meanings/properties/file_write_attributes): Effective right to change file, or directory, attributes.

Grants the right to change file attributes.

Grants the right to change file, or directory, attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object): The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

The Object is used by a file effective rights test to define the objects used to evalutate against the specified state.

An Object is defined as a combination of a Windows file and trustee SID.

The file represents the file to be evaluated while the trustee SID represents the account (SID) to check effective rights of.

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filepath", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filepath): Absolute path for a file on the machine.

`filepath` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/path", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/path): Directory component of the absolute path to a file on the machine.

`path` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filename) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/filename", "type_alternatives": ["null", "object"]} | source-derived |

[/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/filename): Name of a file to evaluate.

`filename` specifies the name of a file to evaluate.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/trustee_sid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/trustee_sid", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/trustee_sid): Unique SID associated with a user, group, system, or program (such as a Windows service).

`trustee_sid` identifies a unique SID associated with a user, group, system, or program (such as a Windows service).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_fileeffectiverights_object/oneOf/1/properties/traversal", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/item): This item stores the effective rights of a file that a discretionary access control list (DACL) structure grants to a specified trustee.

The trustee's effective rights are determined checking all access-allowed and access-denied access control entries (ACEs) in the DACL.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.fileeffectiverights.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
