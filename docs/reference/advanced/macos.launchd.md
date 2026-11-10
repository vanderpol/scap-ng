# macos.launchd — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/label](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/meanings/properties/label) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |
| [/$defs/meanings/properties/status](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/meanings/properties/status) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/label](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/object/properties/label) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.launchd.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
