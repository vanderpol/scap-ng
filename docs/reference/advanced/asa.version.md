# asa.version — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#): The version test is used to check the version of the ASA operating system.

It is based off of the SHOW VERSION command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/asa_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_release) | {} | source-derived |

[/$defs/meanings/properties/asa_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_release): Whole ASA version information.

`asa_release` specifies the whole ASA version information.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/asa_major_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_major_release) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/asa_major_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_major_release): Major-release component of the ASA version.

The asa_major_release is the dotted version that starts a version string.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/asa_minor_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_minor_release) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/asa_minor_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_minor_release): Minor-release component of the ASA version.

The asa_minor_release is the dotted version that starts a version string.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/asa_build](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_build) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/asa_build](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_build): ASA build number.

The asa_build is an integer.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/object): The Object is used by a version test to define the different version information associated with a ASA system.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/item): Stores the version information held within a Cisco ASA software release.

The asa_major_release, asa_minor_release and asa_build elements specify seperated parts of ASA software version information.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
