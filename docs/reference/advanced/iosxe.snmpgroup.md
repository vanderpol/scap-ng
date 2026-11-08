# iosxe.snmpgroup — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/name): The SNMP group name.

Element with the SNMP group name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/version) | {} | source-derived |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/version): The SNMP version of the group.

Element with the SNMP version of the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/snmpv3_sec_level) | {} | source-derived |

[/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/snmpv3_sec_level): The SNMPv3 security configured for the group.

Element with the SNMPv3 security configure for the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv4_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv4_acl): The IPv4 ACL name applied to the group.

Element with the IPv4 ACL name applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv6_acl) | {} | source-derived |

[/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv6_acl): The IPv6 ACL name applied to the group.

Element with the IPv6 ACL name applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/read_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/read_view) | {} | source-derived |

[/$defs/meanings/properties/read_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/read_view): The SNMP read view applied to the group.

Element with the SNMP read view applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/write_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/write_view) | {} | source-derived |

[/$defs/meanings/properties/write_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/write_view): The SNMP write view applied to the group.

Element with the SNMP write view applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/notify_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/notify_view) | {} | source-derived |

[/$defs/meanings/properties/notify_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/notify_view): The SNMP notify view applied to the group.

Element with the SNMP notify view applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object): The Object is used by an snmpgroup test to define the object to be evaluated.

A snmpgroup object consists of a name field that is the name of the SNMP group to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/item): Stores information about an SNMP group configuration in IOS.

That information includes the group name, the SNMP version, the IPv4 or IPv6 ACL it is applied toand the read, write and/or notify views applied to the group.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
