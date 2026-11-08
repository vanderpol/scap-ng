# unix.interface — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/name) | {} | source-derived |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/type) | {"declared_values_not_new_validation_restrictions": ["ARPHRD_ETHER", "ARPHRD_FDDI", "ARPHRD_LOOPBACK", "ARPHRD_VOID", "ARPHRD_PPP", "ARPHRD_SLIP", "ARPHRD_PRONET"]} | source-derived |
| [/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/hardware_addr) | {} | source-derived |
| [/$defs/meanings/properties/inet_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/inet_addr) | {} | source-derived |
| [/$defs/meanings/properties/broadcast_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/broadcast_addr) | {} | source-derived |
| [/$defs/meanings/properties/netmask](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/netmask) | {} | source-derived |
| [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/flag) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1/properties/name", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
