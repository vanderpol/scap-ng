# ios.snmpcommunity — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/name): The SNMP community name.

Element with the SNMP community name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/view](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/view) | {} | source-derived |

[/$defs/meanings/properties/view](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/view): The view that restricts the OIDs of this community.

Element with the view that restricts the OIDs of this community.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/mode](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/mode) | {} | source-derived |

[/$defs/meanings/properties/mode](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/mode): The read-write privileges of the community.

Element with the read-write privileges of the community.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv4_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv4_acl): The IPv4 ACL name applied to the community.

Element with the IPv4 ACL name applied to the community.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv6_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv6_acl): The IPv6 ACL name applied to the community.

Element with the IPv6 ACL name applied to the community.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object): An snmpcommunity object consists of a community name field to be tested.

The Object is used by an snmpcommunity test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
