# unix.process — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/command_line) | {} | source-derived |
| [/$defs/meanings/properties/exec_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_time) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |
| [/$defs/meanings/properties/ppid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ppid) | {} | source-derived |
| [/$defs/meanings/properties/priority](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/priority) | {} | source-derived |
| [/$defs/meanings/properties/ruid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ruid) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/scheduling_class](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/scheduling_class) | {} | source-derived |
| [/$defs/meanings/properties/start_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/start_time) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/tty](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/tty) | {} | source-derived |
| [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/user_id) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/exec_shield](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_shield) | {} | source-derived |
| [/$defs/meanings/properties/loginuid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/loginuid) | {} | source-derived |
| [/$defs/meanings/properties/posix_capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/posix_capability) | {} | source-derived |
| [/$defs/meanings/properties/selinux_domain_label](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/selinux_domain_label) | {} | source-derived |
| [/$defs/meanings/properties/session_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/session_id) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/command_line) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/pid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
