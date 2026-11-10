# macos.diskinfo

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/filters) |
| `device_identifier` | object | 0..1 | Disk device identifier. | [/$defs/object/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/object/properties/device_identifier) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `device_identifier` | array, object | 0..1 | Disk device identifier. | [/$defs/meanings/properties/device_identifier](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_identifier) |
| `volume_name` | array, object | 0..1 | The value of the volume name field (if any). | [/$defs/meanings/properties/volume_name](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/volume_name) |
| `file_system_personality` | array, object | 0..1 | The value of the file system personality field (if any). | [/$defs/meanings/properties/file_system_personality](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_system_personality) |
| `removable_media` | array, object | 0..1 | The value of the removable media field (if any). | [/$defs/meanings/properties/removable_media](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/removable_media) |
| `device_location` | array, object | 0..1 | The value of the device location field (if any). | [/$defs/meanings/properties/device_location](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/device_location) |
| `solid_state` | array, object | 0..1 | The value of the solid state flag. | [/$defs/meanings/properties/solid_state](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/solid_state) |
| `read_only` | array, object | 0..1 | The value of the read-only volume flag. | [/$defs/meanings/properties/read_only](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/read_only) |
| `file_vault` | array, object | 0..1 | Whether or not FileVault is enabled on the disk. | [/$defs/meanings/properties/file_vault](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/file_vault) |
| `mount_point` | array, object | 0..1 | The mount point for this disk (if any). | [/$defs/meanings/properties/mount_point](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/mount_point) |
| `smart_status` | array, object | 0..1 | The value of the SMART status field (if any). | [/$defs/meanings/properties/smart_status](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/smart_status) |
| `encrypted` | array, object | 0..1 | The value of the encrypted status field (if any). | [/$defs/meanings/properties/encrypted](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/encrypted) |
| `apfs_uid` | array, object | 0..1 | APFS user identifier. | [/$defs/meanings/properties/apfs_uid](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json#/$defs/meanings/properties/apfs_uid) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

### Condition logic

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |

### Item existence requirement

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Existence only; there is no satisfaction operation without a comparison. | [/$defs/item_presence_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/item_presence_requirement/properties/item_requirement) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.diskinfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`device_identifier` | string | source-meaning-reviewed |
| Item.`device_identifier` | string | source-meaning-reviewed |
| Item.`volume_name` | string | source-derived |
| Item.`file_system_personality` | string | source-derived |
| Item.`removable_media` | string | source-derived |
| Item.`device_location` | string | source-derived |
| Item.`solid_state` | boolean | source-derived |
| Item.`read_only` | boolean | source-derived |
| Item.`file_vault` | boolean | source-derived |
| Item.`mount_point` | string | source-derived |
| Item.`smart_status` | string | source-derived |
| Item.`encrypted` | boolean | source-derived |
| Item.`apfs_uid` | string | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.diskinfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
