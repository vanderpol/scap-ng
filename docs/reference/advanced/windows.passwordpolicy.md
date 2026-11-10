# windows.passwordpolicy — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/max_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/max_passwd_age) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/max_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/max_passwd_age): Maximum password age.

Alternate Name: "Maximum password age".

A value of TIMEQ_FOREVER (max DWORD value, 4294967295) indicates that the password never expires.

The minimum valid value for this element is ONE_DAY (86400).

See the USER_MODALS_INFO_0 structure returned by a call to NetUserModalsGet().

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/min_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_age) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/min_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_age): Minimum password age.

Alternate Name: "Minimum password age".

A value of zero indicates that no delay is required between password updates.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/min_passwd_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_len) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/min_passwd_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_len): Minimum password length.

Alternate Name: "Minimum password length".

Specifies the minimum allowable password length.

Valid values for this element are zero through PWLEN.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/password_hist_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/password_hist_len) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/password_hist_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/password_hist_len): Number of previous passwords retained in password history.

Alternate Name: "Enforce password history".

Specifies the length of password history maintained.

Valid values for this element are zero through DEF_MAX_PWHIST.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/password_complexity](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/password_complexity) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/reversible_encryption](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/reversible_encryption) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/reversible_encryption](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/reversible_encryption): Whether reversible password encryption is enabled.

Alternate name: "Store passwords using reversible encryption".

Determines whether or not passwords are stored using reversible encryption.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/anonymous_name_lookup](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/anonymous_name_lookup) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/anonymous_name_lookup](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/anonymous_name_lookup): Whether anonymous SID/name translation is allowed.

Alternate name: "Allow anonymous SID/Name translation".

Determines whether or not an anonymous user may query the local LSA policy.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/object): The Object is used by a password policy test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/item): Specific policy items associated with passwords.

It is important to note that these policies are specific to certain versions of Windows.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
