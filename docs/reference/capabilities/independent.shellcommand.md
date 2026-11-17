# independent.shellcommand

Proposed documentation; frozen 0.4.1 validation is unchanged.

Collects evidence produced by an authored command. The Object declares an interpreter, command text and optional output pattern; Require evaluates the collected exit status, output lines and captured text.

## Usage and safety guidance

Treat a content-supplied command as executable code. Review its effects on the target and the privileges of the scanner process before allowing execution. Commands may run in a privileged deployment context; choose commands that do not harm the target system.

Prefer robust commands with bounded, predictable output. Avoid fragile command strings that can fail noisily or produce excessive standard output or standard error. Well-formed output makes the resulting evidence easier to interpret.

Prefer executables supplied by the target operating system. Identify and review any external executable dependencies rather than assuming they are installed or introducing them silently.

Establish content trust, integrity verification and signing policy before enabling command execution. The source's mandatory signing rule is historical; no additional native signing requirement is established by this documentation.

## Evidence and contract boundaries

Standard output and standard error have separate evidence fields. The Object declares whether nonzero exit status or standard-error output is to be treated as a collection error; these acquisition controls are distinct from Require comparisons.

Native contracts for command-form restrictions, an omitted interpreter, output splitting and cardinality, empty output, unavailable interpreters and error propagation remain unresolved. The original single-Item and empty-output status conventions are retained in the semantic ledger rather than adopted as native behavior.

**Contract status: unresolved.** Required collection parameters differ between capability metadata and schema validation. Execution, line splitting, empty output, unavailable interpreters, stderr and nonzero-exit result aggregation remain unresolved; do not infer runtime behavior from these field meanings. See issue #29 and the existing semantic research.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/independent.shellcommand.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `independent.shellcommand` to define a shell to use (e.g. sh, bash, ksh, etc.), a command (or shell script) to be run, and a pattern to filter result lines.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/filters) |
| `shell` | string | 0..1 | Interpreter requested for command execution. | [/$defs/object/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/shell) |
| `command` | string | 0..1 | Command text supplied to the interpreter. | [/$defs/object/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/command) |
| `pattern` | string | 0..1 | Regular expression selecting standard-output lines. | [/$defs/object/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/pattern) |
| `error_if_exit_status_not_0` | boolean | 0..1 | Whether a nonzero exit status is treated as a collection error. | [/$defs/object/properties/error_if_exit_status_not_0](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_exit_status_not_0) |
| `error_if_stderr_exists` | boolean | 0..1 | Whether standard-error output is treated as a collection error. | [/$defs/object/properties/error_if_stderr_exists](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_stderr_exists) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `shell` | string | 0..1 | Interpreter requested for command execution. | [/$defs/meanings/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/shell) |
| `command` | string | 0..1 | Command text supplied to the interpreter. | [/$defs/meanings/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/command) |
| `pattern` | string | 0..1 | Regular expression selecting standard-output lines. | [/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/pattern) |
| `exit_status` | integer | 0..1 | Process exit status. | [/$defs/meanings/properties/exit_status](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/exit_status) |
| `stdout_line` | string | 0..1 | A line from standard output. | [/$defs/meanings/properties/stdout_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stdout_line) |
| `subexpression` | 12 declared types; see details | 0..1 | Text captured by a parenthesized group in the output pattern. | [/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/subexpression) |
| `stderr_line` | string | 0..1 | A line from standard error. | [/$defs/meanings/properties/stderr_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stderr_line) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain the entities that are used to check the values returned by the Object.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `stdout_line` | 12 declared types; see details | 0..1 | A line from standard output. | [/$defs/meanings/properties/stdout_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stdout_line) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/independent.shellcommand.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`shell` | {"allow_variable": true, "enum": ["sh", "bash", "csh", "ksh", "zsh", "cmd", "powershell", "pwsh"], "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`command` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`pattern` | {"allow_variable": true, "required": false, "type": "string"} | native-mapping-reviewed |
| Object.`error_if_exit_status_not_0` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`error_if_stderr_exists` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Item.`subexpression` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

## Examples

**Illustrative expected outcomes; native evaluation unverified.** Syntax validation is reported separately from evaluation. For these compliance teaching cases only, technical `true` is labelled Pass and `false` Fail; a consuming Rule defines policy outcomes. Items are explicit synthetic evidence, not observations from a scanned host.

Both cases use this native Test (inline Object and Require):

```yaml
tests:
  independent-shellcommand-example-test:
    test_title: Compare the explicitly supplied stdout_line
    capability: independent.shellcommand
    object: {shell: sh, command: /usr/bin/getconf LONG_BIT, error_if_exit_status_not_0: false, error_if_stderr_exists: false}
    require:
      item_requirement: {items_found: one_or_more, items_satisfying: every}
      field_requirement: {values_found: one_or_more, values_matching: every}
      fields:
        stdout_line: {datatype: string, equals: '64'}
    reported_elements: all
evaluate: {test: independent-shellcommand-example-test}
```

### Pass — expected `true` (unverified)

The supplied stdout_line string is '64', so the string equality to "64" matches; the command was not executed for this fixture.

```yaml
collection_result:
  id: independent-shellcommand-pass-collection
  capability: independent.shellcommand
  status: complete
  item_refs: [independent-shellcommand-pass-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: independent-shellcommand-pass-item
  capability: independent.shellcommand
  status: exists
  fields:
    exit_status: {datatype: integer, status: exists, value: 0}
    stdout_line: {datatype: string, status: exists, value: '64'}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.1/independent.shellcommand.pass.yaml).

### Fail — expected `false` (unverified)

The supplied stdout_line string is '32', so the string equality to "64" does not match; the command was not executed for this fixture.

```yaml
collection_result:
  id: independent-shellcommand-fail-collection
  capability: independent.shellcommand
  status: complete
  item_refs: [independent-shellcommand-fail-item]
  logical_complete: true
  population_complete: true
collected_items:
- id: independent-shellcommand-fail-item
  capability: independent.shellcommand
  status: exists
  fields:
    exit_status: {datatype: integer, status: exists, value: 0}
    stdout_line: {datatype: string, status: exists, value: '32'}
  provenance: {kind: synthetic-documentation-fixture}
```

[Complete version-pinned fixture](../../../examples/paired/v0.4.1/independent.shellcommand.fail.yaml).

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
