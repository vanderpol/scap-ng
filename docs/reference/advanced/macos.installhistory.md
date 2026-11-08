# macos.installhistory — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/name): Installed software title.

`name` contains the name of the software history entry represented by the item.

`name` contains a string that represents the name of a software title that was collected from the local system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/install_version](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_version) | {} | source-derived |

[/$defs/meanings/properties/install_version](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_version): Version of an installed software item.

`install_version` contains the version of the installed software item.

`install_version` contains the version of an installed software item.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/install_date](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_date) | {} | source-derived |

[/$defs/meanings/properties/install_date](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_date): Date that a software item was installed on the system.

`install_date` contains the date that the software item was installed on the system.

`install_date` contains the date that a software item was installed on the system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/package_source](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/package_source) | {"declared_values_not_new_validation_restrictions": ["Apple", "AppStore", "ThirdParty"]} | source-derived |

[/$defs/meanings/properties/package_source](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/package_source): Source type of an installed software item.

`package_source` contains the source of the installed software item.

`package_source` contains the source type of an installed software item.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/item): The Item stores information retrieved from the system_profiler about installed software on the device.

Information is collected from the target endpoint using the "system_profiler SPInstallHistoryDataType" command and output values are parsed from the XML output.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
