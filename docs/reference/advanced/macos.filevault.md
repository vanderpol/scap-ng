# macos.filevault — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/status](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#/$defs/meanings/properties/status) | {"declared_values_not_new_validation_restrictions": ["enabled", "disabled", "encrypting"]} | source-derived |

[/$defs/meanings/properties/status](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#/$defs/meanings/properties/status): File Vault status of the machine.

`status` contains the File Vault status on the machine.

`status` describes the File Vault status of the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.filevault.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
