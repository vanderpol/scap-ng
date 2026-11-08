# unix.uname — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/machine_class](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/machine_class) | {} | source-derived |

[/$defs/meanings/properties/machine_class](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/machine_class): A machine hardware name.

This field specifies the machine hardware name.

This corresponds to the command uname -m.

This field specifies a machine hardware name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/node_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/node_name) | {} | source-derived |

[/$defs/meanings/properties/node_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/node_name): A host name.

This field specifies the host name.

This corresponds to the command uname -n.

This field specifies a host name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/os_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_name) | {} | source-derived |

[/$defs/meanings/properties/os_name](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_name): An operating system name.

This field specifies the operating system name.

This corresponds to the command uname -s.

This field specifies an operating system name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/os_release](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_release) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/os_release](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_release): Operating-system release identifier.

This field specifies the build version.

This corresponds to the command uname -r.

This field specifies a build version.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/os_version](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_version) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/os_version](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/os_version): Operating-system version identifier.

This field specifies the operating system version.

This corresponds to the command uname -v.

This field specifies an operating system version.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/processor_type](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/processor_type) | {} | source-derived |

[/$defs/meanings/properties/processor_type](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/meanings/properties/processor_type): A processor type.

This field specifies the processor type.

This corresponds to the command uname -p.

This field specifies a processor type.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/object): The Object is used by an uname test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/item): Information about the hardware the machine is running on.

This information is the parsed equivalent of uname -a.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.uname.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
