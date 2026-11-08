# aix.fix — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/apar_number) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/abstract](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/abstract) | {} | source-derived |
| [/$defs/meanings/properties/symptom](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/symptom) | {} | source-derived |
| [/$defs/meanings/properties/installation_status](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/installation_status) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object/properties/apar_number) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
