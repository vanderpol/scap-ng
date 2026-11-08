# unix.process — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/command_line) | {} | source-derived |

[/$defs/meanings/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/command_line): The string used to start the process.

This is the string used to start the process.

This includes any parameters that are part of the command line.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/exec_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_time) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |

[/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/pid): The process ID of the process.

This is the process ID of the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ppid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ppid) | {} | source-derived |

[/$defs/meanings/properties/ppid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ppid): The process ID of the process's parent process.

This is the process ID of the process's parent process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/priority](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/priority) | {} | source-derived |

[/$defs/meanings/properties/priority](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/priority): The scheduling priority with which the process runs.

This is the scheduling priority with which the process runs.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/ruid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ruid) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/ruid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/ruid): Real user identifier of the process.

This is the real user id which represents the user who has created the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/scheduling_class](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/scheduling_class) | {} | source-derived |
| [/$defs/meanings/properties/start_time](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/start_time) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/tty](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/tty) | {} | source-derived |
| [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/user_id) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/user_id): Effective user identifier of the process.

This is the effective user id which represents the actual privileges of the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/exec_shield](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/exec_shield) | {} | source-derived |
| [/$defs/meanings/properties/loginuid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/loginuid) | {} | source-derived |

[/$defs/meanings/properties/loginuid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/loginuid): The loginuid shows which account a user gained access to the system with.

The /proc/XXXX/loginuid shows this value.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/posix_capability](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/posix_capability) | {} | source-derived |
| [/$defs/meanings/properties/selinux_domain_label](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/selinux_domain_label) | {} | source-derived |
| [/$defs/meanings/properties/session_id](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/meanings/properties/session_id) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object): An Object defines the command line used to start the process(es) and pid.

The Object is used by `unix.process` to define the specific process(es) to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/command_line) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/command_line](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/command_line): String used to start the process.

`command_line` is the string used to start the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/pid) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/object/properties/pid): Process ID of the process.

`pid` is the process ID of the process.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/item): Output of /usr/bin/ps.

See ps(1).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/unix.process.schema.json#/$defs/require): The comparison fields define the different metadata associated with a UNIX process.

This includes the command line, pid, ppid, priority, and user id.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
