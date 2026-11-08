# unix.sysctl — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/meanings/properties/name): Kernel parameter name.

`name` contains a string that represents the name of a kernel parameter that was collected from the local system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/meanings/properties/value) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/meanings/properties/value): Value of the kernel parameter.

`value` contains a string that represents the current value(s) for the specified kernel parameter on the local system.

`value` contains a string that represents the value(s) associated with the specified kernel parameter.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.sysctl.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
