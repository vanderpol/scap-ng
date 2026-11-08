# windows.wuaupdatesearcher — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/search_criteria) | {} | source-derived |
| [/$defs/meanings/properties/update_id](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/update_id) | {} | source-derived |
| [/$defs/meanings/properties/title](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/title) | {} | source-derived |
| [/$defs/meanings/properties/support_url](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/support_url) | {} | source-derived |
| [/$defs/meanings/properties/is_installed](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_installed) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/is_hidden](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_hidden) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/msrc_severity](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/msrc_severity) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/last_deployment_change_time](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/last_deployment_change_time) | {} | source-derived |
| [/$defs/meanings/properties/source](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/source) | {"declared_values_not_new_validation_restrictions": ["Windows_Update", "WSUS", "Offline_Cab_File"]} | source-derived |
| [/$defs/meanings/properties/days_since_source_modified](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/days_since_source_modified) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/search_criteria) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/include_superseded_updates](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/include_superseded_updates) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
