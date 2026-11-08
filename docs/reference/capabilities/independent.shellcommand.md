# independent.shellcommand

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Required collection parameters differ between capability metadata and schema validation. Execution, line splitting, empty output, unavailable interpreters, stderr and nonzero-exit result aggregation remain unresolved; do not infer runtime behavior from these field meanings. See issue #29 and the existing semantic research.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/filters) |
| `shell` | See schema | 0..1 | Interpreter requested for command execution. | [/$defs/object/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/shell) |
| `command` | See schema | 0..1 | Command text supplied to the interpreter. | [/$defs/object/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/command) |
| `pattern` | See schema | 0..1 | Regular expression selecting standard-output lines. | [/$defs/object/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/pattern) |
| `error_if_exit_status_not_0` | See schema | 0..1 | Whether a nonzero exit status is treated as a collection error. | [/$defs/object/properties/error_if_exit_status_not_0](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_exit_status_not_0) |
| `error_if_stderr_exists` | See schema | 0..1 | Whether standard-error output is treated as a collection error. | [/$defs/object/properties/error_if_stderr_exists](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/object/properties/error_if_stderr_exists) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `shell` | array, object | 0..1 | Interpreter requested for command execution. | [/$defs/meanings/properties/shell](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/shell) |
| `command` | array, object | 0..1 | Command text supplied to the interpreter. | [/$defs/meanings/properties/command](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/command) |
| `pattern` | array, object | 0..1 | Regular expression selecting standard-output lines. | [/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/pattern) |
| `exit_status` | array, object | 0..1 | Process exit status. | [/$defs/meanings/properties/exit_status](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/exit_status) |
| `stdout_line` | array, object | 0..1 | A line from standard output. | [/$defs/meanings/properties/stdout_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stdout_line) |
| `subexpression` | array, object | 0..1 | Text captured by a parenthesized group in the output pattern. | [/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/subexpression) |
| `stderr_line` | array, object | 0..1 | A line from standard error. | [/$defs/meanings/properties/stderr_line](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json#/$defs/meanings/properties/stderr_line) |

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

[Local schema constraints](../advanced/independent.shellcommand.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`shell` | {"allow_variable": true, "enum": ["sh", "bash", "csh", "ksh", "zsh", "cmd", "powershell", "pwsh"], "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`command` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`pattern` | {"allow_variable": true, "required": false, "type": "string"} | native-mapping-reviewed |
| Object.`error_if_exit_status_not_0` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`error_if_stderr_exists` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Item.`shell` | string | native-mapping-reviewed |
| Item.`command` | string | native-mapping-reviewed |
| Item.`pattern` | string | native-mapping-reviewed |
| Item.`exit_status` | integer | native-mapping-reviewed |
| Item.`stdout_line` | string | native-mapping-reviewed |
| Item.`subexpression` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | native-mapping-reviewed |
| Item.`stderr_line` | string | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.shellcommand.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
