# linux.selinuxboolean — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/name) | {} | source-derived |
| [/$defs/meanings/properties/current_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/current_status) | {} | source-derived |

[/$defs/meanings/properties/current_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/current_status): Current state of the specified SELinux boolean.

`current_status` indicates current state of the specified SELinux boolean.

`current_status` represents the current state of the specified SELinux boolean.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pending_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/pending_status) | {} | source-derived |

[/$defs/meanings/properties/pending_status](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/meanings/properties/pending_status): Pending state of the specified SELinux boolean.

`pending_status` indicates the pending state of the specified SELinux boolean.

`pending_status` represents the pending state of the specified SELinux boolean.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_selinuxboolean_object/oneOf/1/properties/name", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.selinuxboolean.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
