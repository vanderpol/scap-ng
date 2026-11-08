# iosxe.section — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/section_command](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/meanings/properties/section_command) | {} | source-derived |
| [/$defs/meanings/properties/section_config_lines](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/meanings/properties/section_config_lines) | {} | source-derived |
| [/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/meanings/properties/config_line) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/section_command](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/object/properties/section_command) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.section.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
