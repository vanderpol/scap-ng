# expression-invocation.schema

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/assessment) |
| `invocation_ref` | string | 1..1 (required) | Reference to the expression invocation. | [/properties/invocation_ref](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/invocation_ref) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/outcome](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/outcome) |
| `executed_tests` | array | 1..1 (required) | **Unresolved description** | [/properties/executed_tests](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/executed_tests) |
| `trace` | array | 1..1 (required) | **Unresolved description** | [/properties/trace](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace) |
| `diagnostics` | array | 1..1 (required) | Diagnostic entries associated with this result. | [/properties/diagnostics](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/diagnostics) |
| `binding_set_id` | string | Conditional (at most 1) | Digest of immutable effective bindings and explicit invocation identity; never an inferred empty binding. | [/properties/binding_set_id](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/binding_set_id) |
| `input_presence_version` | integer | Conditional (at most 1) | **Unresolved description** | [/properties/input_presence_version](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/input_presence_version) |
| `outcome` | string | Definition | **Unresolved description** | [/$defs/outcome](../../../proposed-schema/documentation/expression-invocation.schema.json#/$defs/outcome) |

## `/properties/trace/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `path` | string | 1..1 (required) | **Unresolved description** | [/properties/trace/items/properties/path](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/path) |
| `kind` | string | 1..1 (required) | Kind of evaluation step recorded in the invocation trace. | [/properties/trace/items/properties/kind](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/kind) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/trace/items/properties/outcome](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/outcome) |
| `condition_outcome` | string | Conditional (at most 1) | Reported outcome of the condition. | [/properties/trace/items/properties/condition_outcome](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/condition_outcome) |
| `selected_branch` | null, string | Conditional (at most 1) | Branch selected after evaluating the condition. | [/properties/trace/items/properties/selected_branch](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/selected_branch) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/trace/items/properties/reason](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/reason) |
| `test` | string | Conditional (at most 1) | **Unresolved description** | [/properties/trace/items/properties/test](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/test) |
| `assessment` | string | Conditional (at most 1) | **Unresolved description** | [/properties/trace/items/properties/assessment](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/assessment) |
| `alias` | string | Conditional (at most 1) | **Unresolved description** | [/properties/trace/items/properties/alias](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/alias) |
| `reused` | boolean | Conditional (at most 1) | Whether this result reuses prior execution evidence. | [/properties/trace/items/properties/reused](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/reused) |
| `invocation_ref` | string | Conditional (at most 1) | Reference to the expression invocation. | [/properties/trace/items/properties/invocation_ref](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/invocation_ref) |
| `owner_invocation_ref` | string | 1..1 (required) | Reference to the invocation owning this result. | [/properties/trace/items/properties/owner_invocation_ref](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/owner_invocation_ref) |
| `input` | string | Conditional (at most 1) | Identifier of the Input supplying the value. | [/properties/trace/items/properties/input](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/input) |
| `binding_set_id` | string | Conditional (at most 1) | Digest of immutable effective bindings and explicit invocation identity; never an inferred empty binding. | [/properties/trace/items/properties/binding_set_id](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/binding_set_id) |
| `source` | string | Conditional (at most 1) | **Unresolved description** | [/properties/trace/items/properties/source](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/source) |
| `source_ref` | null, string | 0..1 | **Unresolved description** | [/properties/trace/items/properties/source_ref](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/source_ref) |
| `follow_up` | string | 0..1 | **Unresolved description** | [/properties/trace/items/properties/follow_up](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/follow_up) |
| `branch_index` | integer | 0..1 | Initial if is index0; ordered else_if branches follow. | [/properties/trace/items/properties/branch_index](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/branch_index) |
| `condition_path` | string | 0..1 | **Unresolved description** | [/properties/trace/items/properties/condition_path](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/trace/items/properties/condition_path) |

## `/properties/diagnostics/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `code` | string | 1..1 (required) | Machine-readable diagnostic code. | [/properties/diagnostics/items/properties/code](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/diagnostics/items/properties/code) |
| `test` | string | 1..1 (required) | **Unresolved description** | [/properties/diagnostics/items/properties/test](../../../proposed-schema/documentation/expression-invocation.schema.json#/properties/diagnostics/items/properties/test) |

## Advanced constraints

[Local constraints](../advanced/expression-invocation.md) and [complete JSON Schema](../../../proposed-schema/documentation/expression-invocation.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
