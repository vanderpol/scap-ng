# ios.version55 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/version_string) | {} | source-derived |
| [/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/major_version) | {} | source-derived |

[/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/major_version): The major version piece of the version string.

`major_release` specifies the major version piece of the version string.

The value is an integer and in the example 03.13.02.S the major_release is '3'.

The value is an integer, and in the example 03.13.02.S the major_release is '3'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/release) | {} | source-derived |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/release): The minor release piece of the version string.

`release` specifies the release piece of the version string.

The value is an integer and in the example 03.13.02.S the release version is '13'.

The value is an integer, and in the example 03.13.02.S the release is '13'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/rebuild) | {} | source-derived |

[/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/rebuild): The rebuild piece of the version string.

`rebuild` specifies the release piece of the version string.

The value is an integer and in the example 03.13.02.S the rebuild is '2'.

The value is an integer, and in the example 03.13.02.S the rebuild is '2'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/train_identifier](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/train_identifier) | {} | source-derived |

[/$defs/meanings/properties/train_identifier](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/train_identifier): The train piece of the version string.

`train` specifies the train piece of the version string.

The value is a string and in the example 03.13.02.S the train is 'S'.

The value is a string, and in the example 03.13.02.S the train is 'S'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/minor_version) | {} | source-derived |
| [/$defs/meanings/properties/subrebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/subrebuild) | {} | source-derived |
| [/$defs/meanings/properties/mainline_rebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/mainline_rebuild) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
