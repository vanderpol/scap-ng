# Draft Test reported elements 0.4.1 — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/oneOf/0](../../../proposed-schema/documentation/reported-elements.schema.json#/oneOf/0) | {"enum": ["all", "compared"]} | existing-native |
| [/oneOf/1](../../../proposed-schema/documentation/reported-elements.schema.json#/oneOf/1) | {"type": "array"} | existing-native |
| [/oneOf/1/items](../../../proposed-schema/documentation/reported-elements.schema.json#/oneOf/1/items) | {"type": "string", "minLength": 1, "pattern": "\\S"} | existing-native |
