# independent.shellcommand — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#): Collects evidence produced by an authored command. The Object declares an interpreter, command text and optional output pattern; Require evaluates the collected exit status, output lines and captured text.

## Usage and safety guidance

Treat a content-supplied command as executable code. Review its effects on the target and the privileges of the scanner process before allowing execution. Commands may run in a privileged deployment context; choose commands that do not harm the target system.

Prefer robust commands with bounded, predictable output. Avoid fragile command strings that can fail noisily or produce excessive standard output or standard error. Well-formed output makes the resulting evidence easier to interpret.

Prefer executables supplied by the target operating system. Identify and review any external executable dependencies rather than assuming they are installed or introducing them silently.

Establish content trust, integrity verification and signing policy before enabling command execution. The source's mandatory signing rule is historical; no additional native signing requirement is established by this documentation.

## Evidence and contract boundaries

Standard output and standard error have separate evidence fields. The Object declares whether nonzero exit status or standard-error output is to be treated as a collection error; these acquisition controls are distinct from Require comparisons.

Native contracts for command-form restrictions, an omitted interpreter, output splitting and cardinality, empty output, unavailable interpreters and error propagation remain unresolved. The original single-Item and empty-output status conventions are retained in the semantic ledger rather than adopted as native behavior.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/shell) | {"declared_values_not_new_validation_restrictions": ["sh", "bash", "csh", "ksh", "zsh", "cmd", "powershell", "pwsh"]} | native-mapping-reviewed |

[/$defs/meanings/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/shell): Interpreter requested for command execution.

`shell` defines the specific shell to use (e.g. bash, csh, ksh, etc.).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/command) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/command): Command text supplied to the interpreter.

`command` specifies the command string to be run on the target system, which could be a single executable/binary or a one-liner which manipulates the output from one or more executables/binaries.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/pattern) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/exit_status](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/exit_status) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/exit_status](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/exit_status): Process exit status.

`exit_status` represents the exit status returned by the system for the execution of the object command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/stdout_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stdout_line) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/subexpression) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/subexpression): Text captured by a parenthesized group in the output pattern.

`subexpression` represents the value of a subexpression in the specified pattern.

`subexpression` represents a value to test against the subexpression in the specified pattern.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/stderr_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stderr_line) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/stderr_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stderr_line): A line from standard error.

`stderr_line` contains a single line of any output from STDERR.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/shell) | {"declaration_only": {"type": "string", "enum": ["sh", "bash", "csh", "ksh", "zsh", "cmd", "powershell", "pwsh"], "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/command) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/pattern) | {"declaration_only": {"type": "string", "required": false, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/error_if_exit_status_not_0](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_exit_status_not_0) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/object/properties/error_if_stderr_exists](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_stderr_exists) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
