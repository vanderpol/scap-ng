# unix.shadow — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#): The shadow test is used to check information from the /etc/shadow file for a specific user.

This file contains a user's password, but also their password aging and lockout information.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/username) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/username): UNIX account name.

This is the name of the user for which data was gathered.

This is the name of the user being checked.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/password) | {} | source-derived |

[/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/password): The encrypted version of the user's password.

This is the encrypted version of the user's password.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/chg_lst](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_lst) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/chg_allow](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_allow) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/chg_allow](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_allow): Minimum interval between password changes.

This specifies how often in days a user may change their password.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/chg_req](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_req) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/exp_warn](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_warn) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/exp_warn](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_warn): Warning interval before password expiration.

This describes how long before password expiration the system begins warning the user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/exp_inact](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_inact) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/exp_inact](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_inact): Inactivity interval after password expiration.

How soon before the expiration the user receives these warnings is specified in exp_warn.

The exp_inact parameter gives the sysadmin flexibility so that a user who reaches the end of their expiration time gains exp_inact more days to login and change their password manually.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/exp_date](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_date) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/flag) | {} | source-derived |

[/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/flag): A numeric reserved field that the shadow file may use in the future.

This is a numeric reserved field that the shadow file may use in the future.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/encrypt_method](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/encrypt_method) | {"declared_values_not_new_validation_restrictions": ["DES", "BSDi", "MD5", "Blowfish", "Sun MD5", "SHA-256", "SHA-512"]} | source-derived |

[/$defs/meanings/properties/encrypt_method](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/encrypt_method): Method that is used for hashing passwords.

`encrypt_method` describes method that is used for hashing passwords.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object): The Object is used by a shadow test to define the shadow file to be evaluated.

A shdow object consists of a single user field that identifies the username associted with the shadow file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/username) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/username", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/item): /etc/shadow.

See shadow(4).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
