# windows.wmi.query — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/namespace](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/namespace) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/query](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/query) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/result) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/namespace](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object/properties/namespace) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/query](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object/properties/query) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
