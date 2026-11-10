# esx.host_service — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#): Inspect service configuration and state on an ESXi host.

This retained experimental mapping comes from the separate pinned 6.0 new-Test source; it has no corresponding 5.12.3 declaration. Its source contracts remain in the engineering ledger.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/service_label](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_label) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/service_policy](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_policy) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/service_running](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_running) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/service_required](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/meanings/properties/service_required) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/service_name](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/object/properties/service_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/esx.host_service.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
