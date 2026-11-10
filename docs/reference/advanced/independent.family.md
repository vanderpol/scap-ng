# independent.family — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#): The `independent.family` element is used to check the family a certain system belongs to.

This test basically allows the high level system types (window, unix, ios, etc.) to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/family](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/meanings/properties/family) | {"declared_values_not_new_validation_restrictions": ["android", "apple_ios", "asa", "aws", "catos", "ios", "iosxe", "junos", "macos", "panos", "pixos", "undefined", "unix", "vmware_infrastructure", "windows"]} | source-meaning-reviewed |

[/$defs/meanings/properties/family](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/meanings/properties/family): Operating-system family.

This element describes the high level system OS type, otherwise known as the family.

This element describes the high-level system OS type to test against.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/object): The Object is used by a family test to define those objects to evaluate based on a specified state.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/independent.family.schema.json#/$defs/require): The comparison fields contain a single field that is used to check the family associated with the system.

The family is a high-level classification of system types.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
