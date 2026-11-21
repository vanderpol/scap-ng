# Native Variable declarations and retained OVAL transformations

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

SCAP-NG 0.4.1 native Variable declarations. Value type, collection cardinality, and observation status are separate semantic dimensions.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `declaration` | object | Definition | Declare a native Variable with kind and expression. | [/$defs/declaration](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration) |
| `expression` | object | Definition | **Unresolved description** | [/$defs/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression) |

## `/$defs/declaration`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Use `local` for a derived value or `constant` for a literal declaration. | [/$defs/declaration/properties/kind](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/kind) |
| `expression` | object | 1..1 (required) | Expression that supplies this Variable’s values. | [/$defs/declaration/properties/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/expression) |
| `title` | null, string | 0..1 | Optional author-facing title for this Variable. | [/$defs/declaration/properties/title](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/title) |

## `/$defs/expression/oneOf/0`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `literal` | array, boolean, number, object, string | 1..1 (required) | A scalar, ordered list, or explicitly typed value. | [/$defs/expression/oneOf/0/properties/literal](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal) |

## `/$defs/expression/oneOf/1`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable` | string | 1..1 (required) | Reference another named Variable. | [/$defs/expression/oneOf/1/properties/variable](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/1/properties/variable) |

## `/$defs/expression/oneOf/2`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input` | string | 1..1 (required) | Reference a typed Assessment Input from the invocation's policy binding. | [/$defs/expression/oneOf/2/properties/input](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/input) |

## `/$defs/expression/oneOf/3`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `values` | object | 1..1 (required) | Read the selected field from the collected Object. | [/$defs/expression/oneOf/3/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/values) |

## `/$defs/expression/oneOf/3/properties/values`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `object` | object, string | 1..1 (required) | Object source whose collected Items supply the field values. | [/$defs/expression/oneOf/3/properties/values/properties/object](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/values/properties/object) |
| `field` | string | 1..1 (required) | Name of the collected field to read from each collected Item. | [/$defs/expression/oneOf/3/properties/values/properties/field](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/values/properties/field) |

## `/$defs/expression/oneOf/4`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `to_integer` | object | 1..1 (required) | Explicit elementwise OVAL xsd:integer decimal conversion. | [/$defs/expression/oneOf/4/properties/to_integer](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/to_integer) |

## `/$defs/expression/oneOf/5`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `time_difference` | object | 1..1 (required) | Parse OVAL 5.12.3 time formats in UTC and return integer seconds. | [/$defs/expression/oneOf/5/properties/time_difference](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/time_difference) |

## `/$defs/expression/oneOf/5/properties/time_difference`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `values` | array | 1..1 (required) | One operand computes current UTC minus that value; two operands compute first minus second. | [/$defs/expression/oneOf/5/properties/time_difference/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/time_difference/properties/values) |
| `format_1` | string | 0..1 | **Unresolved description** | [/$defs/expression/oneOf/5/properties/time_difference/properties/format_1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/time_difference/properties/format_1) |
| `format_2` | string | 0..1 | **Unresolved description** | [/$defs/expression/oneOf/5/properties/time_difference/properties/format_2](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/time_difference/properties/format_2) |

## `/$defs/expression/oneOf/6`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `concat` | array | 1..1 (required) | **Semantic hold.** Existing wording requires a native contract decision; see details. | [/$defs/expression/oneOf/6/properties/concat](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/6/properties/concat) |

## `/$defs/expression/oneOf/7`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `regex_capture` | object | 1..1 (required) | Capture text from each input string using the first capturing group. | [/$defs/expression/oneOf/7/properties/regex_capture](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/regex_capture) |

## `/$defs/expression/oneOf/7/properties/regex_capture`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `pattern` | string | 1..1 (required) | Regular expression containing the capture group to return. | [/$defs/expression/oneOf/7/properties/regex_capture/properties/pattern](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/regex_capture/properties/pattern) |
| `value` | object | 1..1 (required) | Expression producing the string value(s) to search. | [/$defs/expression/oneOf/7/properties/regex_capture/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/regex_capture/properties/value) |

## `/$defs/expression/oneOf/8`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `unique` | array, object | 1..1 (required) | Remove duplicate scalar values from one expression or from multiple ordered component populations. | [/$defs/expression/oneOf/8/properties/unique](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/8/properties/unique) |

## `/$defs/expression/oneOf/9`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `count` | object | 1..1 (required) | Evaluate the nested expression and return the number of values it produces as one integer. | [/$defs/expression/oneOf/9/properties/count](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/9/properties/count) |

## `/$defs/expression/oneOf/10`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `split` | object | 1..1 (required) | Split each input string on the explicit literal delimiter. | [/$defs/expression/oneOf/10/properties/split](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/split) |

