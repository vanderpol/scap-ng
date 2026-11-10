# iosxe.snmpuser — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/name): The SNMP user name.

Element with the SNMP user name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/group) | {} | source-derived |

[/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/group): The SNMP group the user belongs to.

Element with the SNMP group the user belongs to.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/version) | {} | source-derived |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/version): The SNMP version of the user.

Element with the SNMP version of the user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/ipv4_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/ipv4_acl): The IPv4 ACL name applied to the user.

Element with the IPv4 ACL name applied to the user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/ipv6_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/ipv6_acl): The IPv6 ACL name applied to the user.

Element with the IPv6 ACL name applied to the user.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/priv](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/priv) | {} | source-derived |

[/$defs/meanings/properties/priv](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/priv): The SNMP encryption type for the user (for SNMPv3).

Element with the SNMP encryption type for the user (for SNMPv3).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/auth](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/auth) | {} | source-derived |

[/$defs/meanings/properties/auth](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/meanings/properties/auth): The SNMP authentication type for the user (for SNMPv3).

Element with the SNMP authentication type for the user (for SNMPv3).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/object): The Object is used by an snmpuser test to define the object to be evaluated.

A snmpuser object consists of a name field that is the name of the SNMP user to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/item): Stores information about an SNMP user configuration in IOS.

That information includes the user name, the SNMP group he belongs to, the SNMP version, the IPv4 or IPv6 ACL it is applied to, the Security Level and the Authentication type that apply to the user (for SNMPv3).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.snmpuser.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
