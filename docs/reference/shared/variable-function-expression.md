# Inactive canonical-call migration candidate

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

This isolated schema documents a broader migration shape but is not referenced by Assessment. It does not authorize native functions, runtime support, or editor completion; active authoring uses variable-expression.schema.json.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `expression` | object | Definition | **Unresolved description** | [/$defs/expression](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression) |
| `function_call` | object | Definition | **Unresolved description** | [/$defs/function_call](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/function_call) |
| `time_format` | string | Definition | **Unresolved description** | [/$defs/time_format](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/time_format) |

## `/$defs/expression/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable` | string | 1..1 (required) | Identifier of the Variable whose values are referenced. | [/$defs/expression/oneOf/0/properties/variable](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression/oneOf/0/properties/variable) |

## `/$defs/expression/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `literal` | object, string | 1..1 (required) | **Unresolved description** | [/$defs/expression/oneOf/1/properties/literal](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression/oneOf/1/properties/literal) |

## `/$defs/expression/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `values` | object | 1..1 (required) | **Unresolved description** | [/$defs/expression/oneOf/2/properties/values](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression/oneOf/2/properties/values) |

## `/$defs/expression/oneOf/2/properties/values`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `object` | object, string | 1..1 (required) | **Unresolved description** | [/$defs/expression/oneOf/2/properties/values/properties/object](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression/oneOf/2/properties/values/properties/object) |
| `field` | string | 1..1 (required) | **Unresolved description** | [/$defs/expression/oneOf/2/properties/values/properties/field](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/expression/oneOf/2/properties/values/properties/field) |

## `/$defs/function_call`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `function` | object | 1..1 (required) | **Unresolved description** | [/$defs/function_call/properties/function](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/function_call/properties/function) |

## `/$defs/function_call/properties/function`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 1..1 (required) | **Unresolved description** | [/$defs/function_call/properties/function/properties/name](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/function_call/properties/function/properties/name) |
| `arguments` | array | 1..1 (required) | **Unresolved description** | [/$defs/function_call/properties/function/properties/arguments](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/function_call/properties/function/properties/arguments) |
| `options` | object | 1..1 (required) | **Unresolved description** | [/$defs/function_call/properties/function/properties/options](../../../proposed-schema/documentation/variable-function-expression.schema.json#/$defs/function_call/properties/function/properties/options) |

## Advanced constraints

[Local constraints](../advanced/variable-function-expression.md) and [complete JSON Schema](../../../proposed-schema/documentation/variable-function-expression.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
