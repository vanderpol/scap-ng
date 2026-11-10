# linux.systemdunitproperty — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/unit) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/unit): Full systemd unit name, including its type suffix.

`unit` refers to the full systemd unit name, which has a form of "$name.$type".

This name is usually also the filename of the unit configuration file located in the /etc/systemd/ and /usr/lib/systemd/ directories.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/property) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/property): Systemd unit property name.

The name of the property associated with a systemd unit.

`property` refers to the systemd unit property that we are interested in.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/value) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/value): Value of the unit property.

The value of the property associated with a systemd unit.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/unit) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/unit", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/property](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/property) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1/properties/property", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
