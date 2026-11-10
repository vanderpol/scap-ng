# macos.softwareupdate — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/schedule](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/schedule) | {} | source-derived |

[/$defs/meanings/properties/schedule](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/schedule): Whether automatic checking is enabled (true).

Specifies whether automatic checking is enabled (true).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/software_title](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/software_title) | {} | source-derived |

[/$defs/meanings/properties/software_title](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/meanings/properties/software_title): The title string for an available (not installed) software update.

Specifies the title string for an available (not installed) software update.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.softwareupdate.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
