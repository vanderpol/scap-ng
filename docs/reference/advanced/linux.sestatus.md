# linux.sestatus — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/selinux_status](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/selinux_status) | {} | source-derived |
| [/$defs/meanings/properties/current_mode](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/current_mode) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/mode_from_config_file](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/mode_from_config_file) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/loaded_policy_name](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/loaded_policy_name) | {} | source-derived |
| [/$defs/meanings/properties/policy_from_config_file](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/meanings/properties/policy_from_config_file) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.sestatus.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
