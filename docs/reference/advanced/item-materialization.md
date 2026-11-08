# Schema — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/item-materialization.schema.json#) | {"type": "object", "required": ["scope", "available_count", "included_count", "omitted_count", "consumed_item_refs", "collections"], "additionalProperties": false} | native-structure-derived |
| [/properties/scope](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/scope) | {"enum": ["all", "consumed"]} | existing-native |
| [/properties/available_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/available_count) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/included_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/included_count) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/omitted_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/omitted_count) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/consumed_item_refs](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/consumed_item_refs) | {"type": "array"} | native-structure-derived |
| [/properties/consumed_item_refs/items](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/consumed_item_refs/items) | {"type": "string", "minLength": 1} | existing-native |
| [/properties/collections](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections) | {"type": "array"} | native-structure-derived |
| [/properties/collections/items](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items) | {"type": "object", "required": ["object_ref", "available_count", "included_count", "omitted_count"], "additionalProperties": false} | existing-native |
| [/properties/collections/items/properties/object_ref](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/object_ref) | {"type": "string", "minLength": 1} | native-structure-derived |
| [/properties/collections/items/properties/available_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/available_count) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/collections/items/properties/included_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/included_count) | {"type": "integer", "minimum": 0} | existing-native |
| [/properties/collections/items/properties/omitted_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/omitted_count) | {"type": "integer", "minimum": 0} | existing-native |
