# macos.firmwarepassword — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#/$defs/meanings/properties/enabled) | {} | source-derived |

[/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#/$defs/meanings/properties/enabled): The status field describes whether a firmware password is enabled.

The status element describes whether or not a firmware password is enabled on the machine.

The status element describes whether a firmware password is enabled.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.firmwarepassword.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
