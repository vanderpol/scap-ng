# macos.diskinfo

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `macos.diskinfo` is used to inspect the contents of 'diskutil info <device ID>' command output.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.diskinfo.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/filters) |
| `device_identifier` | string | 0..1 | Disk device identifier. | [/$defs/object/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/device_identifier) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item contains information retrieved using the 'diskutil info <device ID>' command.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `device_identifier` | string | 0..1 | Disk device identifier. | [/$defs/meanings/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_identifier) |
| `volume_name` | string | 0..1 | The value of the volume name field (if any). | [/$defs/meanings/properties/volume_name](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/volume_name) |
| `file_system_personality` | string | 0..1 | The value of the file system personality field (if any). | [/$defs/meanings/properties/file_system_personality](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_system_personality) |
| `removable_media` | string | 0..1 | The value of the removable media field (if any). | [/$defs/meanings/properties/removable_media](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/removable_media) |
| `device_location` | string | 0..1 | The value of the device location field (if any). | [/$defs/meanings/properties/device_location](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_location) |
| `solid_state` | boolean | 0..1 | The value of the solid state flag. | [/$defs/meanings/properties/solid_state](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/solid_state) |
| `read_only` | boolean | 0..1 | The value of the read-only volume flag. | [/$defs/meanings/properties/read_only](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/read_only) |
| `file_vault` | boolean | 0..1 | Whether or not FileVault is enabled on the disk. | [/$defs/meanings/properties/file_vault](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_vault) |
| `mount_point` | string | 0..1 | The mount point for this disk (if any). | [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/mount_point) |
| `smart_status` | string | 0..1 | The value of the SMART status field (if any). | [/$defs/meanings/properties/smart_status](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/smart_status) |
| `encrypted` | boolean | 0..1 | The value of the encrypted status field (if any). | [/$defs/meanings/properties/encrypted](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/encrypted) |
| `apfs_uid` | string | 0..1 | APFS user identifier. | [/$defs/meanings/properties/apfs_uid](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/apfs_uid) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain entities that are used to check against retrieved disk information.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.diskinfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
