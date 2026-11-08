# linux.partition — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_point) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_point): Directory at which the filesystem is mounted.

`mount_point` contains a string that represents the mount point of a partition on the local system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/device](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/device) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/device](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/device): Device associated with the mounted filesystem.

`device` contains a string that represents the name of the device.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/uuid](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/uuid) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/uuid](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/uuid): Filesystem UUID.

`uuid` contains a string that represents the universally unique identifier associated with a partition.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/fs_type](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/fs_type) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/fs_type](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/fs_type): Filesystem type.

`fs_type` contains a string that represents the type of filesystem on a partition.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/mount_options](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_options) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/mount_options](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_options): Options recorded for the mount.

`mount_options` contains a string that represents a mount option associated with a partition on the local system.

Implementation note: not all mount options are visible in /etc/mtab or /proc/mounts.

A complete source of additional mount options is the f_flag field of 'struct statvfs'.

`mount_options` contains a string that represents the mount options associated with a partition.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/total_space](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/total_space) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/total_space](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/total_space): Total filesystem space.

`total_space` contains an integer that represents the total number of physical blocks on a partition.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/space_used](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_used) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/space_used](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_used): Filesystem space in use.

`space_used` contains an integer that represents the number of physical blocks used on a partition.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/space_left](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/space_left](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left): Available filesystem space.

`space_left` contains an integer that represents the number of physical blocks left on a partition available to be used by privileged users.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/space_left_for_unprivileged_users](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left_for_unprivileged_users) | {} | source-derived |

[/$defs/meanings/properties/space_left_for_unprivileged_users](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left_for_unprivileged_users): Integer that represents the number of physical blocks remaining on a partition that are available to be used by unprivileged users.

`space_left_for_unprivileged_users` contains an integer that represents the number of physical blocks remaining on a partition that are available to be used by unprivileged users.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/block_size](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/block_size) | {} | source-derived |

[/$defs/meanings/properties/block_size](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/block_size): Integer that represents the actual byte size of each physical block on the partition's block device.

This is the same block size used to compute the total_space, space_used, and space_left.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/mount_point) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1/properties/mount_point", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/require): The comparison fields define the different information associated with a partition.

This includes the name, filesystem type, mount options, total space, space used, and space left.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
