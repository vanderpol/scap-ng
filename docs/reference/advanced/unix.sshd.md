# unix.sshd — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/filepath) | {} | source-derived |

[/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/filepath): The name of the sshd configuration file.

`filepath` specifies the absolute path to the sshd configuration file on the machine.

Specifies the name of the sshd configuration file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/name): SSH daemon configuration parameter name.

`name` contains a string that represents the name of a sshd parameter that was collected from the local system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/value) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/meanings/properties/value): Value of the SSH daemon parameter.

`value` contains a string that represents the current value(s) for the specified sshd parameter on the local system.

`value` contains a string that represents the value(s) associated with the specified sshd parameter.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/object/properties/filepath): The name of the configuration file.

Specifies the name of the configuration file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/item): The Item stores information retrieved from the local system about sshd parameters and their respective value(s).

Information is collected from the target endpoint using the "sshd -f [FILEPATH] -T [NAME]" command and output values are parsed.

Each output line begins with the name of the SSHD parameter, followed by a space, and potentially a tokenized list of values.

It has been found that some parameter values are comma-delimited while some are space-delimited.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.sshd.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
