# Draft Assessment expression execution result 0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Expression-stage result, not a complete Assessment Result or scanner result package.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/outcome](../../../proposed-schema/documentation/expression-result.schema.json#/properties/outcome) |
| `evaluation_scope` | string | 1..1 (required) | Identifies this result as an Assessment-expression evaluation. | [/properties/evaluation_scope](../../../proposed-schema/documentation/expression-result.schema.json#/properties/evaluation_scope) |
| `executed_tests` | array | 1..1 (required) | Test references recorded as executed during this evaluation. | [/properties/executed_tests](../../../proposed-schema/documentation/expression-result.schema.json#/properties/executed_tests) |
| `context` | object | 1..1 (required) | Target and invocation references associated with this expression result. | [/properties/context](../../../proposed-schema/documentation/expression-result.schema.json#/properties/context) |
| `diagnostics` | array | 1..1 (required) | Diagnostic entries associated with this result. | [/properties/diagnostics](../../../proposed-schema/documentation/expression-result.schema.json#/properties/diagnostics) |
| `trace` | array | 1..1 (required) | Evaluation steps recorded for this expression result. | [/properties/trace](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace) |
| `invocations` | array | 1..1 (required) | Invocation records associated with this expression result. | [/properties/invocations](../../../proposed-schema/documentation/expression-result.schema.json#/properties/invocations) |
| `outcome` | string | Definition | Expression outcome encoded with the schema string vocabulary. | [/$defs/outcome](../../../proposed-schema/documentation/expression-result.schema.json#/$defs/outcome) |

## `/properties/context`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `target` | string | 1..1 (required) | Target reference associated with the expression evaluation. | [/properties/context/properties/target](../../../proposed-schema/documentation/expression-result.schema.json#/properties/context/properties/target) |
| `invocation_ref` | string | 1..1 (required) | Reference to the expression invocation. | [/properties/context/properties/invocation_ref](../../../proposed-schema/documentation/expression-result.schema.json#/properties/context/properties/invocation_ref) |

## `/properties/diagnostics/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `code` | string | 1..1 (required) | Machine-readable diagnostic code. | [/properties/diagnostics/items/properties/code](../../../proposed-schema/documentation/expression-result.schema.json#/properties/diagnostics/items/properties/code) |
| `test` | string | 1..1 (required) | Test reference associated with this diagnostic. | [/properties/diagnostics/items/properties/test](../../../proposed-schema/documentation/expression-result.schema.json#/properties/diagnostics/items/properties/test) |

## `/properties/trace/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `path` | string | 1..1 (required) | Recorded location of this step in the expression structure. | [/properties/trace/items/properties/path](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/path) |
| `kind` | string | 1..1 (required) | Kind of evaluation step recorded in the expression trace. | [/properties/trace/items/properties/kind](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/kind) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/trace/items/properties/outcome](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/outcome) |
| `condition_outcome` | string | Conditional (at most 1) | Reported outcome of the condition. | [/properties/trace/items/properties/condition_outcome](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/condition_outcome) |
| `selected_branch` | null, string | Conditional (at most 1) | Branch selected after evaluating the condition. | [/properties/trace/items/properties/selected_branch](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/selected_branch) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/trace/items/properties/reason](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/reason) |
| `test` | string | Conditional (at most 1) | Test reference associated with this trace step. | [/properties/trace/items/properties/test](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/test) |
| `assessment` | string | Conditional (at most 1) | Assessment reference associated with this trace step. | [/properties/trace/items/properties/assessment](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/assessment) |
| `alias` | string | Conditional (at most 1) | Dependency alias associated with this trace step. | [/properties/trace/items/properties/alias](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/alias) |
| `reused` | boolean | Conditional (at most 1) | Whether this result reuses prior execution evidence. | [/properties/trace/items/properties/reused](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/reused) |
| `invocation_ref` | string | Conditional (at most 1) | Reference to the expression invocation. | [/properties/trace/items/properties/invocation_ref](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/invocation_ref) |
| `owner_invocation_ref` | string | 1..1 (required) | Reference to the invocation owning this result. | [/properties/trace/items/properties/owner_invocation_ref](../../../proposed-schema/documentation/expression-result.schema.json#/properties/trace/items/properties/owner_invocation_ref) |

## Advanced constraints

[Local constraints](../advanced/expression-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/expression-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
