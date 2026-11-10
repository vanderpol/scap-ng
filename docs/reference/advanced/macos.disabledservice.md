# macos.disabledservice — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/label](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/label) | {} | source-derived |

[/$defs/meanings/properties/label](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/label): The name of the service disabled in the domain.

Specifies the name of the agent/daemon.

Specifies the name of the service disabled in the domain.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/disabled](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/disabled) | {} | source-derived |

[/$defs/meanings/properties/disabled](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/meanings/properties/disabled): The actual status of the service as indicated by the output of the 'launchctl print-disabled <domain>' command.

Specifies the actual status of the service as indicated by the output of the 'launchctl print-disabled <domain>' command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.disabledservice.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
