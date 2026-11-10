# Native 0.4 Test Result — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/test-result.schema.json#) | {"type": "object", "required": ["id", "outcome", "object_refs", "item_refs", "per_item_results", "item_summary", "invocation_ref", "require_refs", "items_found", "items_observed"], "additionalProperties": false} | existing-native |
| [/properties/id](../../../proposed-schema/documentation/test-result.schema.json#/properties/id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/test_title](../../../proposed-schema/documentation/test-result.schema.json#/properties/test_title) | {"type": ["string", "null"]} | existing-native |
| [/properties/existence_outcome](../../../proposed-schema/documentation/test-result.schema.json#/properties/existence_outcome) | {} | native-structure-derived |
| [/properties/existence_outcome/oneOf/1](../../../proposed-schema/documentation/test-result.schema.json#/properties/existence_outcome/oneOf/1) | {"type": "null"} | existing-native |
| [/properties/object_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/object_refs) | {"type": "array"} | native-structure-derived |
| [/properties/object_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/object_refs/items) | {"type": "string"} | existing-native |
| [/properties/item_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_refs) | {"type": "array"} | existing-native |
| [/properties/item_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_refs/items) | {"type": "string"} | existing-native |
| [/properties/per_item_results](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results) | {"type": "array"} | existing-native |
| [/properties/per_item_results/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items) | {"type": "object", "required": ["item_ref", "outcome", "require_results", "item"], "additionalProperties": false} | existing-native |
| [/properties/per_item_results/items/properties/item_ref](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/item_ref) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/per_item_results/items/properties/require_results](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/require_results) | {"type": "array"} | existing-native |
| [/properties/per_item_results/items/properties/reason](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/per_item_results/items/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/evidence_refs) | {"type": "array"} | existing-native |
| [/properties/per_item_results/items/properties/evidence_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/per_item_results/items/allOf/0/if](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/allOf/0/if) | {"required": ["outcome"]} | existing-native |
| [/properties/per_item_results/items/allOf/0/if/properties/outcome](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/allOf/0/if/properties/outcome) | {"const": "error"} | existing-native |
| [/properties/per_item_results/items/allOf/0/then](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/allOf/0/then) | {"required": ["reason", "evidence_refs"]} | existing-native |
| [/properties/per_item_results/items/allOf/0/then/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/allOf/0/then/properties/evidence_refs) | {"type": "array", "minItems": 1} | existing-native |
| [/properties/per_item_results/items/allOf/0/then/properties/evidence_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/allOf/0/then/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/reason](../../../proposed-schema/documentation/test-result.schema.json#/properties/reason) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/item_summary](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary) | {"type": "object", "required": ["evaluated_items", "observed_mismatches", "actual_mismatches", "returned_items", "truncated_evidence"], "additionalProperties": false} | existing-native |
| [/properties/item_summary/properties/evaluated_items](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/evaluated_items) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/item_summary/properties/observed_mismatches](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/observed_mismatches) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/item_summary/properties/actual_mismatches/oneOf/0](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/actual_mismatches/oneOf/0) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/item_summary/properties/actual_mismatches/oneOf/1](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/actual_mismatches/oneOf/1) | {"const": "unknown"} | existing-native |
| [/properties/item_summary/properties/returned_items](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/returned_items) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/item_summary/properties/truncated_evidence](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/truncated_evidence) | {"type": "boolean"} | existing-native |
| [/properties/invocation_ref](../../../proposed-schema/documentation/test-result.schema.json#/properties/invocation_ref) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/require_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/require_refs) | {"type": "array", "minItems": 1} | native-structure-derived |
| [/properties/require_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/require_refs/items) | {"type": "string", "pattern": "^/tests/(?:[^~/]\|~[01])+/require(?:/(?:[^~]\|~[01])*)?$"} | existing-native |
| [/properties/binding_set_id](../../../proposed-schema/documentation/test-result.schema.json#/properties/binding_set_id) | {"type": "string", "pattern": "^[0-9a-f]{64}$"} | native-structure-derived |
| [/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/evidence_refs) | {"type": "array"} | existing-native |
| [/properties/evidence_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
| [/properties/decisive_require_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/decisive_require_refs) | {"type": "array"} | native-structure-derived |
| [/properties/decisive_require_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/properties/decisive_require_refs/items) | {"type": "string", "pattern": "^/tests/(?:[^~/]\|~[01])+/require(?:/(?:[^~]\|~[01])*)?$"} | existing-native |
| [/properties/items_observed/oneOf/0](../../../proposed-schema/documentation/test-result.schema.json#/properties/items_observed/oneOf/0) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/items_observed/oneOf/1](../../../proposed-schema/documentation/test-result.schema.json#/properties/items_observed/oneOf/1) | {"const": "unknown"} | existing-native |
| [/allOf/0/if](../../../proposed-schema/documentation/test-result.schema.json#/allOf/0/if) | {"required": ["outcome"]} | existing-native |
| [/allOf/0/if/properties/outcome](../../../proposed-schema/documentation/test-result.schema.json#/allOf/0/if/properties/outcome) | {"const": "error"} | existing-native |
| [/allOf/0/then](../../../proposed-schema/documentation/test-result.schema.json#/allOf/0/then) | {"required": ["reason", "evidence_refs"]} | existing-native |
| [/allOf/0/then/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/allOf/0/then/properties/evidence_refs) | {"type": "array", "minItems": 1} | existing-native |
| [/allOf/0/then/properties/evidence_refs/items](../../../proposed-schema/documentation/test-result.schema.json#/allOf/0/then/properties/evidence_refs/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
