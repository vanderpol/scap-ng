# esx.host_vib — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/vib_name](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/meanings/properties/vib_name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/acceptance_level](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/meanings/properties/acceptance_level) | {"declared_values_not_new_validation_restrictions": ["VMwareCertified", "VMwareAccepted", "PartnerSupported", "CommunitySupported", "Unknown"]} | source-meaning-reviewed |
| [/$defs/meanings/properties/creation_date](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/meanings/properties/creation_date) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/vendor](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/meanings/properties/vendor) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/meanings/properties/version) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/vib_name](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/object/properties/vib_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/esx.host_vib.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
