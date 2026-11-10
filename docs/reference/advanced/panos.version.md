# panos.version — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/major_version) | {} | source-derived |

[/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/major_version): Used to check the major version piece of the version string.

`major_version` is used to check the major version piece of the version string.

The value is an integer and in the example 10.1.14-h9 the major version is '10'.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/minor_version) | {} | source-derived |

[/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/minor_version): Used to check the minor version piece of the version string.

`minor_version` is used to check the minor version piece of the version string.

The value is an integer and in the example 10.1.14-h9 the minor version is '1'.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/release) | {} | source-derived |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/release): Used to check the release piece of the version string.

`release` is used to check the release piece of the version string.

The value is an integer and in the example 10.1.14-h9 the release is '14'.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/hotfix](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/hotfix) | {} | source-derived |

[/$defs/meanings/properties/hotfix](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/hotfix): Used to check the hotfix piece of the version string.

`hotfix` is used to check the hotfix piece of the version string.

The value is an integer and in the example 10.1.14-h9 the hotfix is '9'.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/version_string) | {} | source-derived |

[/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/version_string): Used to check the sw-version raw string output of a PAN-OS XML API request.

`version_string` is used to check the sw-version raw string output of a PAN-OS XML API request.

The value is an string and the example 10.1.14-h9.

This is entirely controlled by operator attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/model_name](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/model_name) | {} | source-derived |

[/$defs/meanings/properties/model_name](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/model_name): Used to check the model string output of a PAN-OS XML API request.

`model_name` is used to check the model string output of a PAN-OS XML API request.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/object): The Object is used by `panos.version` to define the different version information associated with an PANOS system.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
