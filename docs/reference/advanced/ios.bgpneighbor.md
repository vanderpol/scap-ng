# ios.bgpneighbor — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/neighbor](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/meanings/properties/neighbor) | {} | source-derived |

[/$defs/meanings/properties/neighbor](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/meanings/properties/neighbor): The bgp neighbor.

Element with the bgp neighbor.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/meanings/properties/password) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/object): A bgpneighbor object consists of a neighbor field.

The Object is used by a bgpneighbor test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/neighbor](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/object/properties/neighbor) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.bgpneighbor.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
