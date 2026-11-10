# ios.routingprotocolauthintf — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/interface](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/interface) | {} | source-derived |

[/$defs/meanings/properties/interface](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/interface): The interface name.

Element with the interface.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/protocol) | {} | source-derived |

[/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/protocol): The routing protocol.

Element with the routing protocol.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/id](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/id) | {} | source-derived |

[/$defs/meanings/properties/id](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/id): The routing protocol id, if applicable.

Element with the routing protocol id.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/auth_type](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/auth_type) | {} | source-derived |

[/$defs/meanings/properties/auth_type](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/auth_type): The routing protocol authentication type.

Element with the routing protocol authentication type.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ospf_area](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/ospf_area) | {} | source-derived |
| [/$defs/meanings/properties/key_chain](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/key_chain) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object): A routingprotocolauthintf object consists of an interface and the routing protocol that is authenticated field.

The Object is used by a routingprotocolauthintf test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/interface](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/interface) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/protocol) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
