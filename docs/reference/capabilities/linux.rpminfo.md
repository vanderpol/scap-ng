# linux.rpminfo

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Package database failures, duplicate package instances and requested-file-path result granularity require native runtime evidence.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/filters) |
| `package_name` | object | 0..1 | Installed RPM package name. | [/$defs/object/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/package_name) |
| `include_file_paths` | See schema | 0..1 | Whether to request the paths of files owned by the package. | [/$defs/object/properties/include_file_paths](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/include_file_paths) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `package_name` | array, object | 0..1 | Installed RPM package name. | [/$defs/meanings/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/package_name) |
| `architecture` | array, object | 0..1 | Package architecture. | [/$defs/meanings/properties/architecture](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/architecture) |
| `epoch` | array, object | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/epoch) |
| `release` | array, object | 0..1 | Package release component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/release) |
| `version` | array, object | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/version) |
| `evr` | array, object | 0..1 | Combined epoch, version, and release. | [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/evr) |
| `signature_key_id` | array, object | 0..1 | Identifier of the package signing key. | [/$defs/meanings/properties/signature_key_id](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/signature_key_id) |
| `extended_name` | array, object | 0..1 | Package name including epoch, version, release, and architecture. | [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/extended_name) |
| `full_path` | array, object | 0..1 | Path of a file owned by the package. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/full_path) |

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

[Local schema constraints](../advanced/linux.rpminfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`package_name` | string | native-mapping-reviewed |
| Object.`include_file_paths` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Item.`package_name` | string | native-mapping-reviewed |
| Item.`architecture` | string | native-mapping-reviewed |
| Item.`epoch` | string, integer | native-mapping-reviewed |
| Item.`release` | string, version | native-mapping-reviewed |
| Item.`version` | string, version | native-mapping-reviewed |
| Item.`evr` | rpm_evr | native-mapping-reviewed |
| Item.`signature_key_id` | string | native-mapping-reviewed |
| Item.`extended_name` | string | native-mapping-reviewed |
| Item.`full_path` | string | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
