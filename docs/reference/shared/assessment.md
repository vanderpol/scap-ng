# SCAP-NG Assessment v0.4.0 draft

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Defines an Assessment's metadata and its manual procedure or automated checks.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | object | 1..1 (required) | Automated Assessments contain Test-local typed predicates and Object/Set-operand Filters with no named State registry. | [/properties/assessment](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment) |

## `/properties/assessment`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Assessment identifier. | [/properties/assessment/properties/id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/id) |
| `version` | integer, string | 1..1 (required) | Version of this Assessment content. | [/properties/assessment/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/version) |
| `assessment_title` | null, string | 1..1 (required) | Human-readable title for the Assessment. | [/properties/assessment/properties/assessment_title](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/assessment_title) |
| `mode` | string | 1..1 (required) | Selects whether the Assessment uses a manual procedure or automated Tests. | [/properties/assessment/properties/mode](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/mode) |
| `class` | string | 1..1 (required) | Classification of the Assessment. | [/properties/assessment/properties/class](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/class) |
| `variables` | object | 0..1 | Named typed variables. | [/properties/assessment/properties/variables](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/variables) |
| `tests` | object | Conditional (at most 1) | Defines the named Tests available to this Assessment. | [/properties/assessment/properties/tests](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests) |
| `evaluate` | object | Conditional (at most 1) | Combines Test and Assessment outcomes using Boolean operators and conditional expressions. | [/properties/assessment/properties/evaluate](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evaluate) |
| `procedure` | string | 0..1 | Manual procedure used to assess the condition. | [/properties/assessment/properties/procedure](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/procedure) |
| `inputs` | object | 0..1 | Named typed input contracts declared by the Assessment. | [/properties/assessment/properties/inputs](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs) |
| `evidence` | array | 0..1 | Defines the publisher’s evidence requirements and guidance for this Assessment. | [/properties/assessment/properties/evidence](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evidence) |
| `specification` | object | Conditional (at most 1) | Specification identifier and version used by this Assessment. | [/properties/assessment/properties/specification](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification) |
| `dependencies` | object | 0..1 | Statically declared dependencies on other Assessments whose final Assessment truth/result may be consumed by this Assessment's evaluate expression. | [/properties/assessment/properties/dependencies](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies) |
| `applicability` | null, object | 0..1 | Conditions limiting where this Assessment applies. | [/properties/assessment/properties/applicability](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/applicability) |
| `response` | See schema | 0..1 | Response information associated with the Assessment. | [/properties/assessment/properties/response](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/response) |
| `references` | See schema | 0..1 | External references supporting this Assessment. | [/properties/assessment/properties/references](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/references) |
| `evidence_guidance` | See schema | 0..1 | Instructions for recording assessment evidence. | [/properties/assessment/properties/evidence_guidance](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/evidence_guidance) |
| `shared_objects` | object | 0..1 | Assessment-scoped named Objects with meaningful reusable/referenceable acquisition identity. | [/properties/assessment/properties/shared_objects](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/shared_objects) |

## `/properties/assessment/properties/tests/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `test_title` | null, string | 1..1 (required) | Human-readable title for the Test. | [/properties/assessment/properties/tests/additionalProperties/properties/test_title](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/test_title) |
| `reported_elements` | array, string | Conditional (at most 1) | Required in saved automated Tests. | [/properties/assessment/properties/tests/additionalProperties/properties/reported_elements](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/reported_elements) |
| `capability` | string | 1..1 (required) | Identifies the native collector and its supported selector and result fields. | [/properties/assessment/properties/tests/additionalProperties/properties/capability](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/capability) |
| `object` | object, string | 0..1 | Defines the evidence source and selectors; an inline Object inherits its Test capability. | [/properties/assessment/properties/tests/additionalProperties/properties/object](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/object) |
| `variable` | string | 0..1 | Named Variable used as the native Test source where the capability supports variable.value. | [/properties/assessment/properties/tests/additionalProperties/properties/variable](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/variable) |
| `require` | object | 1..1 (required) | Structured collected-Item population and field requirements; no legacy State wrapper or implicit field default. | [/properties/assessment/properties/tests/additionalProperties/properties/require](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/tests/additionalProperties/properties/require) |

## `/properties/assessment/properties/inputs/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `datatype` | string | 1..1 (required) | Datatype used to interpret the value; payload validation and conversion rules are separate constraints. | [/properties/assessment/properties/inputs/additionalProperties/properties/datatype](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/datatype) |
| `cardinality` | string | 1..1 (required) | Sets how many values a supplied Input may contain. | [/properties/assessment/properties/inputs/additionalProperties/properties/cardinality](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality) |
| `required` | boolean | 1..1 (required) | Specifies whether this Input must be supplied. | [/properties/assessment/properties/inputs/additionalProperties/properties/required](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required) |
| `description` | null, string | 0..1 | Human explanation of the expected input and its policy meaning; not an executable requirement. | [/properties/assessment/properties/inputs/additionalProperties/properties/description](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/description) |
| `constraints` | object | 0..1 | Explicit constraints on supplied values. | [/properties/assessment/properties/inputs/additionalProperties/properties/constraints](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints) |

## `/properties/assessment/properties/inputs/additionalProperties/properties/constraints`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `allowed` | array | 0..1 | Lists the permitted values for this Input. | [/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed) |

## `/properties/assessment/properties/specification`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | SCAP-NG specification identifier. | [/properties/assessment/properties/specification/properties/id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification/properties/id) |
| `version` | string | 1..1 (required) | SCAP-NG language version used by the Assessment. | [/properties/assessment/properties/specification/properties/version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/specification/properties/version) |

## `/properties/assessment/properties/dependencies/additionalProperties`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `assessment` | string | 1..1 (required) | Logical Assessment ID in native 0.4 authoring; compiler resolves kind, identity, exact version and scope to a packaged reference. | [/properties/assessment/properties/dependencies/additionalProperties/properties/assessment](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/assessment) |
| `expected_id` | string | 0..1 | Transitional duplicate target identity for converted source; when present it SHALL match the resolved Assessment ID. | [/properties/assessment/properties/dependencies/additionalProperties/properties/expected_id](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/expected_id) |
| `expected_version` | integer, string | 1..1 (required) | Expected logical version of the referenced Assessment dependency. | [/properties/assessment/properties/dependencies/additionalProperties/properties/expected_version](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/expected_version) |
| `purpose` | string | 0..1 | Optional context for invoking this dependency. | [/properties/assessment/properties/dependencies/additionalProperties/properties/purpose](../../../proposed-schema/documentation/assessment.schema.json#/properties/assessment/properties/dependencies/additionalProperties/properties/purpose) |

## Advanced constraints

[Local constraints](../advanced/assessment.md) and [complete JSON Schema](../../../proposed-schema/documentation/assessment.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
