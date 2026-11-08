# ios.snmpuser

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/object/properties/filters) |
| `name` | object | 0..1 | The SNMP user name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | array, object | 0..1 | The SNMP user name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/name) |
| `group` | array, object | 0..1 | The SNMP group the user belongs to. | [/$defs/meanings/properties/group](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/group) |
| `version` | array, object | 0..1 | The SNMP version of the user. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/version) |
| `ipv4_acl` | array, object | 0..1 | The IPv4 ACL name applied to the user. | [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/ipv4_acl) |
| `ipv6_acl` | array, object | 0..1 | The IPv6 ACL name applied to the user. | [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/ipv6_acl) |
| `priv` | array, object | 0..1 | The SNMP encryption type for the user (for SNMPv3). | [/$defs/meanings/properties/priv](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/priv) |
| `auth` | array, object | 0..1 | The SNMP authentication type for the user (for SNMPv3). | [/$defs/meanings/properties/auth](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json#/$defs/meanings/properties/auth) |

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

[Local schema constraints](../advanced/ios.snmpuser.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`name` | string | source-derived |
| Item.`name` | string | source-derived |
| Item.`group` | string | source-derived |
| Item.`version` | string | source-derived |
| Item.`ipv4_acl` | string | source-derived |
| Item.`ipv6_acl` | string | source-derived |
| Item.`priv` | string | source-derived |
| Item.`auth` | string | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/ios.snmpuser.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `ios-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
