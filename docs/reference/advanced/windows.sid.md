# windows.sid — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_name) | {} | source-derived |
| [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_sid) | {} | source-derived |
| [/$defs/meanings/properties/trustee_domain](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_domain) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/trustee_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/include_group](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/include_group) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/object/properties/resolve_group](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/resolve_group) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
