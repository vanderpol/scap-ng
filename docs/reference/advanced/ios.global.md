# ios.global — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/global_command](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/meanings/properties/global_command) | {} | source-derived |

[/$defs/meanings/properties/global_command](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/meanings/properties/global_command): Specific line in the ios config file under the global context.

`global_command` identifies a specific line in the ios config file under the global context.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/object): The Object is used by a global test to define the object to be evaluated.

For the most part this object checks for existence and is used without a state comparision.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/global_command](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/object/properties/global_command) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.global.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
