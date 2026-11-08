# Native 0.4 requirement Result — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/require-result.schema.json#) | {"type": "object", "required": ["require_ref", "outcome", "field_results"], "additionalProperties": false} | existing-native |
| [/properties/require_ref](../../../proposed-schema/documentation/require-result.schema.json#/properties/require_ref) | {"type": "string", "pattern": "^/tests/(?:[^~/]\|~[01])+/require(?:/(?:[^~]\|~[01])*)?$"} | existing-native |
| [/properties/record_ref](../../../proposed-schema/documentation/require-result.schema.json#/properties/record_ref) | {"type": "string", "pattern": "^/fields/(?:[^~]\|~[01])+$"} | existing-native |
| [/properties/operator](../../../proposed-schema/documentation/require-result.schema.json#/properties/operator) | {"enum": ["and", "or", "one", "xor"]} | native-structure-derived |
| [/properties/field_results](../../../proposed-schema/documentation/require-result.schema.json#/properties/field_results) | {"type": "array"} | existing-native |
| [/properties/require_results](../../../proposed-schema/documentation/require-result.schema.json#/properties/require_results) | {"type": "array"} | existing-native |
| [/properties/reason](../../../proposed-schema/documentation/require-result.schema.json#/properties/reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/evidence_refs](../../../proposed-schema/documentation/require-result.schema.json#/properties/evidence_refs) | {"type": "array"} | existing-native |
| [/properties/evidence_refs/items](../../../proposed-schema/documentation/require-result.schema.json#/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/observation_complete](../../../proposed-schema/documentation/require-result.schema.json#/properties/observation_complete) | {"type": "boolean"} | existing-native |
| [/allOf/0/if](../../../proposed-schema/documentation/require-result.schema.json#/allOf/0/if) | {"required": ["outcome"]} | existing-native |
| [/allOf/0/if/properties/outcome](../../../proposed-schema/documentation/require-result.schema.json#/allOf/0/if/properties/outcome) | {"const": "error"} | existing-native |
| [/allOf/0/then](../../../proposed-schema/documentation/require-result.schema.json#/allOf/0/then) | {"required": ["reason", "evidence_refs"]} | existing-native |
| [/allOf/0/then/properties/evidence_refs](../../../proposed-schema/documentation/require-result.schema.json#/allOf/0/then/properties/evidence_refs) | {"type": "array", "minItems": 1} | existing-native |
| [/allOf/0/then/properties/evidence_refs/items](../../../proposed-schema/documentation/require-result.schema.json#/allOf/0/then/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
