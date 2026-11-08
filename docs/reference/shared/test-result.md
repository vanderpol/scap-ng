# Native 0.4 Test Result

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Test-centered supplied observations with source-bound native requirements. No OVAL check aliases or synthetic State positions.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/id](../../../proposed-schema/documentation/test-result.schema.json#/properties/id) |
| `test_title` | null, string | 0..1 | Human-readable title for the Test. | [/properties/test_title](../../../proposed-schema/documentation/test-result.schema.json#/properties/test_title) |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/outcome](../../../proposed-schema/documentation/test-result.schema.json#/properties/outcome) |
| `existence_outcome` | null, string | 0..1 | **Unresolved description** | [/properties/existence_outcome](../../../proposed-schema/documentation/test-result.schema.json#/properties/existence_outcome) |
| `object_refs` | array | 1..1 (required) | **Unresolved description** | [/properties/object_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/object_refs) |
| `item_refs` | array | 1..1 (required) | Only the collected Item IDs retained under per_item_results or otherwise needed to explain the Test. | [/properties/item_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_refs) |
| `per_item_results` | array | 1..1 (required) | Test-local reported system Items and their evaluated State/Entity comparisons, subject to scanner-controlled evidence retention. | [/properties/per_item_results](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/reason](../../../proposed-schema/documentation/test-result.schema.json#/properties/reason) |
| `item_summary` | object | 1..1 (required) | Required counts for every technical Test, including no-item, unknown and capped-evidence cases. | [/properties/item_summary](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary) |
| `invocation_ref` | string | 1..1 (required) | Reference to the expression invocation. | [/properties/invocation_ref](../../../proposed-schema/documentation/test-result.schema.json#/properties/invocation_ref) |
| `require_refs` | array | 1..1 (required) | **Unresolved description** | [/properties/require_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/require_refs) |
| `items_found` | string | 1..1 (required) | Collected NG Items have no synthetic does-not-exist entries. | [/properties/items_found](../../../proposed-schema/documentation/test-result.schema.json#/properties/items_found) |
| `items_satisfying` | string | 0..1 | Consistent 0.4 authoring cardinality vocabulary. 'every' means all relevant results satisfy the specified comparison; source OVAL lexical values belong in provenance only. | [/properties/items_satisfying](../../../proposed-schema/documentation/test-result.schema.json#/properties/items_satisfying) |
| `field_requirement` | object | 0..1 | Explicit field existence and matching cardinalities inherited together. | [/properties/field_requirement](../../../proposed-schema/documentation/test-result.schema.json#/properties/field_requirement) |
| `binding_set_id` | string | 0..1 | **Unresolved description** | [/properties/binding_set_id](../../../proposed-schema/documentation/test-result.schema.json#/properties/binding_set_id) |
| `evidence_refs` | array | Conditional (at most 1) | References to the evidence supporting this result. | [/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/evidence_refs) |
| `decisive_require_refs` | array | 0..1 | **Unresolved description** | [/properties/decisive_require_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/decisive_require_refs) |
| `items_observed` | integer, string | 1..1 (required) | Explicit observed Item population, independent from evaluated/retained counts. | [/properties/items_observed](../../../proposed-schema/documentation/test-result.schema.json#/properties/items_observed) |

## `/properties/per_item_results/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_ref` | string | 1..1 (required) | Reference to the collected Item. | [/properties/per_item_results/items/properties/item_ref](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/item_ref) |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/per_item_results/items/properties/outcome](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/outcome) |
| `item` | object | 1..1 (required) | Retained system Item beside the verdict and native requirement observations; its id must equal item_ref. | [/properties/per_item_results/items/properties/item](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/item) |
| `require_results` | array | 1..1 (required) | Nested Require observations associated with this result. | [/properties/per_item_results/items/properties/require_results](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/require_results) |
| `reason` | string | Conditional (at most 1) | Explanation of the reported outcome. | [/properties/per_item_results/items/properties/reason](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/reason) |
| `evidence_refs` | array | Conditional (at most 1) | References to the evidence supporting this result. | [/properties/per_item_results/items/properties/evidence_refs](../../../proposed-schema/documentation/test-result.schema.json#/properties/per_item_results/items/properties/evidence_refs) |

## `/properties/item_summary`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `evaluated_items` | integer | 1..1 (required) | **Unresolved description** | [/properties/item_summary/properties/evaluated_items](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/evaluated_items) |
| `observed_mismatches` | integer | 1..1 (required) | **Unresolved description** | [/properties/item_summary/properties/observed_mismatches](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/observed_mismatches) |
| `actual_mismatches` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/item_summary/properties/actual_mismatches](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/actual_mismatches) |
| `returned_items` | integer | 1..1 (required) | **Unresolved description** | [/properties/item_summary/properties/returned_items](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/returned_items) |
| `truncated_evidence` | boolean | 1..1 (required) | **Unresolved description** | [/properties/item_summary/properties/truncated_evidence](../../../proposed-schema/documentation/test-result.schema.json#/properties/item_summary/properties/truncated_evidence) |

## Advanced constraints

[Local constraints](../advanced/test-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/test-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
