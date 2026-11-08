# SCAP-NG Variable Result draft v0.4.0 strawman — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/variable-result.schema.json#) | {"type": "object", "required": ["id", "datatype", "status", "cardinality", "values", "item_refs"], "additionalProperties": false} | existing-native |
| [/properties/id](../../../proposed-schema/documentation/variable-result.schema.json#/properties/id) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/variable_title](../../../proposed-schema/documentation/variable-result.schema.json#/properties/variable_title) | {"type": ["string", "null"]} | existing-native |
| [/properties/datatype](../../../proposed-schema/documentation/variable-result.schema.json#/properties/datatype) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/datatype/not](../../../proposed-schema/documentation/variable-result.schema.json#/properties/datatype/not) | {"const": "record"} | existing-native |
| [/properties/status](../../../proposed-schema/documentation/variable-result.schema.json#/properties/status) | {"type": "string", "enum": ["complete", "incomplete", "error", "unknown", "not_evaluated", "not_applicable", "zero_values"]} | existing-native |
| [/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/properties/cardinality) | {"type": "string", "enum": ["zero", "one", "many"]} | existing-native |
| [/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/properties/values) | {"type": "array"} | existing-native |
| [/properties/source](../../../proposed-schema/documentation/variable-result.schema.json#/properties/source) | {"type": ["string", "null"]} | existing-native |
| [/properties/provenance](../../../proposed-schema/documentation/variable-result.schema.json#/properties/provenance) | {"type": "object"} | existing-native |
| [/properties/diagnostics](../../../proposed-schema/documentation/variable-result.schema.json#/properties/diagnostics) | {"type": "array"} | existing-native |
| [/properties/diagnostics/items](../../../proposed-schema/documentation/variable-result.schema.json#/properties/diagnostics/items) | {"type": "object"} | existing-native |
| [/properties/item_refs](../../../proposed-schema/documentation/variable-result.schema.json#/properties/item_refs) | {"type": "array"} | existing-native |
| [/properties/item_refs/items](../../../proposed-schema/documentation/variable-result.schema.json#/properties/item_refs/items) | {"type": "string", "minLength": 1} | existing-native |
| [/allOf/0/if](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/0/if) | {"required": ["status"]} | existing-native |
| [/allOf/0/if/properties/status](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/0/if/properties/status) | {"const": "zero_values"} | existing-native |
| [/allOf/0/then/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/0/then/properties/cardinality) | {"const": "zero"} | existing-native |
| [/allOf/0/then/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/0/then/properties/values) | {"maxItems": 0} | existing-native |
| [/allOf/1/if](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/if) | {"required": ["status"]} | existing-native |
| [/allOf/1/if/properties/status](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/if/properties/status) | {"enum": ["complete", "incomplete"]} | existing-native |
| [/allOf/1/then/oneOf/0/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/0/properties/cardinality) | {"const": "zero"} | existing-native |
| [/allOf/1/then/oneOf/0/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/0/properties/values) | {"maxItems": 0} | existing-native |
| [/allOf/1/then/oneOf/1/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/1/properties/cardinality) | {"const": "one"} | existing-native |
| [/allOf/1/then/oneOf/1/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/1/properties/values) | {"minItems": 1, "maxItems": 1} | existing-native |
| [/allOf/1/then/oneOf/2/properties/cardinality](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/2/properties/cardinality) | {"const": "many"} | existing-native |
| [/allOf/1/then/oneOf/2/properties/values](../../../proposed-schema/documentation/variable-result.schema.json#/allOf/1/then/oneOf/2/properties/values) | {"minItems": 2} | existing-native |
