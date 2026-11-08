# SCAP-NG Assessment Result draft v0.4.0 strawman

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Detailed execution result for one Assessment invocation, including Test outcomes, collected Items, bindings, completeness, and diagnostics. Pre-alpha strawman.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment_result` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment_result](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result) |

## `/properties/assessment_result`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_schema_version` | string | 1..1 (required) | Version of the result serialization schema. | [/properties/assessment_result/properties/result_schema_version](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/result_schema_version) |
| `execution_id` | string | 1..1 (required) | Identifier of this execution. | [/properties/assessment_result/properties/execution_id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/execution_id) |
| `assessment` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/assessment](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/assessment) |
| `purpose` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/purpose](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/purpose) |
| `class` | string | 1..1 (required) | Defines what technical truth means. | [/properties/assessment_result/properties/class](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/class) |
| `mode` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/mode](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/mode) |
| `outcome` | string | 1..1 (required) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | [/properties/assessment_result/properties/outcome](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/outcome) |
| `summary` | string | 1..1 (required) | Required concise deterministic standalone explanation of the technical Assessment outcome, including decisive failure, incomplete collection, error, or applicability cause where relevant. | [/properties/assessment_result/properties/summary](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/summary) |
| `logical_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/logical_complete](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/logical_complete) |
| `population_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/population_complete](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/population_complete) |
| `evidence_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/evidence_complete](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_complete) |
| `tests` | array | 1..1 (required) | Test-centered technical results. | [/properties/assessment_result/properties/tests](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/tests) |
| `objects` | array | 1..1 (required) | Runtime records describing Object collection execution, including acquisition status and diagnostics. | [/properties/assessment_result/properties/objects](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/objects) |
| `items` | array | 0..1 | Optional additional collected Items needed by collection/variable results but not represented under a Test. | [/properties/assessment_result/properties/items](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/items) |
| `variables` | array | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/variables](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/variables) |
| `diagnostics` | array | 1..1 (required) | Diagnostic entries associated with this result. | [/properties/assessment_result/properties/diagnostics](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/diagnostics) |
| `evidence` | array | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/evidence](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence) |
| `manual_response` | null, object | Conditional (at most 1) | Required provenance for a completed manual Assessment result. | [/properties/assessment_result/properties/manual_response](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response) |
| `consumed_organizational_inputs` | array | 0..1 | Organizational Input bindings consumed by this Assessment execution. | [/properties/assessment_result/properties/consumed_organizational_inputs](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs) |
| `reason` | null, object, string | 0..1 | Explanation of the reported outcome. | [/properties/assessment_result/properties/reason](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/reason) |
| `dependent_assessments` | array | 1..1 (required) | Assessment-result dependencies consumed by this Assessment invocation. | [/properties/assessment_result/properties/dependent_assessments](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments) |
| `binding_set_id` | null, string | 0..1 | Optional deterministic identifier/digest for the complete effective input-binding set of this invocation. | [/properties/assessment_result/properties/binding_set_id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/binding_set_id) |
| `input_bindings` | array | 0..1 | Effective named Assessment inputs for this invocation. | [/properties/assessment_result/properties/input_bindings](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings) |
| `evidence_summary` | object | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/evidence_summary](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_summary) |
| `target_ref` | string | 1..1 (required) | Reference to the evaluated target. | [/properties/assessment_result/properties/target_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/target_ref) |
| `expression_execution` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/expression_execution](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/expression_execution) |
| `field_uses` | array | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/field_uses](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses) |
| `item_report` | object | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/item_report](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/item_report) |
| `item_materialization` | object | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/item_materialization](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/item_materialization) |
| `evidence_retention` | object | Conditional (at most 1) | Records the effective per-Test Item retention limit and its source. | [/properties/assessment_result/properties/evidence_retention](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention) |

## `/properties/assessment_result/properties/assessment`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/assessment/properties/id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/assessment/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/assessment/properties/version](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/assessment/properties/version) |
| `digest` | null, string | 0..1 | Digest identifying the referenced content. | [/properties/assessment_result/properties/assessment/properties/digest](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/assessment/properties/digest) |

## `/properties/assessment_result/properties/manual_response`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `outcome` | string | 0..1 | Recorded evaluation outcome. | [/properties/assessment_result/properties/manual_response/properties/outcome](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/outcome) |
| `completed_at` | string | 0..1 | Timestamp recorded for the completion of execution. | [/properties/assessment_result/properties/manual_response/properties/completed_at](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/completed_at) |
| `started_at` | null, string | 0..1 | Timestamp recorded for the start of execution. | [/properties/assessment_result/properties/manual_response/properties/started_at](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/started_at) |
| `response_source` | string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/response_source](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/response_source) |
| `evaluator` | object | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator) |
| `review` | null, object | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/review](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/review) |
| `comments` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/comments](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/comments) |
| `evidence_refs` | array | 0..1 | References to the evidence supporting this result. | [/properties/assessment_result/properties/manual_response/properties/evidence_refs](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evidence_refs) |

## `/properties/assessment_result/properties/manual_response/properties/evaluator`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id) |
| `display_name` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/display_name](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/display_name) |
| `organization` | null, string | 0..1 | Organization associated with this declaration. | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/organization](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/organization) |
| `role` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/role](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/role) |
| `identity_source` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/identity_source](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/identity_source) |
| `organizational_unit` | null, string | 0..1 | Organizational unit associated with this declaration. | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/organizational_unit](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/organizational_unit) |
| `contact` | null, object | 0..1 | Contact information for the responsible party. | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact) |

## `/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `scheme` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id/properties/scheme](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id/properties/scheme) |
| `value` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id/properties/value](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/id/properties/value) |

