# unix.password — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/username) | {} | source-derived |

[/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/username): The UNIX account name.

This is the name of the user for which data was gathered.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/password) | {} | source-derived |

[/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/password): The encrypted version of the user's password.

This is the encrypted version of the user's password.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/user_id) | {} | source-derived |
| [/$defs/meanings/properties/group_id](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/group_id) | {} | source-derived |
| [/$defs/meanings/properties/gcos](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/gcos) | {} | source-derived |
| [/$defs/meanings/properties/home_dir](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/home_dir) | {} | source-derived |
| [/$defs/meanings/properties/login_shell](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/login_shell) | {} | source-derived |
| [/$defs/meanings/properties/last_login](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/last_login) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object): The Object is used by a password test to define the object to be evaluated.

A password object consists of a single username field that identifies the user(s) whose password is to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object/properties/username) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1/properties/username", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/item): /etc/passwd.

See passwd(4).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
