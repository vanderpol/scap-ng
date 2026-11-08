# unix.shadow

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/set) |
| `username` | object | 0..1 | UNIX account name. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/username) |

Validation shape: [/$defs/unix_shadow_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | array, object | 0..1 | UNIX account name. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/username) |
| `password` | array, object | 0..1 | The encrypted version of the user's password. | [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/password) |
| `chg_lst` | array, object | 0..1 | Date of the last password change. | [/$defs/meanings/properties/chg_lst](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_lst) |
| `chg_allow` | array, object | 0..1 | Minimum interval between password changes. | [/$defs/meanings/properties/chg_allow](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_allow) |
| `chg_req` | array, object | 0..1 | Maximum password age. | [/$defs/meanings/properties/chg_req](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_req) |
| `exp_warn` | array, object | 0..1 | Warning interval before password expiration. | [/$defs/meanings/properties/exp_warn](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_warn) |
| `exp_inact` | array, object | 0..1 | Inactivity interval after password expiration. | [/$defs/meanings/properties/exp_inact](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_inact) |
| `exp_date` | array, object | 0..1 | Password expiration date. | [/$defs/meanings/properties/exp_date](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_date) |
| `flag` | array, object | 0..1 | A numeric reserved field that the shadow file may use in the future. | [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/flag) |
| `encrypt_method` | array, object | 0..1 | Method that is used for hashing passwords. | [/$defs/meanings/properties/encrypt_method](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/encrypt_method) |

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

[Local schema constraints](../advanced/unix.shadow.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`username` | string | source-meaning-reviewed |
| Item.`username` | string | source-meaning-reviewed |
| Item.`password` | string | source-derived |
| Item.`chg_lst` | string, integer | source-meaning-reviewed |
| Item.`chg_allow` | string, integer | source-meaning-reviewed |
| Item.`chg_req` | string, integer | source-meaning-reviewed |
| Item.`exp_warn` | string, integer | source-meaning-reviewed |
| Item.`exp_inact` | string, integer | source-meaning-reviewed |
| Item.`exp_date` | string, integer | source-meaning-reviewed |
| Item.`flag` | string, integer | source-derived |
| Item.`encrypt_method` | string | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
