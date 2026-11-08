# SCAP-NG Rule Result pre-release v0.4.0

Proposed documentation. Defaults are schema annotations, not inferred scanner fallbacks. Conditional requirements and alternatives remain linked in the schema.

Embedded policy-facing Rule Result with bounded typed decisive facts. Assessment Results own the underlying technical execution.

## `/`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `rule_id` | string | 1..1 (required) | Identifier of the Rule being reported. | [/properties/rule_id](../../../proposed-schema/documentation/rule-result.schema.json#/properties/rule_id) |
| `title` | null, string | 0..1 | Title of the Rule being reported. | [/properties/title](../../../proposed-schema/documentation/rule-result.schema.json#/properties/title) |
| `severity` | null, string | 0..1 | Severity label recorded for the Rule result. | [/properties/severity](../../../proposed-schema/documentation/rule-result.schema.json#/properties/severity) |
| `outcome` | string | 1..1 (required) | Deterministic aggregate policy outcome derived from all Rule result instances. | [/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/properties/outcome) |
| `assessment` | null, object | 1..1 (required) | Identity of the effective selected Assessment for this Rule. | [/properties/assessment](../../../proposed-schema/documentation/rule-result.schema.json#/properties/assessment) |
| `summary` | string | 1..1 (required) | Required concise deterministic human-readable explanation of the Rule outcome and decisive cause, consistent with findings, finding_counts, and the referenced Assessment Results; never just the outcome label. | [/properties/summary](../../../proposed-schema/documentation/rule-result.schema.json#/properties/summary) |
| `reason` | null, object, string | 0..1 | Explanation of the reported outcome. | [/properties/reason](../../../proposed-schema/documentation/rule-result.schema.json#/properties/reason) |
| `evidence_refs` | array | 0..1 | Optional references to decisive evidence or Assessment-result evidence members; evidence is not embedded here. | [/properties/evidence_refs](../../../proposed-schema/documentation/rule-result.schema.json#/properties/evidence_refs) |
| `instances` | array | 1..1 (required) | Explicit result instances contributing to this policy-facing Rule Result. | [/properties/instances](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances) |
| `weight` | null, number | 0..1 | Effective Rule weight used by the selected scoring model, when defined. | [/properties/weight](../../../proposed-schema/documentation/rule-result.schema.json#/properties/weight) |
| `check_selector` | null, string | 0..1 | Effective named Assessment/check selector chosen for this Rule. | [/properties/check_selector](../../../proposed-schema/documentation/rule-result.schema.json#/properties/check_selector) |
| `parameters` | object | 0..1 | Effective publisher/Profile/Tailoring Parameters materially relevant to this Rule result. | [/properties/parameters](../../../proposed-schema/documentation/rule-result.schema.json#/properties/parameters) |
| `organizational_inputs` | array | 0..1 | Concise organization-defined expected policy values actually used by this Rule, each linked to the single authoritative Benchmark Result effective_policy.organizational_inputs assertion. | [/properties/organizational_inputs](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs) |
| `applicability` | null, object | 0..1 | Rule-level applicability disposition plus references to the applicability Assessment Results that produced it; detailed execution data is not embedded here. | [/properties/applicability](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability) |
| `findings` | array | 1..1 (required) | Bounded decisive Assessment-derived typed facts. | [/properties/findings](../../../proposed-schema/documentation/rule-result.schema.json#/properties/findings) |
| `finding_counts` | object | 0..1 | Optional collection summary: evaluated population and actual failures are distinct from returned evidence. | [/properties/finding_counts](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts) |
| `subject` | object | Definition | Identity metadata for the subject of a finding. | [/$defs/subject](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/subject) |
| `comparison_finding` | object | Definition | Comparison finding with its subject, field and operation. | [/$defs/comparison_finding](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding) |
| `missing_finding` | object | Definition | Missing required resource or inconclusive collection; no fictional Item. | [/$defs/missing_finding](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding) |

## `/properties/instances/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of this reported Rule instance. | [/properties/instances/items/properties/id](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/id) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/instances/items/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/outcome) |
| `assessment_result_ref` | null, string | 1..1 (required) | Manifest logical Assessment execution identity, never a guessed artifact filename. | [/properties/instances/items/properties/assessment_result_ref](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/assessment_result_ref) |
| `assessment_invocation_id` | null, string | 0..1 | Identifier of the Assessment invocation associated with this Rule instance. | [/properties/instances/items/properties/assessment_invocation_id](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/assessment_invocation_id) |
| `target_instance` | null, string | 0..1 | Target-instance label recorded for this Rule instance. | [/properties/instances/items/properties/target_instance](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/target_instance) |
| `check_instance` | null, string | 0..1 | Check-instance label recorded for this Rule instance. | [/properties/instances/items/properties/check_instance](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/check_instance) |
| `message` | null, string | 0..1 | Human-readable diagnostic message. | [/properties/instances/items/properties/message](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/message) |
| `reason` | null, object, string | 0..1 | Explanation of the reported outcome. | [/properties/instances/items/properties/reason](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/reason) |
| `evidence_refs` | array | 0..1 | References to the evidence supporting this result. | [/properties/instances/items/properties/evidence_refs](../../../proposed-schema/documentation/rule-result.schema.json#/properties/instances/items/properties/evidence_refs) |

## `/properties/organizational_inputs/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `parameter` | string | 1..1 (required) | Effective organization-resolved Benchmark Parameter. | [/properties/organizational_inputs/items/properties/parameter](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/parameter) |
| `organizational_input_ref` | string | 1..1 (required) | Exact key in benchmark_result.effective_policy.organizational_inputs, not a source filename. | [/properties/organizational_inputs/items/properties/organizational_input_ref](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/organizational_input_ref) |
| `value` | See schema | Conditional (at most 1) | Effective expected policy value; the same typed JSON value as the authoritative assertion, unless disclosure is restricted. | [/properties/organizational_inputs/items/properties/value](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/value) |
| `redacted` | boolean | 1..1 (required) | Explicit policy-value redaction indicator; never combine true with value. | [/properties/organizational_inputs/items/properties/redacted](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/redacted) |
| `provenance_summary` | object | 0..1 | Optional concise nonauthoritative authority summary from the referenced Benchmark assertion, not a second provenance truth. | [/properties/organizational_inputs/items/properties/provenance_summary](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/provenance_summary) |

## `/properties/organizational_inputs/items/properties/provenance_summary`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `organization` | string | 0..1 | Organization associated with this declaration. | [/properties/organizational_inputs/items/properties/provenance_summary/properties/organization](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/provenance_summary/properties/organization) |
| `authorization_reference` | string | 0..1 | Reference documenting the authorization. | [/properties/organizational_inputs/items/properties/provenance_summary/properties/authorization_reference](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/provenance_summary/properties/authorization_reference) |
| `effective_from` | string | 0..1 | Timestamp from which this declaration applies. | [/properties/organizational_inputs/items/properties/provenance_summary/properties/effective_from](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/provenance_summary/properties/effective_from) |
| `expires_at` | string | 0..1 | Timestamp at which this declaration expires. | [/properties/organizational_inputs/items/properties/provenance_summary/properties/expires_at](../../../proposed-schema/documentation/rule-result.schema.json#/properties/organizational_inputs/items/properties/provenance_summary/properties/expires_at) |

## `/properties/applicability`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/applicability/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/outcome) |
| `conditions` | array | 1..1 (required) | Individual applicability-condition observations for this Rule. | [/properties/applicability/properties/conditions](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions) |

## `/properties/applicability/properties/conditions/items`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `id` | string | 1..1 (required) | Identifier of the reported applicability condition. | [/properties/applicability/properties/conditions/items/properties/id](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions/items/properties/id) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/properties/applicability/properties/conditions/items/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions/items/properties/outcome) |
| `assessment_result_ref` | null, string | 0..1 | Reference to the Assessment result supporting the applicability observation. | [/properties/applicability/properties/conditions/items/properties/assessment_result_ref](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions/items/properties/assessment_result_ref) |
| `assessment_invocation_id` | null, string | 0..1 | Identifier of the Assessment invocation supporting the applicability observation. | [/properties/applicability/properties/conditions/items/properties/assessment_invocation_id](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions/items/properties/assessment_invocation_id) |
| `reason` | null, object, string | 0..1 | Explanation of the reported outcome. | [/properties/applicability/properties/conditions/items/properties/reason](../../../proposed-schema/documentation/rule-result.schema.json#/properties/applicability/properties/conditions/items/properties/reason) |

## `/properties/finding_counts`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `evaluated_items` | integer | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/evaluated_items](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/evaluated_items) |
| `observed_violations` | integer | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/observed_violations](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/observed_violations) |
| `actual_violations` | integer, string | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/actual_violations](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/actual_violations) |
| `population_complete` | boolean | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/population_complete](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/population_complete) |
| `reported_items` | integer | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/reported_items](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/reported_items) |
| `sample_truncated` | boolean | 1..1 (required) | **Unresolved description** | [/properties/finding_counts/properties/sample_truncated](../../../proposed-schema/documentation/rule-result.schema.json#/properties/finding_counts/properties/sample_truncated) |

## `/$defs/subject`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Kind of subject identified by the finding. | [/$defs/subject/properties/kind](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/subject/properties/kind) |
| `identifier` | string | 1..1 (required) | Identifier of the subject described by the finding. | [/$defs/subject/properties/identifier](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/subject/properties/identifier) |

## `/$defs/comparison_finding`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Identifies a finding from a comparison. | [/$defs/comparison_finding/properties/kind](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/kind) |
| `instance_id` | string | 1..1 (required) | Identifier of the Rule instance associated with this finding. | [/$defs/comparison_finding/properties/instance_id](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/instance_id) |
| `subject` | object | 1..1 (required) | Subject to which the comparison finding applies. | [/$defs/comparison_finding/properties/subject](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/subject) |
| `field` | string | 1..1 (required) | Name of the field involved in the comparison. | [/$defs/comparison_finding/properties/field](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/field) |
| `operation` | string | 1..1 (required) | Comparison operation recorded for the finding. | [/$defs/comparison_finding/properties/operation](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/operation) |
| `expected` | object | 1..1 (required) | A typed scalar or record result value. | [/$defs/comparison_finding/properties/expected](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/expected) |
| `observed` | object | 1..1 (required) | A typed scalar or record result value. | [/$defs/comparison_finding/properties/observed](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/observed) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/$defs/comparison_finding/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/outcome) |
| `test_ref` | string | 0..1 | Reference to the Test associated with this result. | [/$defs/comparison_finding/properties/test_ref](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/test_ref) |
| `item_ref` | string | 0..1 | Reference to the collected Item. | [/$defs/comparison_finding/properties/item_ref](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/comparison_finding/properties/item_ref) |

## `/$defs/missing_finding`

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `kind` | string | 1..1 (required) | Identifies a finding about expected presence or absence. | [/$defs/missing_finding/properties/kind](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/kind) |
| `instance_id` | string | 1..1 (required) | Identifier of the Rule instance associated with this finding. | [/$defs/missing_finding/properties/instance_id](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/instance_id) |
| `subject` | object | 1..1 (required) | Subject to which the presence finding applies. | [/$defs/missing_finding/properties/subject](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/subject) |
| `predicate` | string | 1..1 (required) | Presence predicate recorded for the finding. | [/$defs/missing_finding/properties/predicate](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/predicate) |
| `expected_existence` | string | 1..1 (required) | Presence or absence expected by the predicate. | [/$defs/missing_finding/properties/expected_existence](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/expected_existence) |
| `observed_existence` | string | 1..1 (required) | Presence status reported for the subject. | [/$defs/missing_finding/properties/observed_existence](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/observed_existence) |
| `outcome` | string | 1..1 (required) | Recorded evaluation outcome. | [/$defs/missing_finding/properties/outcome](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/outcome) |
| `test_ref` | string | 0..1 | Reference to the Test associated with this result. | [/$defs/missing_finding/properties/test_ref](../../../proposed-schema/documentation/rule-result.schema.json#/$defs/missing_finding/properties/test_ref) |

## Advanced constraints

[Local constraints](../advanced/rule-result.md) and [complete JSON Schema](../../../proposed-schema/documentation/rule-result.schema.json) contain conditional requirements, alternatives, bounds and validation expressions. A mapping property occurs at most once; `items`, `minItems` and `maxItems` constrain array members separately. A definition is reusable schema grammar, not itself an authored mapping key.
