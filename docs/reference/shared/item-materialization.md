# item-materialization.schema

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Record of which available Items are included in the result and which are omitted.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `scope` | string | 1..1 (required) | **Unresolved description** | [/properties/scope](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/scope) |
| `available_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/available_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/available_count) |
| `included_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/included_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/included_count) |
| `omitted_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/omitted_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/omitted_count) |
| `consumed_item_refs` | array | 1..1 (required) | References to consumed Items identified by this materialization record. | [/properties/consumed_item_refs](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/consumed_item_refs) |
| `collections` | array | 1..1 (required) | Per-collection entries describing the Item materialization. | [/properties/collections](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections) |

## `/properties/collections/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `object_ref` | string | 1..1 (required) | Object reference associated with this materialization entry. | [/properties/collections/items/properties/object_ref](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/object_ref) |
| `available_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/collections/items/properties/available_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/available_count) |
| `included_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/collections/items/properties/included_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/included_count) |
| `omitted_count` | integer | 1..1 (required) | **Unresolved description** | [/properties/collections/items/properties/omitted_count](../../../proposed-schema/documentation/item-materialization.schema.json#/properties/collections/items/properties/omitted_count) |

## Advanced constraints

[Local constraints](../advanced/item-materialization.md) and [complete JSON Schema](../../../proposed-schema/documentation/item-materialization.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
