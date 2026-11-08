# ios.section — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/section_command](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/section_command) | {} | source-derived |
| [/$defs/meanings/properties/section_config_lines](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/section_config_lines) | {} | source-derived |

[/$defs/meanings/properties/section_config_lines](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/section_config_lines): The value returned with all config lines of the section.

Element with all config lines of the section.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/config_line) | {} | source-derived |

[/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/meanings/properties/config_line): The value returned with one config line of the section at a time.

Element with one config line of the section at a time.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object): A section object consists of a section_command field that is the name of a section command to be tested.

The Object is used by a section test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/section_command](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/object/properties/section_command) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.section.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
