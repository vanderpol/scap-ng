# Draft canonical collected Item 0.4.1

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Records one collected entity, its fields, and supporting provenance.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of this collected Item. | [/properties/id](../../../proposed-schema/documentation/collected-item.schema.json#/properties/id) |
| `capability` | string | 1..1 (required) | Capability responsible for collecting or interpreting this resource. | [/properties/capability](../../../proposed-schema/documentation/collected-item.schema.json#/properties/capability) |
| `status` | string | 1..1 (required) | Collection status of this observed Item. | [/properties/status](../../../proposed-schema/documentation/collected-item.schema.json#/properties/status) |
| `imported` | boolean | 0..1 | Whether this Item was imported from retained evidence. | [/properties/imported](../../../proposed-schema/documentation/collected-item.schema.json#/properties/imported) |
| `fields` | object | 1..1 (required) | Named evidence fields carried by this Item. | [/properties/fields](../../../proposed-schema/documentation/collected-item.schema.json#/properties/fields) |
| `provenance` | object | 1..1 (required) | Source and collection context for this evidence. | [/properties/provenance](../../../proposed-schema/documentation/collected-item.schema.json#/properties/provenance) |
| `context` | object | Conditional (at most 1) | Collection and reuse context associated with this Item. | [/properties/context](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context) |

## `/properties/context`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name_resolution` | object | 0..1 | Context records associated with resolving collected names. | [/properties/context/properties/name_resolution](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/name_resolution) |
| `locators` | array | 0..1 | Locations of the evidence represented by this Item. | [/properties/context/properties/locators](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators) |
| `origin` | object | 0..1 | Source context recorded for an imported Item. | [/properties/context/properties/origin](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin) |
| `import_history` | array | 0..1 | Context records retained for imports of this Item. | [/properties/context/properties/import_history](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history) |

## `/properties/context/properties/name_resolution/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `source_field` | string | 1..1 (required) | Name of the source field for this resolution record. | [/properties/context/properties/name_resolution/additionalProperties/properties/source_field](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/name_resolution/additionalProperties/properties/source_field) |
| `target_context_ref` | string | 1..1 (required) | Reference to the target context associated with this resolution. | [/properties/context/properties/name_resolution/additionalProperties/properties/target_context_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/name_resolution/additionalProperties/properties/target_context_ref) |
| `source_ref` | string | 1..1 (required) | Reference to the source of the resolution observation. | [/properties/context/properties/name_resolution/additionalProperties/properties/source_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/name_resolution/additionalProperties/properties/source_ref) |
| `observed_at` | string | 1..1 (required) | Timestamp recorded for this name-resolution observation. | [/properties/context/properties/name_resolution/additionalProperties/properties/observed_at](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/name_resolution/additionalProperties/properties/observed_at) |

## `/properties/context/properties/locators/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Kind of evidence location: text position, structured path, or record position. | [/properties/context/properties/locators/items/properties/kind](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/kind) |
| `source_ref` | string | 1..1 (required) | Reference to the evidence source containing this location. | [/properties/context/properties/locators/items/properties/source_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/source_ref) |
| `line` | integer | Conditional (at most 1) | Line number in the referenced text evidence. | [/properties/context/properties/locators/items/properties/line](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/line) |
| `column` | integer | 0..1 | Column number in the referenced text evidence. | [/properties/context/properties/locators/items/properties/column](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/column) |
| `path` | string | Conditional (at most 1) | Path selecting a location in structured evidence. | [/properties/context/properties/locators/items/properties/path](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/path) |
| `path_language` | string | Conditional (at most 1) | Language used to express the structured evidence path. | [/properties/context/properties/locators/items/properties/path_language](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/path_language) |
| `index` | integer | Conditional (at most 1) | Record index in the referenced evidence. | [/properties/context/properties/locators/items/properties/index](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/index) |
| `field` | string | Conditional (at most 1) | Collected field identified by this record locator. | [/properties/context/properties/locators/items/properties/field](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/field) |
| `value_index` | integer | 0..1 | Index of the referenced field value. | [/properties/context/properties/locators/items/properties/value_index](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/value_index) |
| `property` | string | 0..1 | Property name within the referenced record value. | [/properties/context/properties/locators/items/properties/property](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/locators/items/properties/property) |

## `/properties/context/properties/origin`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_ref` | string | 1..1 (required) | Reference to a retained result. | [/properties/context/properties/origin/properties/result_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/result_ref) |
| `item_ref` | string | 1..1 (required) | Reference to the collected Item. | [/properties/context/properties/origin/properties/item_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/item_ref) |
| `source_execution_ref` | string | Conditional (at most 1) | Reference to the source execution whose evidence is used. | [/properties/context/properties/origin/properties/source_execution_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/source_execution_ref) |
| `source_digest` | string | 0..1 | Digest of the referenced source. | [/properties/context/properties/origin/properties/source_digest](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/source_digest) |
| `binding_set_id` | string | Conditional (at most 1) | Binding-set identifier recorded for the imported Item origin. | [/properties/context/properties/origin/properties/binding_set_id](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/binding_set_id) |
| `source_completeness` | object | Conditional (at most 1) | Completeness information retained from the source result. | [/properties/context/properties/origin/properties/source_completeness](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/origin/properties/source_completeness) |

## `/properties/context/properties/import_history/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_ref` | string | 1..1 (required) | Reference to a retained result. | [/properties/context/properties/import_history/items/properties/result_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/result_ref) |
| `item_ref` | string | 1..1 (required) | Reference to the collected Item. | [/properties/context/properties/import_history/items/properties/item_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/item_ref) |
| `source_execution_ref` | string | Conditional (at most 1) | Reference to the source execution whose evidence is used. | [/properties/context/properties/import_history/items/properties/source_execution_ref](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/source_execution_ref) |
| `source_digest` | string | 0..1 | Digest of the referenced source. | [/properties/context/properties/import_history/items/properties/source_digest](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/source_digest) |
| `binding_set_id` | string | Conditional (at most 1) | Binding-set identifier recorded in this import-history entry. | [/properties/context/properties/import_history/items/properties/binding_set_id](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/binding_set_id) |
| `source_completeness` | object | Conditional (at most 1) | Completeness information retained from the source result. | [/properties/context/properties/import_history/items/properties/source_completeness](../../../proposed-schema/documentation/collected-item.schema.json#/properties/context/properties/import_history/items/properties/source_completeness) |

## Advanced constraints

[Local constraints](../advanced/collected-item.md) and [complete JSON Schema](../../../proposed-schema/documentation/collected-item.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
