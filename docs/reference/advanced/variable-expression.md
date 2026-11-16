# Native Variable declarations and retained expressions — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/declaration](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration) | {"type": "object", "required": ["kind", "datatype", "expression"], "additionalProperties": false} | native-grammar-derived |
| [/$defs/declaration/properties/kind](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/kind) | {"enum": ["local", "constant"]} | editorially-approved |

[/$defs/declaration/properties/kind](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/kind): Selects a constant or locally derived Variable.

Editorial receipt: editorial-batch-2.json case 06

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/declaration/properties/datatype](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/datatype) | {} | semantic-hold |

[/$defs/declaration/properties/datatype](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/datatype): Datatype promised by this Variable. The expression must produce compatible values.

The enum is enforced, but full declaration-to-expression compatibility and casts are not established by these witnesses. Retain a semantic hold for the strength of this promise; do not imply coercion or complete tag/payload validation.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/declaration/properties/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/expression) | {} | editorially-approved |

[/$defs/declaration/properties/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/expression): Defines how this Variable's values are obtained.

Editorial receipt: editorial-batch.json case 06

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/declaration/properties/title](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/properties/title) | {"type": ["string", "null"]} | existing-native |
| [/$defs/declaration/allOf/0/if/properties/kind](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/if/properties/kind) | {"const": "constant"} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression) | {"type": "object", "required": ["literal"], "additionalProperties": false} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/0](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/0) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/1) | {"type": "array"} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/1/items](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/1/items) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2) | {"type": "object", "required": ["datatype", "value"], "additionalProperties": false} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/properties/value) | {"type": ["string", "number", "boolean", "array", "object"]} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/if/properties/datatype](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/if/properties/datatype) | {"const": "record"} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/then/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/then/properties/value) | {"type": "object"} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/0](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/0) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1) | {"type": "array"} | existing-native |
| [/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1/items](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1/items) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/expression](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression) | {} | native-grammar-derived |
| [/$defs/expression/oneOf/0](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0) | {"type": "object", "required": ["literal"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal) | {} | editorially-approved |

[/$defs/expression/oneOf/0/properties/literal](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal): Supplies a literal value, list of values, or explicitly typed value.

Editorial receipt: editorial-batch-2.json case 08

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/0](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/0) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/1) | {"type": "array"} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/1/items](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/1/items) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2) | {"type": "object", "required": ["datatype", "value"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/properties/value) | {"type": ["string", "number", "boolean", "array", "object"]} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/if/properties/datatype](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/if/properties/datatype) | {"const": "record"} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/then/properties/value](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/then/properties/value) | {"type": "object"} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/0](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/0) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1) | {"type": "array"} | existing-native |
| [/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1/items](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal/oneOf/2/allOf/0/else/properties/value/anyOf/1/items) | {"type": ["string", "number", "boolean"]} | existing-native |
| [/$defs/expression/oneOf/1](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/1) | {"type": "object", "required": ["variable"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/1/properties/variable](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/1/properties/variable) | {"type": "string", "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-variable$", "maxLength": 64} | existing-native |
| [/$defs/expression/oneOf/2](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2) | {"type": "object", "required": ["values"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/2/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values) | {"type": "object", "required": ["object", "field"], "additionalProperties": false} | editorially-approved |

[/$defs/expression/oneOf/2/properties/values](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values): Reads a field from the Items collected by an Object.

Editorial receipt: editorial-batch-2.json case 09

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/2/properties/values/properties/field](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values/properties/field) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/expression/oneOf/3](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3) | {"type": "object", "required": ["concat"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/3/properties/concat](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat) | {"type": "array", "minItems": 2} | semantic-hold |

[/$defs/expression/oneOf/3/properties/concat](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat): Concatenate two or more components in order. Multiple values produce the Cartesian product of component values. Components follow inherited source casting rules when a string conversion is required; incompatible values produce an error. A missing or nonexistent component yields the inherited source status; Error, Incomplete, Not Collected, and Not Applicable statuses are not silently converted to strings.

Existing native annotations state component order and Cartesian combinations. Casting, output representation and no-value/error-status mappings remain pending semantic review; examples demonstrate syntax only, not executed results.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/4](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4) | {"type": "object", "required": ["regex_capture"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/4/properties/regex_capture](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture) | {"type": "object", "required": ["pattern", "value"], "additionalProperties": false} | semantic-hold |

[/$defs/expression/oneOf/4/properties/regex_capture](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture): Capture text from each input string using the first capturing group. The source regex dialect and first-match behavior are retained; inputs with no capture group or no match produce an empty string under the inherited function contract.

The current native annotation specifies the first group but delegates regex dialect, no-match/no-group behavior and statuses to inherited rules. The pattern member is only a string constraint; validating it does not prove capture semantics.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/4/properties/regex_capture/properties/pattern](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture/properties/pattern) | {"type": "string"} | existing-native |
| [/$defs/expression/oneOf/5](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5) | {"type": "object", "required": ["unique"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/5/properties/unique](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/unique) | {} | semantic-hold |

[/$defs/expression/oneOf/5/properties/unique](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/unique): Remove duplicate scalar values from the input. Record data is not a supported transformation operand; value ordering and status propagation remain governed by the inherited semantic contract.

The native description excludes record operands, although the expression reference does not by itself close every operand type. Equality, ordering and unavailable-value propagation remain pending; no deduplication runtime is executed.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/6](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/6) | {"type": "object", "required": ["count"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/7](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7) | {"type": "object", "required": ["merge"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/7/properties/merge](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/merge) | {"type": "object", "required": ["delimiter", "sort", "order", "values"], "additionalProperties": false} | semantic-hold |

[/$defs/expression/oneOf/7/properties/merge](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/merge): Combine input values into one string using an explicit delimiter, sort mode, and order. `document` preserves input order; other modes sort before joining. Duplicates are preserved unless a separate `unique` expression removes them.

delimiter, sort, order and values are explicit required inputs; duplicates are not implicitly removed. Sorting edge cases, casting and unavailable/error behavior need semantic confirmation before unqualified publication.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/7/properties/merge/properties/delimiter](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/merge/properties/delimiter) | {"type": "string"} | existing-native |
| [/$defs/expression/oneOf/7/properties/merge/properties/sort](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/merge/properties/sort) | {"enum": ["document", "lexical", "numeric", "natural"]} | existing-native |
| [/$defs/expression/oneOf/7/properties/merge/properties/order](../../../proposed-schema/documentation/variable-expression.schema.json#/$defs/expression/oneOf/7/properties/merge/properties/order) | {"enum": ["ascending", "descending"]} | existing-native |
