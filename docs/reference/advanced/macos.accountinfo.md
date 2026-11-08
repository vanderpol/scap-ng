# macos.accountinfo — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/username) | {} | source-derived |
| [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/password) | {} | source-derived |
| [/$defs/meanings/properties/uid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/uid) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/gid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/gid) | {} | source-derived |
| [/$defs/meanings/properties/realname](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/realname) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/home_dir](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/home_dir) | {} | source-derived |
| [/$defs/meanings/properties/login_shell](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/login_shell) | {} | source-derived |
| [/$defs/meanings/properties/generated_uid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/generated_uid) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/object/properties/username) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
