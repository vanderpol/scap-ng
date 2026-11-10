# iosxe.line — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/show_subcommand](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/meanings/properties/show_subcommand) | {} | source-derived |
| [/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/meanings/properties/config_line) | {} | source-derived |

[/$defs/meanings/properties/config_line](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/meanings/properties/config_line): The value returned by the specified SHOW sub-command.

The value returned from by the specified SHOW sub-command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/object): A line object consists of a show_subcommand field that is the name of a SHOW sub-command to be tested.

The Object is used by a line test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/show_subcommand](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/object/properties/show_subcommand) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.line.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