## `/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `email` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/email](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/email) |
| `phone` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/phone](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/phone) |
| `uri` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/uri](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/manual_response/properties/evaluator/properties/contact/properties/uri) |

## `/properties/assessment_result/properties/consumed_organizational_inputs/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input` | string | 1..1 (required) | Identifier of the Input supplying the value. | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/input](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/input) |
| `value` | See schema | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/value](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/value) |
| `redacted` | boolean | 0..1 | Whether this value was redacted from reported evidence. | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/redacted](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/redacted) |
| `organizational_input_ref` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/organizational_input_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/organizational_input_ref) |
| `materialized` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/materialized](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/materialized) |
| `validation_status` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/validation_status](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/consumed_organizational_inputs/items/properties/validation_status) |

## `/properties/assessment_result/properties/dependent_assessments/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `alias` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/dependent_assessments/items/properties/alias](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/alias) |
| `assessment` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/dependent_assessments/items/properties/assessment](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/assessment) |
| `execution_id` | string | 1..1 (required) | Identifier of this execution. | [/properties/assessment_result/properties/dependent_assessments/items/properties/execution_id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/execution_id) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/assessment_result/properties/dependent_assessments/items/properties/outcome](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/outcome) |
| `purpose` | null, string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/dependent_assessments/items/properties/purpose](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/purpose) |
| `reused` | boolean | 1..1 (required) | Whether this result reuses prior execution evidence. | [/properties/assessment_result/properties/dependent_assessments/items/properties/reused](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/reused) |

## `/properties/assessment_result/properties/dependent_assessments/items/properties/assessment`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/id](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/version](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/version) |
| `digest` | null, string | 0..1 | Digest identifying the referenced content. | [/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/digest](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/dependent_assessments/items/properties/assessment/properties/digest) |

## `/properties/assessment_result/properties/input_bindings/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input` | string | 1..1 (required) | Identifier of the Input supplying the value. | [/properties/assessment_result/properties/input_bindings/items/properties/input](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings/items/properties/input) |
| `value` | See schema | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/input_bindings/items/properties/value](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings/items/properties/value) |
| `redacted` | boolean | 0..1 | Whether this value was redacted from reported evidence. | [/properties/assessment_result/properties/input_bindings/items/properties/redacted](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings/items/properties/redacted) |
| `source` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/input_bindings/items/properties/source](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings/items/properties/source) |
| `source_ref` | null, string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/input_bindings/items/properties/source_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/input_bindings/items/properties/source_ref) |

## `/properties/assessment_result/properties/field_uses/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `test_ref` | string | 1..1 (required) | Reference to the Test associated with this result. | [/properties/assessment_result/properties/field_uses/items/properties/test_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses/items/properties/test_ref) |
| `item_ref` | string | 1..1 (required) | Reference to the collected Item. | [/properties/assessment_result/properties/field_uses/items/properties/item_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses/items/properties/item_ref) |
| `used_elements` | array | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/field_uses/items/properties/used_elements](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses/items/properties/used_elements) |
| `required_elements` | array | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/field_uses/items/properties/required_elements](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses/items/properties/required_elements) |
| `relationship` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/field_uses/items/properties/relationship](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/field_uses/items/properties/relationship) |

## `/properties/assessment_result/properties/evidence_retention`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `scope` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/evidence_retention/properties/scope](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention/properties/scope) |
| `maximum_items` | integer, null | 1..1 (required) | Maximum retained Test-local per-Item records per Test. | [/properties/assessment_result/properties/evidence_retention/properties/maximum_items](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention/properties/maximum_items) |
| `source` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment_result/properties/evidence_retention/properties/source](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention/properties/source) |
| `override_reason` | string | Conditional (at most 1) | **Unresolved description** | [/properties/assessment_result/properties/evidence_retention/properties/override_reason](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention/properties/override_reason) |
| `operator_ref` | string | 0..1 | **Unresolved description** | [/properties/assessment_result/properties/evidence_retention/properties/operator_ref](../../../proposed-schema/documentation/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention/properties/operator_ref) |

## Advanced constraints

[Local constraints](../advanced/assessment-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/assessment-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
