# windows.wuaupdatesearcher

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/filters) |
| `search_criteria` | object | 0..1 | Search criteria to use when generating a search result. | [/$defs/object/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/search_criteria) |
| `include_superseded_updates` | See schema | 0..1 | Whether updates superseded by other matching updates are included. | [/$defs/object/properties/include_superseded_updates](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/include_superseded_updates) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `search_criteria` | array, object | 0..1 | String to examine the search criteria that was used to generate the object set. | [/$defs/meanings/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/search_criteria) |
| `update_id` | array, object | 0..1 | The update_id enity specifies a string that represents a revision-independent identifier of an update. | [/$defs/meanings/properties/update_id](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/update_id) |
| `title` | array, object | 0..1 | Short text provided from Micrsoft related to the update ID | [/$defs/meanings/properties/title](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/title) |
| `support_url` | array, object | 0..1 | The support field is the URL provideded by Microsoft related to this update ID | [/$defs/meanings/properties/support_url](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/support_url) |
| `is_installed` | array, object | 0..1 | Whether the update is installed. | [/$defs/meanings/properties/is_installed](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_installed) |
| `is_hidden` | array, object | 0..1 | Whether the update is hidden. | [/$defs/meanings/properties/is_hidden](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_hidden) |
| `msrc_severity` | array, object | 0..1 | Microsoft Security Response Center severity rating. | [/$defs/meanings/properties/msrc_severity](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/msrc_severity) |
| `last_deployment_change_time` | array, object | 0..1 | The last published date of the update, provided by Microsoft related to this update ID | [/$defs/meanings/properties/last_deployment_change_time](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/last_deployment_change_time) |
| `source` | array, object | 0..1 | Where the update information was obtained. | [/$defs/meanings/properties/source](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/source) |
| `days_since_source_modified` | array, object | 0..1 | Age of the update-search source file in days. | [/$defs/meanings/properties/days_since_source_modified](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/days_since_source_modified) |

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

[Local schema constraints](../advanced/windows.wuaupdatesearcher.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`search_criteria` | string | source-derived |
| Object.`include_superseded_updates` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Item.`search_criteria` | string | source-derived |
| Item.`update_id` | string | source-derived |
| Item.`title` | string | source-derived |
| Item.`support_url` | string | source-derived |
| Item.`is_installed` | boolean | source-meaning-reviewed |
| Item.`is_hidden` | boolean | source-meaning-reviewed |
| Item.`msrc_severity` | string | source-meaning-reviewed |
| Item.`last_deployment_change_time` | string | source-derived |
| Item.`source` | string | source-derived |
| Item.`days_since_source_modified` | integer | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
