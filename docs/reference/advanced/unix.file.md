# unix.file — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/full_path) | {} | editorially-approved |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/full_path): Full path of the collected entry.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/directory) | {} | editorially-approved |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/directory): Directory component of the collected path.

`directory` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/name) | {} | editorially-approved |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/name): Entry name without the directory.

The name of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/type) | {} | editorially-approved |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/type): Kind of filesystem entry.

This is the file's type: regular file (regular), directory, named pipe (fifo), symbolic link, socket or block special.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/owner_gid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_gid) | {} | editorially-approved |

[/$defs/meanings/properties/owner_gid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_gid): Numeric group ID of the owning group.

This is the group owner of the file, by group number.

`owner_gid` represents the group owner of a file, by group number.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/owner_uid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_uid) | {} | editorially-approved |

[/$defs/meanings/properties/owner_uid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_uid): Numeric user ID of the owner.

The numeric user id, or uid, is the third column of each user's entry in /etc/passwd.

This element represents the owner of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/access_time) | {} | editorially-approved |
| [/$defs/meanings/properties/change_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/change_time) | {} | editorially-approved |

[/$defs/meanings/properties/change_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/change_time): Last inode-status change, not creation time.

An inode is a Unix data structure that stores all of the information about a particular file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/modify_time) | {} | editorially-approved |
| [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/size) | {} | editorially-approved |
| [/$defs/meanings/properties/setuid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setuid) | {} | editorially-approved |

[/$defs/meanings/properties/setuid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setuid): Set-user-ID permission flag.

Does the program run with the uid (thus privileges) of the file's owner, rather than the calling user?

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/setgid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setgid) | {} | editorially-approved |

[/$defs/meanings/properties/setgid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setgid): Set-group-ID permission flag.

Does the program run with the gid (thus privileges) of the file's group owner, rather than the calling user's group?

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/sticky](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/sticky) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_read) | {} | editorially-approved |

[/$defs/meanings/properties/owner_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_read): Whether the owner-read permission bit is set.

Permission flags are bits, not an effective-access guarantee; directory-specific read/write/search interpretation remains unspecified.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/owner_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_write) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/group_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_read) | {} | editorially-approved |
| [/$defs/meanings/properties/group_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_write) | {} | editorially-approved |
| [/$defs/meanings/properties/group_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/other_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_read) | {} | editorially-approved |
| [/$defs/meanings/properties/other_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_write) | {} | editorially-approved |
| [/$defs/meanings/properties/other_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/has_extended_acl](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/has_extended_acl) | {} | editorially-approved |

[/$defs/meanings/properties/has_extended_acl](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/has_extended_acl): Whether ACL permissions differ from standard UNIX permissions.

Does the file or directory have ACL permissions applied to it?

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object): A file object defines the path and filename of the file(s).

In addition, a number of behaviors may be provided that help guide the collection of objects.

The Object is used by a file test to define the specific file(s) to be evaluated.

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filepath", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/path", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filename) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filename", "type_alternatives": ["null", "object"]} | source-derived |

[/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filename): Name of a file to evaluate.

`filename` specifies the name of a file to evaluate.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/traversal", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/item): The file item holds information about the individual files found on a system.

Each file item contains path and filename information as well as its type, associated user and group ids, relevant dates, and the privileges granted.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/require): The comparison fields define the different metadata associated with a UNIX file.

This includes the path, filename, type, group id, user id, size, etc.

In addition, the permission associated with the file are also included.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
