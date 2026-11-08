# SCAP-NG Object Collection Result pre-release v0.4.0 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/collection-result.schema.json#) | {"type": "object", "required": ["id", "capability", "status", "item_refs"], "additionalProperties": false} | editorially-approved |

[schema](../../../proposed-schema/documentation/collection-result.schema.json#): Records an Object's collection outcome and supporting Item references.

Editorial receipt: editorial-batch.json case 24

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/id](../../../proposed-schema/documentation/collection-result.schema.json#/properties/id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/object_title](../../../proposed-schema/documentation/collection-result.schema.json#/properties/object_title) | {"type": ["string", "null"]} | existing-native |
| [/properties/capability](../../../proposed-schema/documentation/collection-result.schema.json#/properties/capability) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/status](../../../proposed-schema/documentation/collection-result.schema.json#/properties/status) | {"type": "string", "enum": ["error", "complete", "incomplete", "does_not_exist", "not_collected", "not_applicable"]} | editorially-approved |

[/properties/status](../../../proposed-schema/documentation/collection-result.schema.json#/properties/status): Reports the outcome of collecting an Object’s Items.

Editorial receipt: editorial-batch-2.json case 24

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/item_refs](../../../proposed-schema/documentation/collection-result.schema.json#/properties/item_refs) | {"type": "array"} | editorially-approved |

[/properties/item_refs](../../../proposed-schema/documentation/collection-result.schema.json#/properties/item_refs): Identifies the Items retained or referenced by this collection result.

Editorial receipt: editorial-batch-2.json case 26

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/properties/item_refs/items](../../../proposed-schema/documentation/collection-result.schema.json#/properties/item_refs/items) | {"type": "string"} | existing-native |
| [/properties/logical_complete](../../../proposed-schema/documentation/collection-result.schema.json#/properties/logical_complete) | {"type": ["boolean", "null"]} | existing-native |
| [/properties/population_complete](../../../proposed-schema/documentation/collection-result.schema.json#/properties/population_complete) | {"type": ["boolean", "null"]} | existing-native |
| [/properties/stop_reason](../../../proposed-schema/documentation/collection-result.schema.json#/properties/stop_reason) | {"type": ["string", "null"]} | native-structure-derived |
| [/properties/source_execution_ref](../../../proposed-schema/documentation/collection-result.schema.json#/properties/source_execution_ref) | {"type": ["string", "null"]} | existing-native |
| [/properties/diagnostics](../../../proposed-schema/documentation/collection-result.schema.json#/properties/diagnostics) | {"type": "array"} | existing-native |
| [/properties/diagnostics/items](../../../proposed-schema/documentation/collection-result.schema.json#/properties/diagnostics/items) | {"type": "object"} | existing-native |
| [/allOf/0/if](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/if) | {"required": ["status"]} | existing-native |
| [/allOf/0/if/properties/status](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/if/properties/status) | {"enum": ["error", "incomplete"]} | existing-native |
| [/allOf/0/then](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then) | {"required": ["stop_reason", "diagnostics"]} | existing-native |
| [/allOf/0/then/properties/stop_reason](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then/properties/stop_reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/allOf/0/then/properties/diagnostics](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then/properties/diagnostics) | {"type": "array", "minItems": 1} | existing-native |
| [/allOf/0/then/properties/diagnostics/items](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then/properties/diagnostics/items) | {"type": "object", "required": ["code", "message"]} | existing-native |
| [/allOf/0/then/properties/diagnostics/items/properties/code](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then/properties/diagnostics/items/properties/code) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/allOf/0/then/properties/diagnostics/items/properties/message](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/0/then/properties/diagnostics/items/properties/message) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/allOf/1/if](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/1/if) | {"required": ["status"]} | existing-native |
| [/allOf/1/if/properties/status](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/1/if/properties/status) | {"const": "incomplete"} | existing-native |
| [/allOf/1/then](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/1/then) | {"required": ["population_complete"]} | existing-native |
| [/allOf/1/then/properties/population_complete](../../../proposed-schema/documentation/collection-result.schema.json#/allOf/1/then/properties/population_complete) | {"const": false} | existing-native |
