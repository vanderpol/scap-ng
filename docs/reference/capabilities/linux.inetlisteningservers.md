# linux.inetlisteningservers

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/filters) |
| `protocol` | object | 0..1 | Certain transport-layer protocol, in lowercase: tcp or udp. | [/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/protocol) |
| `local_address` | object | 0..1 | The IP address of the network interface on which an application listens. | [/$defs/object/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_address) |
| `local_port` | object | 0..1 | The TCP or UDP port on which an application would listen. | [/$defs/object/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_port) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `protocol` | array, object | 0..1 | Specific transport-layer protocol, in lowercase: tcp or udp, associated with the inet listening server. | [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/protocol) |
| `local_address` | array, object | 0..1 | The IP address of the network interface on which the program listens. | [/$defs/meanings/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_address) |
| `local_port` | array, object | 0..1 | The TCP or UDP port number associated with the inet listening server. | [/$defs/meanings/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_port) |
| `local_full_address` | array, object | 0..1 | The IP address and network port number associated with the inet listening server, equivalent to local_address:local_port. | [/$defs/meanings/properties/local_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_full_address) |
| `program_name` | array, object | 0..1 | The name of the communicating program. | [/$defs/meanings/properties/program_name](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/program_name) |
| `foreign_address` | array, object | 0..1 | The IP address with which the program is communicating, or with which it will communicate, in the case of a listening server. | [/$defs/meanings/properties/foreign_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_address) |
| `foreign_port` | array, object | 0..1 | The TCP or UDP port to which the program communicates. | [/$defs/meanings/properties/foreign_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_port) |
| `foreign_full_address` | array, object | 0..1 | The IP address and network port to which the program is communicating or will accept communications from, equivalent to foreign_address:foreign_port. | [/$defs/meanings/properties/foreign_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_full_address) |
| `pid` | array, object | 0..1 | The pid is the process ID of a specific process. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/pid) |
| `user_id` | array, object | 0..1 | Numeric user identifier associated with the listening program. | [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/user_id) |

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

[Local schema constraints](../advanced/linux.inetlisteningservers.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`protocol` | string | source-derived |
| Object.`local_address` | string | source-derived |
| Object.`local_port` | integer | source-derived |
| Item.`protocol` | string | source-derived |
| Item.`local_address` | string | source-derived |
| Item.`local_port` | integer | source-derived |
| Item.`local_full_address` | string | source-derived |
| Item.`program_name` | string | source-derived |
| Item.`foreign_address` | string | source-derived |
| Item.`foreign_port` | integer | source-derived |
| Item.`foreign_full_address` | string | source-derived |
| Item.`pid` | integer | source-derived |
| Item.`user_id` | integer | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
