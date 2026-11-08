# panos.version — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/major_version) | {} | source-derived |
| [/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/minor_version) | {} | source-derived |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/release) | {} | source-derived |
| [/$defs/meanings/properties/hotfix](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/hotfix) | {} | source-derived |
| [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/version_string) | {} | source-derived |
| [/$defs/meanings/properties/model_name](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/model_name) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
