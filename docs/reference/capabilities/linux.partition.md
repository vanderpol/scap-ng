# linux.partition

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.partition` is used to check the information associated with partitions on the local system.

**Contract status: unresolved.** Mount namespace, space units, inaccessible mounts and repeated mount records require native runtime evidence.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.partition.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/set) |
| `mount_point` | string | 0..1 | Directory at which the filesystem is mounted. | [/$defs/object/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/object/properties/mount_point) |

Validation shape: [/$defs/linux_partition_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_partition_object/oneOf/1).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `mount_point` | string | 0..1 | Directory at which the filesystem is mounted. | [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_point) |
| `device` | string | 0..1 | Device associated with the mounted filesystem. | [/$defs/meanings/properties/device](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/device) |
| `uuid` | string | 0..1 | Filesystem UUID. | [/$defs/meanings/properties/uuid](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/uuid) |
| `fs_type` | string | 0..1 | Filesystem type. | [/$defs/meanings/properties/fs_type](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/fs_type) |
| `mount_options` | string | 0..1 | Options recorded for the mount. | [/$defs/meanings/properties/mount_options](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/mount_options) |
| `total_space` | integer | 0..1 | Total filesystem space. | [/$defs/meanings/properties/total_space](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/total_space) |
| `space_used` | integer | 0..1 | Filesystem space in use. | [/$defs/meanings/properties/space_used](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_used) |
| `space_left` | integer | 0..1 | Available filesystem space. | [/$defs/meanings/properties/space_left](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left) |
| `space_left_for_unprivileged_users` | integer | 0..1 | Integer that represents the number of physical blocks remaining on a partition that are available to be used by unprivileged users. | [/$defs/meanings/properties/space_left_for_unprivileged_users](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/space_left_for_unprivileged_users) |
| `block_size` | integer | 0..1 | Integer that represents the actual byte size of each physical block on the partition's block device. | [/$defs/meanings/properties/block_size](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json#/$defs/meanings/properties/block_size) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with a partition.

This includes the name, filesystem type, mount options, total space, space used, and space left.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.partition.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.partition.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
