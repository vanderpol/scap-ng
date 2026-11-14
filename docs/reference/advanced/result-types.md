# Draft shared result types 0.4.1 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/technical_outcome](../../../proposed-schema/documentation/result-types.schema.json#/$defs/technical_outcome) | {"type": "string", "enum": ["true", "false", "error", "unknown", "not_evaluated", "not_applicable"]} | editorially-approved |

[/$defs/technical_outcome](../../../proposed-schema/documentation/result-types.schema.json#/$defs/technical_outcome): Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable.

Editorial receipt: editorial-batch-2.json case 23

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/assessment_purpose](../../../proposed-schema/documentation/result-types.schema.json#/$defs/assessment_purpose) | {"type": "string", "enum": ["assessment", "applicability"]} | native-structure-derived |
| [/$defs/assessment_class](../../../proposed-schema/documentation/result-types.schema.json#/$defs/assessment_class) | {"type": "string", "enum": ["compliance", "vulnerability", "patch", "inventory", "miscellaneous"]} | existing-native |
| [/$defs/completeness](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness) | {"type": "object", "required": ["logical_complete", "population_complete", "evidence_complete"], "additionalProperties": false} | existing-native |
| [/$defs/completeness/properties/logical_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/logical_complete) | {"type": "boolean"} | existing-native |
| [/$defs/completeness/properties/population_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/population_complete) | {"type": "boolean"} | existing-native |
| [/$defs/completeness/properties/evidence_complete](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/evidence_complete) | {"type": "boolean"} | existing-native |
| [/$defs/completeness/properties/stop_reason](../../../proposed-schema/documentation/result-types.schema.json#/$defs/completeness/properties/stop_reason) | {"type": ["string", "null"]} | existing-native |
| [/$defs/typed_value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value) | {"type": "object", "required": ["datatype", "status"], "additionalProperties": false} | existing-native |
| [/$defs/typed_value/properties/datatype](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/datatype) | {"type": "string", "minLength": 1} | existing-native |
| [/$defs/typed_value/properties/value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/value) | {} | semantic-hold |

[/$defs/typed_value/properties/value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/value): No description approved.

This describes intended representation, not a validation guarantee: generic 0.4 does not fully enforce non-record tag/payload consistency. Status/redaction can prohibit the payload, and record rules can require it; the intent/enforcement distinction needs semantic review.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/typed_value/properties/status](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/status) | {"enum": ["exists", "does_not_exist", "error", "not_collected"]} | editorially-approved |

[/$defs/typed_value/properties/status](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/status): Distinguishes an existing value from absence, an error, or a value that was not collected.

Editorial receipt: editorial-batch.json case 22

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/typed_value/properties/redacted](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/redacted) | {"type": "boolean"} | editorially-approved |

[/$defs/typed_value/properties/redacted](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/properties/redacted): Indicates that the value was intentionally omitted from the reported evidence.

Editorial receipt: editorial-batch-2.json case 25

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/typed_value/allOf/0/if](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/0/if) | {"required": ["status"]} | existing-native |
| [/$defs/typed_value/allOf/0/if/properties/status](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/0/if/properties/status) | {"enum": ["does_not_exist", "error", "not_collected"]} | existing-native |
| [/$defs/typed_value/allOf/0/then/not](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/0/then/not) | {"required": ["value"]} | existing-native |
| [/$defs/typed_value/allOf/1/if](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/1/if) | {"required": ["redacted"]} | existing-native |
| [/$defs/typed_value/allOf/1/if/properties/redacted](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/1/if/properties/redacted) | {"const": true} | existing-native |
| [/$defs/typed_value/allOf/1/then/not](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/1/then/not) | {"required": ["value"]} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/0](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/0) | {"required": ["datatype"]} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/0/properties/datatype](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/0/properties/datatype) | {"const": "record"} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/1/not](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/1/not) | {"required": ["redacted"]} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/1/not/properties/redacted](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/1/not/properties/redacted) | {"const": true} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/2/not](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/2/not) | {"required": ["status"]} | existing-native |
| [/$defs/typed_value/allOf/2/if/allOf/2/not/properties/status](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/if/allOf/2/not/properties/status) | {"enum": ["does_not_exist", "error", "not_collected"]} | existing-native |
| [/$defs/typed_value/allOf/2/then](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/then) | {"required": ["value"]} | existing-native |
| [/$defs/typed_value/allOf/2/then/properties/value](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/then/properties/value) | {"type": "object"} | existing-native |
| [/$defs/typed_value/allOf/2/then/properties/value/additionalProperties/oneOf/1](../../../proposed-schema/documentation/result-types.schema.json#/$defs/typed_value/allOf/2/then/properties/value/additionalProperties/oneOf/1) | {"type": "array"} | existing-native |
| [/$defs/bounded_evidence](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence) | {"type": "object", "required": ["observed_failures", "actual_failures", "maximum", "returned", "truncated_population"], "additionalProperties": false} | native-structure-derived |
| [/$defs/bounded_evidence/properties/observed_failures](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/observed_failures) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/bounded_evidence/properties/actual_failures/oneOf/0](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/actual_failures/oneOf/0) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/bounded_evidence/properties/actual_failures/oneOf/1](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/actual_failures/oneOf/1) | {"type": "string", "enum": ["unknown"]} | existing-native |
| [/$defs/bounded_evidence/properties/maximum](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/maximum) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/bounded_evidence/properties/returned](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/returned) | {"type": "integer", "minimum": 0} | existing-native |
| [/$defs/bounded_evidence/properties/truncated_population](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/truncated_population) | {"type": "boolean"} | existing-native |
| [/$defs/bounded_evidence/properties/stop_reason](../../../proposed-schema/documentation/result-types.schema.json#/$defs/bounded_evidence/properties/stop_reason) | {"type": ["string", "null"]} | existing-native |
