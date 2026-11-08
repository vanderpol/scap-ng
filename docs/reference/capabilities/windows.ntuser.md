# windows.ntuser

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/set) |
| `key` | object | 0..1 | Registry key to be collected. | [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/key) |
| `name` | null, object | 0..1 | Name assigned to a value associated with a specific registry key. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/name) |
| `include_default` | boolean | 0..1 | Whether the local Default user's ntuser.dat is included. | [/$defs/object/properties/include_default](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/include_default) |
| `item_creation` | string | 0..1 | Controls whether Items are created only for matching key/name pairs or for every relevant ntuser.dat. | [/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/item_creation) |
| `traversal` | not accepted | 0..1 | **Not accepted in this inline form.** Controls downward traversal from the selected hierarchy entry. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/object/properties/traversal) |

### traversal

**Semantic hold inherited from the parent field; these children do not make the parent accepted.**

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means the starting key only, and unlimited removes the depth limit. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

Validation shape: [/$defs/windows_ntuser_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_ntuser_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `key` | array, object | 0..1 | A registry key normally found in the HKCU hive to be tested. | [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/key) |
| `name` | array, object | 0..1 | The name of a value of a registry key. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/name) |
| `sid` | array, object | 0..1 | This field holds a string that represents the SID of a particular user. | [/$defs/meanings/properties/sid](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/sid) |
| `username` | array, object | 0..1 | Name of a particular user. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/username) |
| `account_type` | array, object | 0..1 | If the user account is a local account or domain account. | [/$defs/meanings/properties/account_type](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/account_type) |
| `logged_on` | array, object | 0..1 | If the user account is currently logged on to the computer. | [/$defs/meanings/properties/logged_on](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/logged_on) |
| `days_since_last_logon` | array, object | 0..1 | **Unresolved description** | [/$defs/meanings/properties/days_since_last_logon](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/days_since_last_logon) |
| `user_has_signed_into_explorer` | array, object | 0..1 | If the user account has ever executed explorer.exe. | [/$defs/meanings/properties/user_has_signed_into_explorer](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/user_has_signed_into_explorer) |
| `enabled` | array, object | 0..1 | If the user account is enabled or disabled. | [/$defs/meanings/properties/enabled](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/enabled) |
| `date_modified` | array, object | 0..1 | Time of last modification of file. | [/$defs/meanings/properties/date_modified](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/date_modified) |
| `days_since_modified` | array, object | 0..1 | The number of days since the ntuser.dat file was last modified. | [/$defs/meanings/properties/days_since_modified](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/days_since_modified) |
| `filepath` | array, object | 0..1 | The filepath of the ntuser.dat file. | [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/filepath) |
| `last_write_time` | array, object | 0..1 | The last time that the key or any of its value entries was modified. | [/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/last_write_time) |
| `type` | array, object | 0..1 | The type field allows a test to be written against the registy type associated with the specified registry key(s). | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/type) |
| `value` | array, object | 0..1 | The value field allows a test to be written against the value held within the specified registry key(s). | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json#/$defs/meanings/properties/value) |

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

[Local schema constraints](../advanced/windows.ntuser.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`key` | string | source-derived |
| Object.`name` | string | source-derived |
| Object.`include_default` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`item_creation` | {"enum": ["key_and_name_exist", "every_ntuser"], "required": true, "type": "string"} | native-mapping-reviewed |
| Item.`key` | string | source-derived |
| Item.`name` | string | source-derived |
| Item.`sid` | string | source-derived |
| Item.`username` | string | source-derived |
| Item.`account_type` | string | source-derived |
| Item.`logged_on` | boolean | source-derived |
| Item.`days_since_last_logon` | integer | unresolved |
| Item.`user_has_signed_into_explorer` | boolean | source-derived |
| Item.`enabled` | boolean | source-derived |
| Item.`date_modified` | integer | source-derived |
| Item.`days_since_modified` | integer | source-derived |
| Item.`filepath` | string | source-derived |
| Item.`last_write_time` | integer | source-derived |
| Item.`type` | string | source-derived |
| Item.`value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.ntuser.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
