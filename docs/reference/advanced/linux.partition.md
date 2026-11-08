# linux.partition — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_point) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/device](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/device) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/uuid](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/uuid) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/fs_type](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/fs_type) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/mount_options](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_options) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/total_space](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/total_space) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/space_used](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_used) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/space_left](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/space_left_for_unprivileged_users](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left_for_unprivileged_users) | {} | source-derived |
| [/$defs/meanings/properties/block_size](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/block_size) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/mount_point) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/mount_point", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement", "type_alternatives": ["object"]} | existing-native |
