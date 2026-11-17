# unix.process

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `unix.process` is used to check information found in the UNIX processes.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.process.md) retain the validated encodings and any broader schema acceptance.

## Object

An Object defines the command line used to start the process(es) and pid.

The Object is used by `unix.process` to define the specific process(es) to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/filters) |
| `command_line` | string | 0..1 | String used to start the process. | [/$defs/object/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/command_line) |
| `pid` | integer | 0..1 | Process ID of the process. | [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/pid) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Output of /usr/bin/ps.

See ps(1).

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `command_line` | string | 0..1 | The string used to start the process. | [/$defs/meanings/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/command_line) |
| `exec_time` | string | 0..1 | Cumulative CPU time used by the process. | [/$defs/meanings/properties/exec_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_time) |
| `pid` | integer | 0..1 | The process ID of the process. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/pid) |
| `ppid` | integer | 0..1 | The process ID of the process's parent process. | [/$defs/meanings/properties/ppid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ppid) |
| `priority` | integer | 0..1 | The scheduling priority with which the process runs. | [/$defs/meanings/properties/priority](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/priority) |
| `ruid` | integer | 0..1 | Real user identifier of the process. | [/$defs/meanings/properties/ruid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ruid) |
| `scheduling_class` | string | 0..1 | A platform specific characteristic maintained by the scheduler: RT (real-time), TS (timeshare), FF (fifo), SYS (system), etc. | [/$defs/meanings/properties/scheduling_class](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/scheduling_class) |
| `start_time` | string | 0..1 | Process start time. | [/$defs/meanings/properties/start_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/start_time) |
| `tty` | string | 0..1 | The TTY on which the process was started, if applicable. | [/$defs/meanings/properties/tty](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/tty) |
| `user_id` | integer | 0..1 | Effective user identifier of the process. | [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/user_id) |
| `exec_shield` | boolean | 0..1 | A boolean that when true would indicates that ExecShield is enabled for the process. | [/$defs/meanings/properties/exec_shield](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_shield) |
| `loginuid` | integer | 0..1 | The loginuid shows which account a user gained access to the system with. | [/$defs/meanings/properties/loginuid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/loginuid) |
| `posix_capability` | string | 0..1 | An effective capability associated with the process. | [/$defs/meanings/properties/posix_capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/posix_capability) |
| `selinux_domain_label` | string | 0..1 | An selinux domain label associated with the process. | [/$defs/meanings/properties/selinux_domain_label](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/selinux_domain_label) |
| `session_id` | integer | 0..1 | The session ID of the process. | [/$defs/meanings/properties/session_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/session_id) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a UNIX process.

This includes the command line, pid, ppid, priority, and user id.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.process.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.process.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
