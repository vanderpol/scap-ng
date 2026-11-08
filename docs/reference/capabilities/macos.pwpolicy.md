# macos.pwpolicy

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/filters) |
| `username` | object | 0..1 | User whose password policy is queried. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/username) |
| `authenticator` | object | 0..1 | Username of the authenticator. | [/$defs/object/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator) |
| `authenticator_password` | object | 0..1 | Password of the authenticator as specified by the username field. | [/$defs/object/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator_password) |
| `directory_node` | object | 0..1 | Directory-service node queried for password policy. | [/$defs/object/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/directory_node) |
| `xpath` | object | 0..1 | An XPath 1.0 expression to evaluate against the XML representation of the output generated from the pwpolicy -getaccountinfo command. | [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/xpath) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | array, object | 0..1 | User whose password policy is queried. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/username) |
| `authenticator` | array, object | 0..1 | Username of the authenticator. | [/$defs/meanings/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator) |
| `authenticator_password` | array, object | 0..1 | Password of the authenticator as specified by the authenticator field. | [/$defs/meanings/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator_password) |
| `directory_node` | array, object | 0..1 | Directory-service node queried for password policy. | [/$defs/meanings/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/directory_node) |
| `xpath` | array, object | 0..1 | An XPath expression describing the text node(s) or attribute(s) to look at. | [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/xpath) |
| `value_of` | array, object | 0..1 | The value of the preference key. | [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/value_of) |

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

[Local schema constraints](../advanced/macos.pwpolicy.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`username` | string | source-meaning-reviewed |
| Object.`authenticator` | string | source-derived |
| Object.`authenticator_password` | string | source-derived |
| Object.`directory_node` | string | source-meaning-reviewed |
| Object.`xpath` | string | source-derived |
| Item.`username` | string | source-meaning-reviewed |
| Item.`authenticator` | string | source-derived |
| Item.`authenticator_password` | string | source-derived |
| Item.`directory_node` | string | source-meaning-reviewed |
| Item.`xpath` | string | source-derived |
| Item.`value_of` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
