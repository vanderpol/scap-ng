# SCAP-NG Manual Assessment v0.4.0 high-level draft

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Disposable high-level schema for simple, traceable human determinations. Intentionally avoids OCIL-style questionnaire/workflow graphs.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | object | 1..1 (required) | **Unresolved description** | [/properties/assessment](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment) |

## `/properties/assessment`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/id](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/id) |
| `version` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/version](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/version) |
| `assessment_title` | null, string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/assessment_title](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/assessment_title) |
| `mode` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/mode](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/mode) |
| `class` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/class](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/class) |
| `procedure` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/procedure](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/procedure) |
| `response` | object | 1..1 (required) | Small human-response contract. | [/properties/assessment/properties/response](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response) |
| `references` | array | 0..1 | **Unresolved description** | [/properties/assessment/properties/references](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/references) |
| `evidence_guidance` | null, string | 0..1 | **Unresolved description** | [/properties/assessment/properties/evidence_guidance](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/evidence_guidance) |

## `/properties/assessment/properties/response`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `type` | string | 1..1 (required) | Publisher-defined or standardized response vocabulary identifier. | [/properties/assessment/properties/response/properties/type](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/type) |
| `choices` | array | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/response/properties/choices](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/choices) |
| `allow_comment` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/response/properties/allow_comment](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/allow_comment) |
| `allow_evidence` | boolean | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/response/properties/allow_evidence](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/allow_evidence) |

## `/properties/assessment/properties/response/properties/choices/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `value` | string | 1..1 (required) | **Unresolved description** | [/properties/assessment/properties/response/properties/choices/items/properties/value](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/choices/items/properties/value) |
| `label` | null, string | 0..1 | **Unresolved description** | [/properties/assessment/properties/response/properties/choices/items/properties/label](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/choices/items/properties/label) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/assessment/properties/response/properties/choices/items/properties/outcome](../../../proposed-schema/documentation/manual-assessment.schema.json#/properties/assessment/properties/response/properties/choices/items/properties/outcome) |

## Advanced constraints

[Local constraints](../advanced/manual-assessment.md) and [complete JSON Schema](../../../proposed-schema/documentation/manual-assessment.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
