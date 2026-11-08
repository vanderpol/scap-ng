# Draft invocation-linked Assessment Results transport — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/assessment-result-set.schema.json#) | {"type": "object", "required": ["entry_execution_id", "target_ref", "assessment_results"], "additionalProperties": false} | existing-native |
| [/properties/entry_execution_id](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/entry_execution_id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/target_ref](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/target_ref) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/assessment_results](../../../proposed-schema/documentation/assessment-result-set.schema.json#/properties/assessment_results) | {"type": "array", "minItems": 1} | native-structure-derived |
