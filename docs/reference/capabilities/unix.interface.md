# unix.interface

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/set) |
| `name` | object | 0..1 | Interface (eth0, eth1, fw0, etc.) name to check. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/unix_interface_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | array, object | 0..1 | Interface (eth0, eth1, fw0, etc.) name to check. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/name) |
| `type` | array, object | 0..1 | Type of interface. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/type) |
| `hardware_addr` | array, object | 0..1 | Hardware or MAC address of the physical network card. | [/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/hardware_addr) |
| `inet_addr` | array, object | 0..1 | The IP address of the interface. | [/$defs/meanings/properties/inet_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/inet_addr) |
| `broadcast_addr` | array, object | 0..1 | The broadcast IP address for this interface's network. | [/$defs/meanings/properties/broadcast_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/broadcast_addr) |
| `netmask` | array, object | 0..1 | The bitmask used to calculate the interface's IP network. | [/$defs/meanings/properties/netmask](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/netmask) |
| `flag` | array, object | 0..1 | Interface flag line, which generally contains flags like "UP" to denote an active interface, "PROMISC" to note that the interface is listening for Ethernet frames not specifically addressed to it, and others. | [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/flag) |

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

[Local schema constraints](../advanced/unix.interface.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`name` | string | source-derived |
| Item.`name` | string | source-derived |
| Item.`type` | string | source-derived |
| Item.`hardware_addr` | string | source-derived |
| Item.`inet_addr` | string | source-derived |
| Item.`broadcast_addr` | string | source-derived |
| Item.`netmask` | string | source-derived |
| Item.`flag` | string | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
