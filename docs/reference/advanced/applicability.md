# SCAP-NG Applicability Catalog v0.4.0 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/applicability.schema.json#) | {"type": "object", "required": ["applicability"], "additionalProperties": false} | existing-native |
| [/properties/applicability](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability) | {"type": "object", "required": ["id", "conditions"], "additionalProperties": false} | native-structure-derived |
| [/properties/applicability/properties/id](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/applicability/properties/conditions](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions) | {"type": "object"} | native-structure-derived |
| [/properties/applicability/properties/conditions/additionalProperties](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties) | {"type": "object", "required": ["assessment"], "additionalProperties": false} | existing-native |
| [/properties/applicability/properties/conditions/additionalProperties/properties/assessment](../../../proposed-schema/documentation/applicability.schema.json#/properties/applicability/properties/conditions/additionalProperties/properties/assessment) | {"type": "string", "minLength": 1} | native-structure-derived |
