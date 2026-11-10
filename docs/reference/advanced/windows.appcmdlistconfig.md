# windows.appcmdlistconfig — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#): The `windows.appcmdlistconfig` is one of two tests used to gather Microsoft Internet Information Server (IIS) configuration settings.

It can gather Webserver, Site, and VDir settings.

Whereas certain website (Site) and virtual directory (VDir) data gathering are found in both or either test.

Meaning to be able capture larger sets of Site or VDir data both tests may be needed to gather all data.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/identifier_type](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/meanings/properties/identifier_type) | {"declared_values_not_new_validation_restrictions": ["Site", "VDir", "Webserver"]} | source-derived |
| [/$defs/meanings/properties/identifier](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/meanings/properties/identifier) | {} | source-derived |
| [/$defs/meanings/properties/section](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/meanings/properties/section) | {} | source-derived |
| [/$defs/meanings/properties/parameter](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/meanings/properties/parameter) | {} | source-derived |
| [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/meanings/properties/result) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/identifier_type](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/object/properties/identifier_type) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"], "declared_values_not_new_validation_restrictions": ["Site", "VDir", "Webserver"]} | source-derived |
| [/$defs/object/properties/identifier](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/object/properties/identifier) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/section](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/object/properties/section) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/parameter](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/object/properties/parameter) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.appcmdlistconfig.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
