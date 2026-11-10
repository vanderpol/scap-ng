# Draft SCAP-NG 0.4.0 automated expression — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/0](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/0) | {"type": "object", "required": ["test"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/0/properties/test](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/0/properties/test) | {"type": "string", "minLength": 1, "maxLength": 64, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-test$"} | editorially-approved |

[/$defs/expression/oneOf/0/properties/test](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/0/properties/test): Uses a named Test’s outcome in this expression.

Editorial receipt: editorial-batch-2.json case 10

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/1](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/1) | {"type": "object", "required": ["assessment"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/1/properties/assessment](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/1/properties/assessment) | {"type": "string", "minLength": 1} | editorially-approved |

[/$defs/expression/oneOf/1/properties/assessment](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/1/properties/assessment): Uses a referenced Assessment’s outcome in this expression.

Editorial receipt: editorial-batch-2.json case 11

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/2](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2) | {"type": "object", "required": ["if", "then", "else"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/2/properties/if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/if) | {} | editorially-approved |

[/$defs/expression/oneOf/2/properties/if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/if): Tests the condition that selects a conditional branch.

Editorial receipt: editorial-batch-2.json case 12

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/2/properties/else_if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if) | {"type": "array", "minItems": 1} | editorially-approved |

[/$defs/expression/oneOf/2/properties/else_if](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if): Selects the first true alternative branch when preceding conditions are false.

Editorial receipt: editorial-batch-2.json case 13

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/2/properties/else_if/items](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if/items) | {"type": "object", "required": ["if", "then"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/3](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/3) | {"type": "object", "required": ["not"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/4](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/4) | {"type": "object", "required": ["and"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/4/properties/and](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/4/properties/and) | {"type": "array", "minItems": 1} | editorially-approved |

[/$defs/expression/oneOf/4/properties/and](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/4/properties/and): Combines expression outcomes using logical AND.

Editorial receipt: editorial-batch-2.json case 14

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/5](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/5) | {"type": "object", "required": ["or"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/5/properties/or](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/5/properties/or) | {"type": "array", "minItems": 1} | editorially-approved |

[/$defs/expression/oneOf/5/properties/or](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/5/properties/or): Combines expression outcomes using logical OR.

Editorial receipt: editorial-batch-2.json case 15

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/6](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6) | {"type": "object", "required": ["not_evaluated"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/6/properties/not_evaluated](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated) | {"type": "object", "required": ["reason"], "additionalProperties": false} | editorially-approved |

[/$defs/expression/oneOf/6/properties/not_evaluated](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated): Declares that this branch cannot be evaluated and provides a reason.

Editorial receipt: editorial-batch-2.json case 18

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/6/properties/not_evaluated/properties/reason](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/properties/reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/$defs/expression/oneOf/6/properties/not_evaluated/properties/follow_up](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/properties/follow_up) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/expression/oneOf/7](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7) | {"type": "object", "required": ["not_applicable"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/7/properties/not_applicable](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable) | {"type": "object", "required": ["reason"], "additionalProperties": false} | editorially-approved |

[/$defs/expression/oneOf/7/properties/not_applicable](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable): Declares that this branch does not apply and provides a reason.

Editorial receipt: editorial-batch-2.json case 19

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/7/properties/not_applicable/properties/reason](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable/properties/reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/$defs/expression/oneOf/8](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/8) | {"type": "object", "required": ["one"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/8/properties/one](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/8/properties/one) | {"type": "array", "minItems": 1} | semantic-hold |

[/$defs/expression/oneOf/8/properties/one](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/8/properties/one): No description approved.

The active grammar supports this operator and a nonempty recursive operand list. Confirm multi-state truth/indeterminate aggregation before clearing this proposed meaning; structural acceptance alone proves neither truth tables nor evaluation order.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/expression/oneOf/9](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/9) | {"type": "object", "required": ["xor"], "additionalProperties": false} | existing-native |
| [/$defs/expression/oneOf/9/properties/xor](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/9/properties/xor) | {"type": "array", "minItems": 1} | semantic-hold |

[/$defs/expression/oneOf/9/properties/xor](../../../proposed-schema/documentation/expression.schema.json#/$defs/expression/oneOf/9/properties/xor): Logical XOR of complete Test outcomes; separate from Test Item matching.

The active grammar supports this operator and a nonempty recursive operand list. Confirm multi-state truth/indeterminate aggregation before clearing this proposed meaning; structural acceptance alone proves neither truth tables nor evaluation order.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/input_presence](../../../proposed-schema/documentation/expression.schema.json#/$defs/input_presence) | {"type": "object", "required": ["input_provided"], "additionalProperties": false} | native-structure-derived |
| [/$defs/input_presence/properties/input_provided](../../../proposed-schema/documentation/expression.schema.json#/$defs/input_presence/properties/input_provided) | {"type": "string", "maxLength": 64, "pattern": "^[a-z0-9]+(?:-[a-z0-9]+)*-input$"} | editorially-approved |

[/$defs/input_presence/properties/input_provided](../../../proposed-schema/documentation/expression.schema.json#/$defs/input_presence/properties/input_provided): Checks whether a declared Input was supplied, even if its value is empty.

Editorial receipt: editorial-batch.json case 05

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/condition](../../../proposed-schema/documentation/expression.schema.json#/$defs/condition) | {} | native-structure-derived |
