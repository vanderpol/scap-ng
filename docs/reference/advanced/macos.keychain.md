# macos.keychain — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/filepath) | {} | source-derived |

[/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/filepath): The filepath of the keychain used to create the object.

Specifies the filepath of the keychain.

Specifies the filepath of the keychain used to create the object.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/lock_on_sleep](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/lock_on_sleep) | {} | source-derived |

[/$defs/meanings/properties/lock_on_sleep](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/lock_on_sleep): Whether the keychain is configured to lock when the computer sleeps.

Specifies whether the keychain is configured to lock on sleep.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/timeout](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/timeout) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object/properties/filepath): The filepath of the keychain to be queried.

Specifies the filepath of the keychain to be queried.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
