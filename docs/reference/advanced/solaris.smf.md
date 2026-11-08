# solaris.smf — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/fmri) | {} | source-derived |
| [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_name) | {} | source-derived |
| [/$defs/meanings/properties/service_state](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_state) | {} | source-derived |
| [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/protocol) | {} | source-derived |
| [/$defs/meanings/properties/server_executable](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_executable) | {} | source-derived |
| [/$defs/meanings/properties/server_arguements](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_arguements) | {} | source-derived |
| [/$defs/meanings/properties/exec_as_user](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/exec_as_user) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object/properties/fmri) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
