# unix.shadow — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/username) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/password) | {} | source-derived |
| [/$defs/meanings/properties/chg_lst](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_lst) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/chg_allow](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_allow) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/chg_req](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_req) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/exp_warn](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_warn) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/exp_inact](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_inact) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/exp_date](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_date) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/flag) | {} | source-derived |
| [/$defs/meanings/properties/encrypt_method](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/encrypt_method) | {"declared_values_not_new_validation_restrictions": ["DES", "BSDi", "MD5", "Blowfish", "Sun MD5", "SHA-256", "SHA-512"]} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/username) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1/properties/username", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
