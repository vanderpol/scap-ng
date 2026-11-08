# SCAP-NG Rule v0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `rule` | object | 1..1 (required) | Rule content, Assessment choices, and selection metadata. | [/properties/rule](../../../proposed-schema/documentation/rule.schema.json#/properties/rule) |

## `/properties/rule`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Rule identifier. | [/properties/rule/properties/id](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/id) |
| `version` | string | 1..1 (required) | Version of this Rule content. | [/properties/rule/properties/version](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/version) |
| `title` | string | 1..1 (required) | Human-readable Rule title. | [/properties/rule/properties/title](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/title) |
| `severity` | string | 1..1 (required) | Severity label assigned to the Rule. | [/properties/rule/properties/severity](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/severity) |
| `role` | string | 1..1 (required) | Role label assigned to the Rule. | [/properties/rule/properties/role](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/role) |
| `weight` | number | 1..1 (required) | Scoring weight declared for the Rule. | [/properties/rule/properties/weight](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/weight) |
| `discussion` | string | 0..1 | Discussion explaining the condition addressed by the Rule. | [/properties/rule/properties/discussion](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/discussion) |
| `rationale` | null, string | 0..1 | Reason for the Rule and its security objective. | [/properties/rule/properties/rationale](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/rationale) |
| `extensions` | object | 0..1 | Extension metadata carried by the Rule. | [/properties/rule/properties/extensions](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/extensions) |
| `warnings` | array | 0..1 | Warnings associated with using the Rule. | [/properties/rule/properties/warnings](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/warnings) |
| `identifiers` | array | 0..1 | External identifiers associated with the Rule. | [/properties/rule/properties/identifiers](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/identifiers) |
| `references` | array | 0..1 | External references supporting the Rule. | [/properties/rule/properties/references](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/references) |
| `requires` | array | 1..1 (required) | Selection prerequisites. | [/properties/rule/properties/requires](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/requires) |
| `conflicts` | array | 1..1 (required) | Rule identifiers declared as selection conflicts. | [/properties/rule/properties/conflicts](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/conflicts) |
| `applicability` | array | 1..1 (required) | Applicability declarations associated with the Rule. | [/properties/rule/properties/applicability](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/applicability) |
| `parameters` | object | 1..1 (required) | Parameter declarations or bindings associated with the Rule. | [/properties/rule/properties/parameters](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/parameters) |
| `remediation` | object | 0..1 | Remediation information associated with the Rule. | [/properties/rule/properties/remediation](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/remediation) |
| `assessment_choices` | object | 1..1 (required) | Publisher-defined Assessment choices. | [/properties/rule/properties/assessment_choices](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/assessment_choices) |
| `default_assessment_choice` | string | 1..1 (required) | Name of the publisher-defined Assessment choice selected as the default. | [/properties/rule/properties/default_assessment_choice](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/default_assessment_choice) |
| `organizational_input_requirements` | object | 0..1 | Compiler-derived Organizational Input discovery by Assessment choice. | [/properties/rule/properties/organizational_input_requirements](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements) |

## `/properties/rule/properties/assessment_choices/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 1..1 (required) | Reference to the Assessment used by this choice. | [/properties/rule/properties/assessment_choices/additionalProperties/properties/assessment](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/assessment_choices/additionalProperties/properties/assessment) |
| `inputs` | object | 0..1 | Assessment input name to Benchmark Parameter binding. | [/properties/rule/properties/assessment_choices/additionalProperties/properties/inputs](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/assessment_choices/additionalProperties/properties/inputs) |
| `expected_version` | integer, string | 0..1 | Exact logical Assessment version required to disambiguate multiple versions in the declared source scope. | [/properties/rule/properties/assessment_choices/additionalProperties/properties/expected_version](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/assessment_choices/additionalProperties/properties/expected_version) |

## `/properties/rule/properties/organizational_input_requirements/additionalProperties/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `input` | string | 1..1 (required) | Identifier of the Input supplying the value. | [/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/input](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/input) |
| `required` | boolean | 1..1 (required) | Requiredness recorded for this discovered Input. | [/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/required](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/required) |
| `uses` | array | 1..1 (required) | Locations where the selected Assessment references the Input. | [/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses) |

## `/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Value consumption versus an explicit Input-provision guard. | [/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses/items/properties/kind](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses/items/properties/kind) |
| `source_path` | string | 1..1 (required) | Canonical RFC6901 pointer to an actual Input reference scalar in the selected Assessment body; derived by the compiler, not manually authored coordinates. | [/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses/items/properties/source_path](../../../proposed-schema/documentation/rule.schema.json#/properties/rule/properties/organizational_input_requirements/additionalProperties/items/properties/uses/items/properties/source_path) |

## Advanced constraints

[Local constraints](../advanced/rule.md) and [complete JSON Schema](../../../proposed-schema/documentation/rule.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
