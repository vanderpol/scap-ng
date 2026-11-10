# macos.diskinfo — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_identifier) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_identifier): Disk device identifier.

The device identifier.

Use a wildcard pattern to collect information for all disk devices.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/volume_name](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/volume_name) | {} | source-derived |
| [/$defs/meanings/properties/file_system_personality](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_system_personality) | {} | source-derived |
| [/$defs/meanings/properties/removable_media](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/removable_media) | {} | source-derived |
| [/$defs/meanings/properties/device_location](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_location) | {} | source-derived |
| [/$defs/meanings/properties/solid_state](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/solid_state) | {} | source-derived |
| [/$defs/meanings/properties/read_only](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/read_only) | {} | source-derived |
| [/$defs/meanings/properties/file_vault](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_vault) | {} | source-derived |
| [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/mount_point) | {} | source-derived |
| [/$defs/meanings/properties/smart_status](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/smart_status) | {} | source-derived |
| [/$defs/meanings/properties/encrypted](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/encrypted) | {} | source-derived |
| [/$defs/meanings/properties/apfs_uid](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/apfs_uid) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/device_identifier) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
