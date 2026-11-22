# SCAP-NG declared CPE identity v0.4.1 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/cpe-identity.schema.json#) | {"type": "object", "required": ["value", "binding", "source"], "additionalProperties": false} | native-structure-derived |
| [/properties/value](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/value) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/binding](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/binding) | {"type": "string", "enum": ["cpe_uri_2_2", "cpe_formatted_string_2_3"]} | native-structure-derived |
| [/properties/source](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source) | {"type": "object", "required": ["kind", "id", "sha256"], "additionalProperties": false} | native-structure-derived |
| [/properties/source/properties/kind](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/kind) | {"const": "cpe_platform"} | native-structure-derived |
| [/properties/source/properties/id](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/id) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/source/properties/idref](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/idref) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/source/properties/href](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/href) | {"type": "string"} | native-structure-derived |
| [/properties/source/properties/sha256](../../../proposed-schema/documentation/cpe-identity.schema.json#/properties/source/properties/sha256) | {"type": "string", "pattern": "^[0-9a-f]{64}$"} | native-structure-derived |
