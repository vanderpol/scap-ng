# iosxe.version — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/version_string) | {} | source-derived |
| [/$defs/meanings/properties/major_release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/major_release) | {} | source-derived |

[/$defs/meanings/properties/major_release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/major_release): The major version piece of the version string.

`major_release` specifies the major version piece of the version string.

The value is an integer and in the example 03.13.02.S the major_release is '3'.

The value is an integer, and in the example 03.13.02.S the major_release is '3'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/release) | {} | source-derived |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/release): The minor release piece of the version string.

`release` specifies the release piece of the version string.

The value is an integer and in the example 03.13.02.S the release version is '13'.

The value is an integer, and in the example 03.13.02.S the release is '13'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/rebuild) | {} | source-derived |

[/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/rebuild): The rebuild piece of the version string.

`rebuild` specifies the release piece of the version string.

The value is an integer and in the example 03.13.02.S the rebuild is '2'.

The value is an integer, and in the example 03.13.02.S the rebuild is '2'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/train](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/train) | {} | source-derived |

[/$defs/meanings/properties/train](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/meanings/properties/train): The train piece of the version string.

`train` specifies the train piece of the version string.

The value is a string and in the example 03.13.02.S the train is 'S'.

The value is a string, and in the example 03.13.02.S the train is 'S'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/object): The Object is used by `iosxe.version` to define the different version information associated with an IOS-XE system.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/iosxe.version.schema.json#/$defs/require): The comparison fields define the version information held within a Cisco IOS-XE Train.

A Cisco IOS-XE train is a vehicle for delivering releases that evolve from a common code base.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
