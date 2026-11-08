# windows.user_sid — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user_sid) | {} | source-derived |
| [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/enabled) | {} | source-derived |
| [/$defs/meanings/properties/group_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group_sid) | {} | source-derived |
| [/$defs/meanings/properties/last_logon](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/last_logon) | {} | source-derived |
| [/$defs/meanings/properties/user](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/user) | {} | source-derived |
| [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/group) | {} | source-derived |
| [/$defs/meanings/properties/full_name](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/full_name) | {} | source-derived |
| [/$defs/meanings/properties/comment](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/comment) | {} | source-derived |
| [/$defs/meanings/properties/password_age_days](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/meanings/properties/password_age_days) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/user_sid](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/object/properties/user_sid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.user_sid.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
