# SCAP-NG Manual Assessment Result v0.4.1 high-level draft

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Disposable high-level schema for a self-contained manual determination and its provenance.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `manual_assessment_result` | object | 1..1 (required) | Recorded answer and provenance for one manual Assessment execution. | [/properties/manual_assessment_result](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result) |

## `/properties/manual_assessment_result`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `result_schema_version` | string | 1..1 (required) | Version of the result serialization schema. | [/properties/manual_assessment_result/properties/result_schema_version](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/result_schema_version) |
| `execution_id` | string | 1..1 (required) | Identifier of this execution. | [/properties/manual_assessment_result/properties/execution_id](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/execution_id) |
| `assessment` | object | 1..1 (required) | Identity and version of the manual Assessment being reported. | [/properties/manual_assessment_result/properties/assessment](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/assessment) |
| `answer` | boolean, integer, null, number, string | 1..1 (required) | Exact response value selected or supplied under the Manual Assessment response contract. | [/properties/manual_assessment_result/properties/answer](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/answer) |
| `answer_label` | null, string | 0..1 | Human-readable label of the recorded manual answer. | [/properties/manual_assessment_result/properties/answer_label](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/answer_label) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/manual_assessment_result/properties/outcome](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/outcome) |
| `started_at` | null, string | 0..1 | Timestamp recorded for the start of execution. | [/properties/manual_assessment_result/properties/started_at](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/started_at) |
| `completed_at` | string | 1..1 (required) | Timestamp recorded for the completion of execution. | [/properties/manual_assessment_result/properties/completed_at](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/completed_at) |
| `response_source` | string | 1..1 (required) | Reported source of the manual response. | [/properties/manual_assessment_result/properties/response_source](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/response_source) |
| `evaluator` | object | 1..1 (required) | Identity and contact information recorded for the manual evaluator. | [/properties/manual_assessment_result/properties/evaluator](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator) |
| `comment` | null, string | 0..1 | Comment accompanying the manual response. | [/properties/manual_assessment_result/properties/comment](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/comment) |
| `evidence_refs` | array | 0..1 | References to the evidence supporting this result. | [/properties/manual_assessment_result/properties/evidence_refs](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evidence_refs) |
| `import_provenance` | null, object | 0..1 | Provenance recorded for an imported manual response. | [/properties/manual_assessment_result/properties/import_provenance](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/import_provenance) |
| `review` | null, object | 0..1 | Review metadata associated with the manual response. | [/properties/manual_assessment_result/properties/review](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/review) |
| `procedure_snapshot` | null, string | 0..1 | Optional snapshot when required for durable audit; normally source identity/digest is sufficient. | [/properties/manual_assessment_result/properties/procedure_snapshot](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/procedure_snapshot) |

## `/properties/manual_assessment_result/properties/assessment`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the Assessment being reported. | [/properties/manual_assessment_result/properties/assessment/properties/id](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/assessment/properties/id) |
| `version` | integer, string | 1..1 (required) | Version of the Assessment being reported. | [/properties/manual_assessment_result/properties/assessment/properties/version](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/assessment/properties/version) |
| `digest` | null, string | 0..1 | Digest identifying the referenced content. | [/properties/manual_assessment_result/properties/assessment/properties/digest](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/assessment/properties/digest) |

## `/properties/manual_assessment_result/properties/evaluator`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | object | 1..1 (required) | Structured identifier declared for the evaluator. | [/properties/manual_assessment_result/properties/evaluator/properties/id](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/id) |
| `display_name` | null, string | 0..1 | Display name recorded for the evaluator. | [/properties/manual_assessment_result/properties/evaluator/properties/display_name](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/display_name) |
| `organization` | null, string | 0..1 | Organization associated with this declaration. | [/properties/manual_assessment_result/properties/evaluator/properties/organization](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/organization) |
| `organizational_unit` | null, string | 0..1 | Organizational unit associated with this declaration. | [/properties/manual_assessment_result/properties/evaluator/properties/organizational_unit](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/organizational_unit) |
| `role` | null, string | 0..1 | Role label declared for the evaluator. | [/properties/manual_assessment_result/properties/evaluator/properties/role](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/role) |
| `identity_source` | null, string | 0..1 | Source named for the evaluator identity. | [/properties/manual_assessment_result/properties/evaluator/properties/identity_source](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/identity_source) |

## `/properties/manual_assessment_result/properties/evaluator/properties/id`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `scheme` | string | 1..1 (required) | Naming scheme of the evaluator identifier. | [/properties/manual_assessment_result/properties/evaluator/properties/id/properties/scheme](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/id/properties/scheme) |
| `value` | string | 1..1 (required) | Evaluator identifier within the named scheme. | [/properties/manual_assessment_result/properties/evaluator/properties/id/properties/value](../../../proposed-schema/documentation/manual-assessment-result.schema.json#/properties/manual_assessment_result/properties/evaluator/properties/id/properties/value) |

## Advanced constraints

[Local constraints](../advanced/manual-assessment-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/manual-assessment-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
