# iosxe.snmphost — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/host](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/host) | {} | source-derived |

[/$defs/meanings/properties/host](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/host): The SNMP host address or hostname.

Element with the SNMP host address or hostname.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/community_or_user](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/community_or_user) | {} | source-derived |

[/$defs/meanings/properties/community_or_user](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/community_or_user): The community string or SNMPv3 user configured for the host.

Element with the community string or SNMPv3 user configured for the host.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/version) | {} | source-derived |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/version): The SNMP version.

Element with the SNMP version.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/snmpv3_sec_level) | {} | source-derived |

[/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/snmpv3_sec_level): The SNMPv3 security configured for the host.

Element with the SNMPv3 security configure for the host.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/traps](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/traps) | {} | source-derived |

[/$defs/meanings/properties/traps](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/traps): The SNMP traps configured.

Element with the SNMP traps configured.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object): A snmphost object consists of a host field that is the host of the 'snmp host' IOS-XE command to be tested.

The Object is used by an snmphost test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/host](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object/properties/host) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
