# Draft derived Item report 0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

An explicitly marked projection of evaluated/redacted canonical Items. Not a replacement Assessment Result.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_report` | object | 1..1 (required) | Projection of evaluated and redacted Items selected for reporting. | [/properties/item_report](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report) |
| `names` | array | Definition | List of distinct, nonempty element names. | [/$defs/names](../../../proposed-schema/documentation/item-report.schema.json#/$defs/names) |

## `/properties/item_report`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Identifies a projection of the requested reported elements. | [/properties/item_report/properties/kind](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/kind) |
| `source_execution_ref` | string | 1..1 (required) | Reference to the source execution whose evidence is used. | [/properties/item_report/properties/source_execution_ref](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/source_execution_ref) |
| `source_completeness` | object | 1..1 (required) | Completeness information copied from the source result. | [/properties/item_report/properties/source_completeness](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/source_completeness) |
| `items` | array | 1..1 (required) | Item projections included in this report. | [/properties/item_report/properties/items](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items) |

## `/properties/item_report/properties/source_completeness`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `logical_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/item_report/properties/source_completeness/properties/logical_complete](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/source_completeness/properties/logical_complete) |
| `population_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/item_report/properties/source_completeness/properties/population_complete](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/source_completeness/properties/population_complete) |
| `evidence_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/item_report/properties/source_completeness/properties/evidence_complete](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/source_completeness/properties/evidence_complete) |

## `/properties/item_report/properties/items/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item` | object | 1..1 (required) | Projected collected Item included in the report. | [/properties/item_report/properties/items/items/properties/item](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item) |
| `selection` | object | 1..1 (required) | Metadata describing the selection of elements for this Item projection. | [/properties/item_report/properties/items/items/properties/selection](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/selection) |

## `/properties/item_report/properties/items/items/properties/item`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of this collected Item. | [/properties/item_report/properties/items/items/properties/item/properties/id](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/id) |
| `capability` | string | 1..1 (required) | Capability responsible for collecting or interpreting this resource. | [/properties/item_report/properties/items/items/properties/item/properties/capability](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/capability) |
| `status` | string | 1..1 (required) | Collection status of this observed Item. | [/properties/item_report/properties/items/items/properties/item/properties/status](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/status) |
| `imported` | boolean | 0..1 | Whether this Item was imported from retained evidence. | [/properties/item_report/properties/items/items/properties/item/properties/imported](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/imported) |
| `provenance` | object | 1..1 (required) | Source and collection context for this evidence. | [/properties/item_report/properties/items/items/properties/item/properties/provenance](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/provenance) |
| `context` | object | 0..1 | Collection and reuse context associated with this Item. | [/properties/item_report/properties/items/items/properties/item/properties/context](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/context) |
| `fields` | object | 1..1 (required) | Named evidence fields carried by this Item. | [/properties/item_report/properties/items/items/properties/item/properties/fields](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/item/properties/fields) |

## `/properties/item_report/properties/items/items/properties/selection`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `omitted_elements` | array | 1..1 (required) | List of distinct, nonempty element names. | [/properties/item_report/properties/items/items/properties/selection/properties/omitted_elements](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/selection/properties/omitted_elements) |
| `unavailable_elements` | array | 1..1 (required) | List of distinct, nonempty element names. | [/properties/item_report/properties/items/items/properties/selection/properties/unavailable_elements](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/selection/properties/unavailable_elements) |
| `retained_required_elements` | array | 1..1 (required) | List of distinct, nonempty element names. | [/properties/item_report/properties/items/items/properties/selection/properties/retained_required_elements](../../../proposed-schema/documentation/item-report.schema.json#/properties/item_report/properties/items/items/properties/selection/properties/retained_required_elements) |

## Advanced constraints

[Local constraints](../advanced/item-report.md) and [complete JSON Schema](../../../proposed-schema/documentation/item-report.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
