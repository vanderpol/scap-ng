# linux.rpmverifyfile

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/filters) |
| `name` | object | 0..1 | Package name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/name) |
| `epoch` | object | 0..1 | Package epoch. | [/$defs/object/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/epoch) |
| `version` | object | 0..1 | Package version component. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/version) |
| `release` | object | 0..1 | Package release component. | [/$defs/object/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/release) |
| `arch` | object | 0..1 | Package architecture. | [/$defs/object/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/arch) |
| `filepath` | object | 0..1 | Absolute path for a file or directory in the specified package. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/filepath) |
| `skip_link_target` | See schema | 0..1 | Whether symbolic-link target verification is skipped. | [/$defs/object/properties/skip_link_target](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_link_target) |
| `skip_size` | See schema | 0..1 | Whether file-size verification is skipped. | [/$defs/object/properties/skip_size](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_size) |
| `skip_owner` | See schema | 0..1 | Whether file-owner verification is skipped. | [/$defs/object/properties/skip_owner](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_owner) |
| `skip_group` | See schema | 0..1 | Whether file-group verification is skipped. | [/$defs/object/properties/skip_group](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_group) |
| `skip_mtime` | See schema | 0..1 | Whether mtime verification is skipped. | [/$defs/object/properties/skip_mtime](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_mtime) |
| `skip_mode` | See schema | 0..1 | Whether mode verification is skipped. | [/$defs/object/properties/skip_mode](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_mode) |
| `skip_rdev` | See schema | 0..1 | Whether device verification is skipped. | [/$defs/object/properties/skip_rdev](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_rdev) |
| `skip_config_files` | See schema | 0..1 | Whether RPM %config files are excluded. | [/$defs/object/properties/skip_config_files](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_config_files) |
| `skip_ghost_files` | See schema | 0..1 | Whether RPM %ghost files are excluded. | [/$defs/object/properties/skip_ghost_files](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_ghost_files) |
| `skip_file_digest` | See schema | 0..1 | Whether file-digest verification is skipped. | [/$defs/object/properties/skip_file_digest](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_file_digest) |
| `skip_capabilities` | See schema | 0..1 | Whether file-capability verification is skipped. | [/$defs/object/properties/skip_capabilities](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/object/properties/skip_capabilities) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | array, object | 0..1 | Package name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/name) |
| `epoch` | array, object | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/epoch) |
| `version` | array, object | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/version) |
| `release` | array, object | 0..1 | Package release component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/release) |
| `arch` | array, object | 0..1 | Package architecture. | [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/arch) |
| `filepath` | array, object | 0..1 | Absolute path for a file or directory in the specified package. | [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/filepath) |
| `extended_name` | array, object | 0..1 | Package name including epoch, version, release, and architecture. | [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/extended_name) |
| `size_differs` | array, object | 0..1 | Whether file size differs from the package record. | [/$defs/meanings/properties/size_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/size_differs) |
| `mode_differs` | array, object | 0..1 | Whether the file mode differs from the package record. | [/$defs/meanings/properties/mode_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/mode_differs) |
| `filedigest_differs` | array, object | 0..1 | Whether the file digest differs from the package record. | [/$defs/meanings/properties/filedigest_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/filedigest_differs) |
| `device_differs` | array, object | 0..1 | Whether device metadata differs from the package record. | [/$defs/meanings/properties/device_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/device_differs) |
| `link_mismatch` | array, object | 0..1 | Whether the symbolic-link target differs from the package record. | [/$defs/meanings/properties/link_mismatch](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/link_mismatch) |
| `ownership_differs` | array, object | 0..1 | Whether ownership differs from the package record. | [/$defs/meanings/properties/ownership_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/ownership_differs) |
| `group_differs` | array, object | 0..1 | Whether group ownership differs from the package record. | [/$defs/meanings/properties/group_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/group_differs) |
| `mtime_differs` | array, object | 0..1 | Whether modification time differs from the package record. | [/$defs/meanings/properties/mtime_differs](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/mtime_differs) |
| `capabilities_differ` | array, object | 0..1 | Whether file capabilities differ from the package record. | [/$defs/meanings/properties/capabilities_differ](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/capabilities_differ) |
| `configuration_file` | array, object | 0..1 | Configuration file attribute marker that may be present on a file. | [/$defs/meanings/properties/configuration_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/configuration_file) |
| `documentation_file` | array, object | 0..1 | Whether the package marks the file as documentation. | [/$defs/meanings/properties/documentation_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/documentation_file) |
| `ghost_file` | array, object | 0..1 | Ghost file attribute marker that may be present on a file. | [/$defs/meanings/properties/ghost_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/ghost_file) |
| `license_file` | array, object | 0..1 | License file attribute marker that may be present on a file. | [/$defs/meanings/properties/license_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/license_file) |
| `readme_file` | array, object | 0..1 | Readme file attribute marker that may be present on a file. | [/$defs/meanings/properties/readme_file](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json#/$defs/meanings/properties/readme_file) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |


Validation shape: [/$defs/canonical_all_items_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.rpmverifyfile.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`name` | string | source-meaning-reviewed |
| Object.`epoch` | string, integer | source-meaning-reviewed |
| Object.`version` | string, version | source-meaning-reviewed |
| Object.`release` | string, version | source-meaning-reviewed |
| Object.`arch` | string | source-meaning-reviewed |
| Object.`filepath` | string | source-derived |
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
| Item.`name` | string | source-meaning-reviewed |
| Item.`epoch` | string, integer | source-meaning-reviewed |
| Item.`version` | string, version | source-meaning-reviewed |
| Item.`release` | string, version | source-meaning-reviewed |
| Item.`arch` | string | source-meaning-reviewed |
| Item.`filepath` | string | source-derived |
| Item.`extended_name` | string | source-meaning-reviewed |
| Item.`size_differs` | string | source-meaning-reviewed |
| Item.`mode_differs` | string | source-meaning-reviewed |
| Item.`filedigest_differs` | string | source-meaning-reviewed |
| Item.`device_differs` | string | source-meaning-reviewed |
| Item.`link_mismatch` | string | source-meaning-reviewed |
| Item.`ownership_differs` | string | source-meaning-reviewed |
| Item.`group_differs` | string | source-meaning-reviewed |
| Item.`mtime_differs` | string | source-meaning-reviewed |
| Item.`capabilities_differ` | string | source-meaning-reviewed |
| Item.`configuration_file` | boolean | source-derived |
| Item.`documentation_file` | boolean | source-meaning-reviewed |
| Item.`ghost_file` | boolean | source-derived |
| Item.`license_file` | boolean | source-derived |
| Item.`readme_file` | boolean | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.rpmverifyfile.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
