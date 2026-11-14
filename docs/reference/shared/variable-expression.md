# Native Variable declarations and retained OVAL transformations

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Declare typed local or constant Variables from literal data, other Variables, collected Object fields, or explicit recursive transformations. Active 0.4 forms preserve source operand order, collection multiplicity, empty values, and evaluation status; datatype compatibility and status propagation are checked separately by semantic validation or a qualified runtime.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `declaration` | object | Definition | Declares a constant or locally derived Variable. | [/$defs/declaration](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration) |
| `expression` | object | Definition | One retained expression form: literal, Variable reference, Object field values, concat, regex_capture, unique, or merge. | [/$defs/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression) |

## `/$defs/declaration`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Selects a constant or locally derived Variable. | [/$defs/declaration/properties/kind](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/kind) |
| `expression` | object | 1..1 (required) | Defines how this Variable's values are obtained. | [/$defs/declaration/properties/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/expression) |
| `title` | null, string | 0..1 | Optional author-facing title for this Variable. | [/$defs/declaration/properties/title](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/title) |

## `/$defs/expression/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `literal` | array, boolean, number, object, string | 1..1 (required) | Supplies a literal value, list of values, or explicitly typed value. | [/$defs/expression/oneOf/0/properties/literal](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal) |

## `/$defs/expression/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable` | string | 1..1 (required) | Reference another named Variable. | [/$defs/expression/oneOf/1/properties/variable](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/1/properties/variable) |

## `/$defs/expression/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `values` | object | 1..1 (required) | Reads a field from the Items collected by an Object. | [/$defs/expression/oneOf/2/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values) |

## `/$defs/expression/oneOf/2/properties/values`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `object` | object, string | 1..1 (required) | Object source whose collected Items supply the field values. | [/$defs/expression/oneOf/2/properties/values/properties/object](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values/properties/object) |
| `field` | string | 1..1 (required) | Name of the collected field to read from each collected Item. | [/$defs/expression/oneOf/2/properties/values/properties/field](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values/properties/field) |

## `/$defs/expression/oneOf/3`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `concat` | array | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/3/properties/concat](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat) |

## `/$defs/expression/oneOf/4`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `regex_capture` | object | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/4/properties/regex_capture](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture) |

## `/$defs/expression/oneOf/4/properties/regex_capture`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `pattern` | string | 1..1 (required) | Regular expression containing the capture group to return. | [/$defs/expression/oneOf/4/properties/regex_capture/properties/pattern](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture/properties/pattern) |
| `value` | object | 1..1 (required) | Expression producing the string value(s) to search. | [/$defs/expression/oneOf/4/properties/regex_capture/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture/properties/value) |

## `/$defs/expression/oneOf/5`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `unique` | array, object | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/5/properties/unique](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/unique) |

## `/$defs/expression/oneOf/6`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `count` | object | 1..1 (required) | Evaluate the nested expression and return the number of values it produces as one integer. | [/$defs/expression/oneOf/6/properties/count](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/6/properties/count) |

## `/$defs/expression/oneOf/7`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `split` | object | 1..1 (required) | Split each input string on the explicit literal delimiter. | [/$defs/expression/oneOf/7/properties/split](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/split) |

## `/$defs/expression/oneOf/7/properties/split`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `delimiter` | string | 1..1 (required) | Literal delimiter; an empty delimiter is literal, not a regular expression. | [/$defs/expression/oneOf/7/properties/split/properties/delimiter](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/split/properties/delimiter) |
| `value` | object | 1..1 (required) | Expression producing string values to split independently. | [/$defs/expression/oneOf/7/properties/split/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/split/properties/value) |

## `/$defs/expression/oneOf/8`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `substring` | object | 1..1 (required) | Extract a substring from each input string using explicit signed 32-bit source options. | [/$defs/expression/oneOf/8/properties/substring](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/8/properties/substring) |

## `/$defs/expression/oneOf/8/properties/substring`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `substring_start` | integer | 1..1 (required) | Signed 32-bit OVAL start position; evaluation applies the source one-based boundary rules. | [/$defs/expression/oneOf/8/properties/substring/properties/substring_start](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/8/properties/substring/properties/substring_start) |
| `substring_length` | integer | 1..1 (required) | Signed 32-bit length; negative or oversized lengths retain the source remainder behavior. | [/$defs/expression/oneOf/8/properties/substring/properties/substring_length](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/8/properties/substring/properties/substring_length) |
| `value` | object | 1..1 (required) | Expression producing string values to slice independently. | [/$defs/expression/oneOf/8/properties/substring/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/8/properties/substring/properties/value) |

## `/$defs/expression/oneOf/9`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `arithmetic` | object | 1..1 (required) | Add or multiply two or more numeric populations over the source Cartesian product. | [/$defs/expression/oneOf/9/properties/arithmetic](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/9/properties/arithmetic) |

## `/$defs/expression/oneOf/9/properties/arithmetic`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `arithmetic_operation` | string | 1..1 (required) | Numeric addition or multiplication; no boolean or string coercion. | [/$defs/expression/oneOf/9/properties/arithmetic/properties/arithmetic_operation](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/9/properties/arithmetic/properties/arithmetic_operation) |
| `values` | array | 1..1 (required) | Two or more ordered numeric expressions. | [/$defs/expression/oneOf/9/properties/arithmetic/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/9/properties/arithmetic/properties/values) |

## `/$defs/expression/oneOf/10`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `begin` | object | 1..1 (required) | Retain the source begin-character transformation with one explicit input and character. | [/$defs/expression/oneOf/10/properties/begin](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/begin) |

## `/$defs/expression/oneOf/10/properties/begin`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `character` | string | 1..1 (required) | Explicit character used by the source begin operation. | [/$defs/expression/oneOf/10/properties/begin/properties/character](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/begin/properties/character) |
| `value` | object | 1..1 (required) | Expression producing string values to test. | [/$defs/expression/oneOf/10/properties/begin/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/begin/properties/value) |

## `/$defs/expression/oneOf/11`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `end` | object | 1..1 (required) | Retain the source end-character transformation with one explicit input and character. | [/$defs/expression/oneOf/11/properties/end](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/end) |

## `/$defs/expression/oneOf/11/properties/end`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `character` | string | 1..1 (required) | Explicit character used by the source end operation. | [/$defs/expression/oneOf/11/properties/end/properties/character](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/end/properties/character) |
| `value` | object | 1..1 (required) | Expression producing string values to test. | [/$defs/expression/oneOf/11/properties/end/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/end/properties/value) |

## `/$defs/expression/oneOf/12`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `merge` | object | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/12/properties/merge](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge) |

## `/$defs/expression/oneOf/12/properties/merge`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `delimiter` | string | 1..1 (required) | String inserted between adjacent values. | [/$defs/expression/oneOf/12/properties/merge/properties/delimiter](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge/properties/delimiter) |
| `sort` | string | 1..1 (required) | `document` preserves input order; `lexical`, `numeric`, and `natural` select the corresponding explicit ordering. | [/$defs/expression/oneOf/12/properties/merge/properties/sort](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge/properties/sort) |
| `order` | string | 1..1 (required) | Ascending or descending order for the selected sort mode. | [/$defs/expression/oneOf/12/properties/merge/properties/order](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge/properties/order) |
| `values` | array, object | 1..1 (required) | Expression or ordered component populations to join. | [/$defs/expression/oneOf/12/properties/merge/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge/properties/values) |

## Advanced constraints

[Local constraints](../advanced/variable-expression.md) and [complete JSON Schema](../../../proposed-schema/documentation/variable-expression.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
