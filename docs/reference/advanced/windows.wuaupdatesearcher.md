# windows.wuaupdatesearcher — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#): The `windows.wuaupdatesearcher` is used to evaluate patch level in a Windows environment utilizing the WUA (Windows Update Agent) interface.

The content source is specific to a given system evaluating `windows.wuaupdatesearcher` and thus is not defined by this test.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/search_criteria) | {} | source-derived |

[/$defs/meanings/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/search_criteria): String to examine the search criteria that was used to generate the object set.

`search_criteria` specifies a string to examine the search criteria that was used to generate the object set.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/update_id](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/update_id) | {} | source-derived |

[/$defs/meanings/properties/update_id](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/update_id): The update_id enity specifies a string that represents a revision-independent identifier of an update.

`update_id` specifies a string that represents a revision-independent identifier of an update.

This information is part of the IUpdateIdentity interface that is part of the result of the IUpdateSearcher interface's Search method.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/title](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/title) | {} | source-derived |

[/$defs/meanings/properties/title](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/title): Short text provided from Micrsoft related to the update ID

`title` is the short text provided from Micrsoft related to the update ID

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/support_url](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/support_url) | {} | source-derived |

[/$defs/meanings/properties/support_url](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/support_url): The support field is the URL provideded by Microsoft related to this update ID

The SupportUrl field is the URL provided by Microsoft related to this update ID

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/is_installed](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_installed) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/is_installed](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_installed): Whether the update is installed.

The IsInstalled field is the URL provided by Microsoft related to this update ID

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/is_hidden](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_hidden) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/is_hidden](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_hidden): Whether the update is hidden.

The IsHidden field is the URL provided by Microsoft related to this update ID

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/msrc_severity](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/msrc_severity) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/msrc_severity](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/msrc_severity): Microsoft Security Response Center severity rating.

The Microsoft Security Response Center (MSRC) rating provided by Microsoft related to this update ID, includes 'Critical', 'Important', 'Moderate', 'Low', 'Unspecified', ''

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/last_deployment_change_time](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/last_deployment_change_time) | {} | source-derived |
| [/$defs/meanings/properties/source](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/source) | {"declared_values_not_new_validation_restrictions": ["Windows_Update", "WSUS", "Offline_Cab_File"]} | source-derived |
| [/$defs/meanings/properties/days_since_source_modified](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/days_since_source_modified) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/days_since_source_modified](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/days_since_source_modified): Age of the update-search source file in days.

The number of days since the wsusscn2.cab file was last modified, rounded down to the nearest integer (floor function).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/search_criteria) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/search_criteria): Search criteria to use when generating a search result.

The string consists of criteria that are evaluated to determine which updates to return.

The Search method performs a synchronous search for updates by using the current configured search options.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/include_superseded_updates](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/include_superseded_updates) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
