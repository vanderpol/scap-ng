# linux.systemdunitdependency — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#): The `linux.systemdunitdependency` is used to retrieve information about dependencies of a single systemd unit in the form of a list.

This list contains all dependencies, including transitive dependencies.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/unit) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/unit): Full systemd unit name, including its type suffix.

`unit` refers to the full systemd unit name, which has a form of "$name.$type".

This name is usually also the filename of the unit configuration file located in the /etc/systemd/ and /usr/lib/systemd/ directories.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/dependency](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/dependency) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/dependency](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/dependency): Name of a unit on which the selected unit depends.

`dependency` refers to the name of a unit that was confirmed to be a dependency of the given unit.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object/properties/unit) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1/properties/unit", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
