# aix.fileset — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/flstinst) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/level](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/level) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/state](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/state) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/description) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object/properties/flstinst) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
