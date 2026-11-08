# esx.host_account

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/object/properties/filters) |
| `account_name` | object | 0..1 | User account name on the ESXi host. | [/$defs/object/properties/account_name](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/object/properties/account_name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `account_name` | array, object | 0..1 | User account name on the ESXi host. | [/$defs/meanings/properties/account_name](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/account_name) |
| `domain` | array, object | 0..1 | The name of the domain to which the user account belongs. | [/$defs/meanings/properties/domain](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/domain) |
| `description` | array, object | 0..1 | Descriptive information about the user account. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/description) |
| `shell_access_enabled` | array, object | 0..1 | True if ESXi shell access is enabled for the user account; false otherwise. | [/$defs/meanings/properties/shell_access_enabled](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/shell_access_enabled) |
| `role` | array, object | 0..1 | The role granted to the host account. | [/$defs/meanings/properties/role](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json#/$defs/meanings/properties/role) |

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

[Local schema constraints](../advanced/esx.host_account.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`account_name` | string | source-meaning-reviewed |
| Item.`account_name` | string | source-meaning-reviewed |
| Item.`domain` | string | source-meaning-reviewed |
| Item.`description` | string | source-meaning-reviewed |
| Item.`shell_access_enabled` | boolean | source-meaning-reviewed |
| Item.`role` | string | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/esx.host_account.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 6.0 new tests only, commit `5afcf590fb5d334687bfdc47f98716424cdb7f3d`, `esx-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **experimental**.
