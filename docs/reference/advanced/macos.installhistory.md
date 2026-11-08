# macos.installhistory — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/install_version](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_version) | {} | source-derived |
| [/$defs/meanings/properties/install_date](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_date) | {} | source-derived |
| [/$defs/meanings/properties/package_source](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/package_source) | {"declared_values_not_new_validation_restrictions": ["Apple", "AppStore", "ThirdParty"]} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