## `/$defs/expression/oneOf/10/properties/split`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `delimiter` | string | 1..1 (required) | Literal delimiter; an empty delimiter is literal, not a regular expression. | [/$defs/expression/oneOf/10/properties/split/properties/delimiter](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/split/properties/delimiter) |
| `value` | object | 1..1 (required) | Expression producing string values to split independently. | [/$defs/expression/oneOf/10/properties/split/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/10/properties/split/properties/value) |

## `/$defs/expression/oneOf/11`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `substring` | object | 1..1 (required) | Extract a substring from each input string using explicit signed 32-bit source options. | [/$defs/expression/oneOf/11/properties/substring](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/substring) |

## `/$defs/expression/oneOf/11/properties/substring`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `substring_start` | integer | 1..1 (required) | Signed 32-bit OVAL start position; evaluation applies the source one-based boundary rules. | [/$defs/expression/oneOf/11/properties/substring/properties/substring_start](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/substring/properties/substring_start) |
| `substring_length` | integer | 1..1 (required) | Signed 32-bit length; negative or oversized lengths retain the source remainder behavior. | [/$defs/expression/oneOf/11/properties/substring/properties/substring_length](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/substring/properties/substring_length) |
| `value` | object | 1..1 (required) | Expression producing string values to slice independently. | [/$defs/expression/oneOf/11/properties/substring/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/11/properties/substring/properties/value) |

## `/$defs/expression/oneOf/12`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `arithmetic` | object | 1..1 (required) | Add or multiply two or more numeric populations over the source Cartesian product. | [/$defs/expression/oneOf/12/properties/arithmetic](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/arithmetic) |

## `/$defs/expression/oneOf/12/properties/arithmetic`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `arithmetic_operation` | string | 1..1 (required) | Numeric addition or multiplication; no boolean or string coercion. | [/$defs/expression/oneOf/12/properties/arithmetic/properties/arithmetic_operation](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/arithmetic/properties/arithmetic_operation) |
| `values` | array | 1..1 (required) | Two or more ordered numeric expressions. | [/$defs/expression/oneOf/12/properties/arithmetic/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/arithmetic/properties/values) |

## `/$defs/expression/oneOf/13`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `begin` | object | 1..1 (required) | Retain the source begin-character transformation with one explicit input and character. | [/$defs/expression/oneOf/13/properties/begin](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/13/properties/begin) |

## `/$defs/expression/oneOf/13/properties/begin`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `character` | string | 1..1 (required) | Explicit character used by the source begin operation. | [/$defs/expression/oneOf/13/properties/begin/properties/character](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/13/properties/begin/properties/character) |
| `value` | object | 1..1 (required) | Expression producing string values to test. | [/$defs/expression/oneOf/13/properties/begin/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/13/properties/begin/properties/value) |

## `/$defs/expression/oneOf/14`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `end` | object | 1..1 (required) | Retain the source end-character transformation with one explicit input and character. | [/$defs/expression/oneOf/14/properties/end](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/14/properties/end) |

## `/$defs/expression/oneOf/14/properties/end`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `character` | string | 1..1 (required) | Explicit character used by the source end operation. | [/$defs/expression/oneOf/14/properties/end/properties/character](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/14/properties/end/properties/character) |
| `value` | object | 1..1 (required) | Expression producing string values to test. | [/$defs/expression/oneOf/14/properties/end/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/14/properties/end/properties/value) |

## `/$defs/expression/oneOf/15`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `merge` | object | 1..1 (required) | Combine one or more ordered input populations into one string using an explicit delimiter, sort mode, and order. document preserves flattened input order; other modes sort before joining. | [/$defs/expression/oneOf/15/properties/merge](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/15/properties/merge) |

## `/$defs/expression/oneOf/15/properties/merge`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `delimiter` | string | 1..1 (required) | String inserted between adjacent values. | [/$defs/expression/oneOf/15/properties/merge/properties/delimiter](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/15/properties/merge/properties/delimiter) |
| `sort` | string | 1..1 (required) | `document` preserves input order; `lexical`, `numeric`, and `natural` select the corresponding explicit ordering. | [/$defs/expression/oneOf/15/properties/merge/properties/sort](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/15/properties/merge/properties/sort) |
| `order` | string | 1..1 (required) | Ascending or descending order for the selected sort mode. | [/$defs/expression/oneOf/15/properties/merge/properties/order](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/15/properties/merge/properties/order) |
| `values` | array, object | 1..1 (required) | Expression or ordered component populations to join. | [/$defs/expression/oneOf/15/properties/merge/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/15/properties/merge/properties/values) |

## Advanced constraints

[Local constraints](../advanced/variable-expression.md) and [complete JSON Schema](../../../proposed-schema/documentation/variable-expression.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
