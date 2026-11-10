# windows.lockoutpolicy — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/force_logoff](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/force_logoff) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/force_logoff](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/force_logoff): Delay between the end of valid logon time and forced network logoff.

A value of TIMEQ_FOREVER (max DWORD value, 4294967295) indicates that the user is never forced to log off.

See the USER_MODALS_INFO_0 structure returned by a call to NetUserModalsGet().

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/lockout_duration](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_duration) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/lockout_observation_window](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_observation_window) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/lockout_observation_window](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_observation_window): Interval over which failed logon attempts are counted.

See the USER_MODALS_INFO_3 structure returned by a call to NetUserModalsGet().

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/lockout_threshold](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_threshold) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/object): The Object is used by a lockout policy test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
