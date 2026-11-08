# esx.host_account — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/account_name](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/account_name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/domain](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/domain) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/description) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/shell_access_enabled](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/shell_access_enabled) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/role](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/role) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/account_name](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/object/properties/account_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
