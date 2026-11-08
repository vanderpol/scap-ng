# linux.rpmverifyfile

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.rpmverifyfile` is used to verify the integrity of the individual files in installed RPMs.

This test aligns with the rpm -V command for verifying RPMs.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.rpmverifyfile.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `linux.rpmverifyfile` to define a set of files within a set of RPMs to verify.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/filters) |
| `name` | string | 0..1 | Package name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/name) |
| `epoch` | integer, string | 0..1 | Package epoch. | [/$defs/object/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/epoch) |
| `version` | string, version | 0..1 | Package version component. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/version) |
| `release` | string, version | 0..1 | Package release component. | [/$defs/object/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/release) |
| `arch` | string | 0..1 | Package architecture. | [/$defs/object/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/arch) |
| `filepath` | string | 0..1 | Absolute path for a file or directory in the specified package. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/filepath) |
| `skip_link_target` | boolean | 0..1 | Whether symbolic-link target verification is skipped. | [/$defs/object/properties/skip_link_target](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_link_target) |
| `skip_size` | boolean | 0..1 | Whether file-size verification is skipped. | [/$defs/object/properties/skip_size](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_size) |
| `skip_owner` | boolean | 0..1 | Whether file-owner verification is skipped. | [/$defs/object/properties/skip_owner](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_owner) |
| `skip_group` | boolean | 0..1 | Whether file-group verification is skipped. | [/$defs/object/properties/skip_group](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_group) |
| `skip_mtime` | boolean | 0..1 | Whether mtime verification is skipped. | [/$defs/object/properties/skip_mtime](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_mtime) |
| `skip_mode` | boolean | 0..1 | Whether mode verification is skipped. | [/$defs/object/properties/skip_mode](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_mode) |
| `skip_rdev` | boolean | 0..1 | Whether device verification is skipped. | [/$defs/object/properties/skip_rdev](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_rdev) |
| `skip_config_files` | boolean | 0..1 | Whether RPM %config files are excluded. | [/$defs/object/properties/skip_config_files](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_config_files) |
| `skip_ghost_files` | boolean | 0..1 | Whether RPM %ghost files are excluded. | [/$defs/object/properties/skip_ghost_files](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_ghost_files) |
| `skip_file_digest` | boolean | 0..1 | Whether file-digest verification is skipped. | [/$defs/object/properties/skip_file_digest](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_file_digest) |
| `skip_capabilities` | boolean | 0..1 | Whether file-capability verification is skipped. | [/$defs/object/properties/skip_capabilities](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_capabilities) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores the verification results of the individual files in an rpm similar to what is produced by the rpm -V command.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | Package name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/name) |
| `epoch` | integer, string | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/epoch) |
| `version` | string, version | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/version) |
| `release` | string, version | 0..1 | Package release component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/release) |
| `arch` | string | 0..1 | Package architecture. | [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/arch) |
| `filepath` | string | 0..1 | Absolute path for a file or directory in the specified package. | [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/filepath) |
| `extended_name` | string | 0..1 | Package name including epoch, version, release, and architecture. | [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/extended_name) |
| `size_differs` | string | 0..1 | Whether file size differs from the package record. | [/$defs/meanings/properties/size_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/size_differs) |
| `mode_differs` | string | 0..1 | Whether the file mode differs from the package record. | [/$defs/meanings/properties/mode_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/mode_differs) |
| `filedigest_differs` | string | 0..1 | Whether the file digest differs from the package record. | [/$defs/meanings/properties/filedigest_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/filedigest_differs) |
| `device_differs` | string | 0..1 | Whether device metadata differs from the package record. | [/$defs/meanings/properties/device_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/device_differs) |
| `link_mismatch` | string | 0..1 | Whether the symbolic-link target differs from the package record. | [/$defs/meanings/properties/link_mismatch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/link_mismatch) |
| `ownership_differs` | string | 0..1 | Whether ownership differs from the package record. | [/$defs/meanings/properties/ownership_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/ownership_differs) |
| `group_differs` | string | 0..1 | Whether group ownership differs from the package record. | [/$defs/meanings/properties/group_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/group_differs) |
| `mtime_differs` | string | 0..1 | Whether modification time differs from the package record. | [/$defs/meanings/properties/mtime_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/mtime_differs) |
| `capabilities_differ` | string | 0..1 | Whether file capabilities differ from the package record. | [/$defs/meanings/properties/capabilities_differ](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/capabilities_differ) |
| `configuration_file` | boolean | 0..1 | Configuration file attribute marker that may be present on a file. | [/$defs/meanings/properties/configuration_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/configuration_file) |
| `documentation_file` | boolean | 0..1 | Whether the package marks the file as documentation. | [/$defs/meanings/properties/documentation_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/documentation_file) |
| `ghost_file` | boolean | 0..1 | Ghost file attribute marker that may be present on a file. | [/$defs/meanings/properties/ghost_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/ghost_file) |
| `license_file` | boolean | 0..1 | License file attribute marker that may be present on a file. | [/$defs/meanings/properties/license_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/license_file) |
| `readme_file` | boolean | 0..1 | Readme file attribute marker that may be present on a file. | [/$defs/meanings/properties/readme_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/readme_file) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.rpmverifyfile.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`skip_link_target` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_size` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_owner` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_group` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_mtime` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_mode` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_rdev` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_config_files` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_ghost_files` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_file_digest` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_capabilities` | {"required": true, "type": "boolean"} | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
