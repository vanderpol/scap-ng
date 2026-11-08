# unix.interface — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/name): Interface (eth0, eth1, fw0, etc.) name to check.

`name` is the actual name of the specific interface.

Examples might be eth0, eth1, fwo, etc.

`name` is the interface (eth0, eth1, fw0, etc.) name to check.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/type) | {"declared_values_not_new_validation_restrictions": ["ARPHRD_ETHER", "ARPHRD_FDDI", "ARPHRD_LOOPBACK", "ARPHRD_VOID", "ARPHRD_PPP", "ARPHRD_SLIP", "ARPHRD_PRONET"]} | source-derived |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/type): Type of interface.

This element specifies the type of interface.

`type` specifies the type of interface.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/hardware_addr) | {} | source-derived |

[/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/hardware_addr): Hardware or MAC address of the physical network card.

`hardware_addr` is the hardware or MAC address of the physical network card.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/inet_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/inet_addr) | {} | source-derived |

[/$defs/meanings/properties/inet_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/inet_addr): The IP address of the interface.

`inet_addr` is the IP address of the specific interface.

This is the IP address of the interface.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/broadcast_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/broadcast_addr) | {} | source-derived |

[/$defs/meanings/properties/broadcast_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/broadcast_addr): The broadcast IP address for this interface's network.

`broadcast_addr` is the broadcast IP address for this interface's network.

This is the broadcast IP address for this interface's network.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/netmask](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/netmask) | {} | source-derived |

[/$defs/meanings/properties/netmask](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/netmask): The bitmask used to calculate the interface's IP network.

The network number is calculated by bitwise-ANDing this with the IP address.

The host number on that network is calculated by bitwise-XORing this with the IP address.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/flag) | {} | source-derived |

[/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/flag): Interface flag line, which generally contains flags like "UP" to denote an active interface, "PROMISC" to note that the interface is listening for Ethernet frames not specifically addressed to it, and others.

This is the interface flag line, which generally contains flags like "UP" to denote an active interface, "PROMISC" to note that the interface is listening for Ethernet frames not specifically addressed to it, and others.

`flag` represents the interface flag line, which generally contains flags like "UP" to denote an active interface, "PROMISC" to note that the interface is listening for Ethernet frames not specifically addressed to it, and others.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object): An interface object consists of a single name field that identifies which interface is being specified.

The Object is used by an interface test to define the specific interfaces(s) to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/name", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/item): The interface item holds information about the interfaces on a system.

Each interface item contains name and address information as well as any associated flags.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
