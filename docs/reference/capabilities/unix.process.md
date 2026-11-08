# unix.process

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/filters) |
| `command_line` | object | 0..1 | String used to start the process. | [/$defs/object/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/command_line) |
| `pid` | object | 0..1 | Process ID of the process. | [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/pid) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `command_line` | array, object | 0..1 | The string used to start the process. | [/$defs/meanings/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/command_line) |
| `exec_time` | array, object | 0..1 | Cumulative CPU time used by the process. | [/$defs/meanings/properties/exec_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_time) |
| `pid` | array, object | 0..1 | The process ID of the process. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/pid) |
| `ppid` | array, object | 0..1 | The process ID of the process's parent process. | [/$defs/meanings/properties/ppid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ppid) |
| `priority` | array, object | 0..1 | The scheduling priority with which the process runs. | [/$defs/meanings/properties/priority](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/priority) |
| `ruid` | array, object | 0..1 | Real user identifier of the process. | [/$defs/meanings/properties/ruid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ruid) |
| `scheduling_class` | array, object | 0..1 | A platform specific characteristic maintained by the scheduler: RT (real-time), TS (timeshare), FF (fifo), SYS (system), etc. | [/$defs/meanings/properties/scheduling_class](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/scheduling_class) |
| `start_time` | array, object | 0..1 | Process start time. | [/$defs/meanings/properties/start_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/start_time) |
| `tty` | array, object | 0..1 | The TTY on which the process was started, if applicable. | [/$defs/meanings/properties/tty](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/tty) |
| `user_id` | array, object | 0..1 | Effective user identifier of the process. | [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/user_id) |
| `exec_shield` | array, object | 0..1 | A boolean that when true would indicates that ExecShield is enabled for the process. | [/$defs/meanings/properties/exec_shield](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_shield) |
| `loginuid` | array, object | 0..1 | The loginuid shows which account a user gained access to the system with. | [/$defs/meanings/properties/loginuid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/loginuid) |
| `posix_capability` | array, object | 0..1 | An effective capability associated with the process. | [/$defs/meanings/properties/posix_capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/posix_capability) |
| `selinux_domain_label` | array, object | 0..1 | An selinux domain label associated with the process. | [/$defs/meanings/properties/selinux_domain_label](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/selinux_domain_label) |
| `session_id` | array, object | 0..1 | The session ID of the process. | [/$defs/meanings/properties/session_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/session_id) |

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

[Local schema constraints](../advanced/unix.process.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`command_line` | string | source-derived |
| Object.`pid` | integer | source-derived |
| Item.`command_line` | string | source-derived |
| Item.`exec_time` | string | source-meaning-reviewed |
| Item.`pid` | integer | source-derived |
| Item.`ppid` | integer | source-derived |
| Item.`priority` | integer | source-derived |
| Item.`ruid` | integer | source-meaning-reviewed |
| Item.`scheduling_class` | string | source-derived |
| Item.`start_time` | string | source-meaning-reviewed |
| Item.`tty` | string | source-derived |
| Item.`user_id` | integer | source-meaning-reviewed |
| Item.`exec_shield` | boolean | source-derived |
| Item.`loginuid` | integer | source-derived |
| Item.`posix_capability` | string | source-derived |
| Item.`selinux_domain_label` | string | source-derived |
| Item.`session_id` | integer | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.process.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
