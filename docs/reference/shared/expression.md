# Draft SCAP-NG 0.4.0 automated expression

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

SCAP-NG 0.4.0 Test-result expression grammar. Logical and/or/one/xor are canonical; legacy all/any/odd are invalid. Item cardinalities are separate.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `expression` | object | Definition | Explicit new-authoring selection for assessment logic; applies only in explicit logical group. | [/$defs/expression](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression) |
| `input_presence` | object | Definition | **Unresolved description** | [/$defs/input_presence](../../../proposed-schema/documentation/expression.schema.json#/$defs/input_presence) |
| `condition` | object | Definition | **Unresolved description** | [/$defs/condition](../../../proposed-schema/documentation/expression.schema.json#/$defs/condition) |

## `/$defs/expression/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `test` | string | 1..1 (required) | Uses a named Test’s outcome in this expression. | [/$defs/expression/oneOf/0/properties/test](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/0/properties/test) |

## `/$defs/expression/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 1..1 (required) | Uses a referenced Assessment’s outcome in this expression. | [/$defs/expression/oneOf/1/properties/assessment](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/1/properties/assessment) |

## `/$defs/expression/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `if` | object | 1..1 (required) | Tests the condition that selects a conditional branch. | [/$defs/expression/oneOf/2/properties/if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/if) |
| `then` | object | 1..1 (required) | Explicit new-authoring selection for assessment logic; applies only in explicit logical group. | [/$defs/expression/oneOf/2/properties/then](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/then) |
| `else_if` | array | 0..1 | Selects the first true alternative branch when preceding conditions are false. | [/$defs/expression/oneOf/2/properties/else_if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if) |
| `else` | object | 1..1 (required) | Explicit new-authoring selection for assessment logic; applies only in explicit logical group. | [/$defs/expression/oneOf/2/properties/else](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else) |

## `/$defs/expression/oneOf/2/properties/else_if/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `if` | object | 1..1 (required) | **Unresolved description** | [/$defs/expression/oneOf/2/properties/else_if/items/properties/if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if/items/properties/if) |
| `then` | object | 1..1 (required) | Explicit new-authoring selection for assessment logic; applies only in explicit logical group. | [/$defs/expression/oneOf/2/properties/else_if/items/properties/then](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if/items/properties/then) |

## `/$defs/expression/oneOf/3`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `not` | object | 1..1 (required) | Explicit new-authoring selection for assessment logic; applies only in explicit logical group. | [/$defs/expression/oneOf/3/properties/not](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/3/properties/not) |

## `/$defs/expression/oneOf/4`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `and` | array | 1..1 (required) | Combines expression outcomes using logical AND. | [/$defs/expression/oneOf/4/properties/and](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/4/properties/and) |

## `/$defs/expression/oneOf/5`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `or` | array | 1..1 (required) | Combines expression outcomes using logical OR. | [/$defs/expression/oneOf/5/properties/or](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/5/properties/or) |

## `/$defs/expression/oneOf/6`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `not_evaluated` | object | 1..1 (required) | Declares that this branch cannot be evaluated and provides a reason. | [/$defs/expression/oneOf/6/properties/not_evaluated](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated) |

## `/$defs/expression/oneOf/6/properties/not_evaluated`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `reason` | string | 1..1 (required) | Explanation of the reported outcome. | [/$defs/expression/oneOf/6/properties/not_evaluated/properties/reason](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/properties/reason) |
| `follow_up` | string | 0..1 | What a reviewer or manual follow-up must inspect. | [/$defs/expression/oneOf/6/properties/not_evaluated/properties/follow_up](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/properties/follow_up) |

## `/$defs/expression/oneOf/7`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `not_applicable` | object | 1..1 (required) | Declares that this branch does not apply and provides a reason. | [/$defs/expression/oneOf/7/properties/not_applicable](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable) |

## `/$defs/expression/oneOf/7/properties/not_applicable`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `reason` | string | 1..1 (required) | Explanation of the reported outcome. | [/$defs/expression/oneOf/7/properties/not_applicable/properties/reason](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable/properties/reason) |

## `/$defs/expression/oneOf/8`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `one` | array | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/8/properties/one](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/8/properties/one) |

## `/$defs/expression/oneOf/9`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `xor` | array | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/9/properties/xor](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/9/properties/xor) |

## `/$defs/input_presence`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input_provided` | string | 1..1 (required) | Checks whether a declared Input was supplied, even if its value is empty. | [/$defs/input_presence/properties/input_provided](../../../proposed-schema/documentation/expression.schema.json#/$defs/input_presence/properties/input_provided) |

## Advanced constraints

[Local constraints](../advanced/expression.md) and [complete JSON Schema](../../../proposed-schema/documentation/expression.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
