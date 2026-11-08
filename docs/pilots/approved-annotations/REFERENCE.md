# Approved description integration prototype

<!-- Generated: python tools/generate_approved_annotation_pilot.py -->

**Isolated next-version proposal; not the frozen 0.4.0 contract.**

| Element | Type | Description | Vocabulary / annotations |
| --- | --- | --- | --- |
| input-reference | object | Uses the value of a declared Input. |  |
| input-cardinality | string | Sets how many values a supplied Input may contain. | `exactly_one`, `zero_or_one`, `one_or_more`, `zero_or_more`. |
| input-required | boolean | Specifies whether this Input must be supplied. |  |
| field-predicate | object | Compares a collected field's values or checks for confirmed absence. |  |
| else-if | array | Selects the first true alternative branch when preceding conditions are false. |  |
| not-evaluated | object | Declares that this branch cannot be evaluated and provides a reason. |  |
| technical-outcome | string | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | `true`, `false`, `error`, `unknown`, `not_evaluated`, `not_applicable`. |
| value-redaction | boolean | Indicates that the value was intentionally omitted from the reported evidence. |  |

## Description origins

| Element | Authoritative proposal annotation |
| --- | --- |
| input-reference | [capability-common.schema.json](schema-next/capability-common.schema.json) `https://scap-ng.dev/schema/proposals/issue40/capability-common.schema.json#/$defs/input_reference/description` |
| input-cardinality | [assessment.schema.json](schema-next/assessment.schema.json) `https://scap-ng.dev/schema/proposals/issue40/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality/description` |
| input-required | [assessment.schema.json](schema-next/assessment.schema.json) `https://scap-ng.dev/schema/proposals/issue40/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required/description` |
| field-predicate | [assessment-language.schema.json](schema-next/assessment-language.schema.json) `https://scap-ng.dev/schema/proposals/issue40/assessment-language.schema.json#/$defs/canonical_field_predicate/description` |
| else-if | [expression.schema.json](schema-next/expression.schema.json) `https://scap-ng.dev/schema/proposals/issue40/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if/description` |
| not-evaluated | [expression.schema.json](schema-next/expression.schema.json) `https://scap-ng.dev/schema/proposals/issue40/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated/description` |
| technical-outcome | [result-types.schema.json](schema-next/result-types.schema.json) `https://scap-ng.dev/schema/proposals/issue40/result-types.schema.json#/$defs/technical_outcome/description` |
| value-redaction | [result-types.schema.json](schema-next/result-types.schema.json) `https://scap-ng.dev/schema/proposals/issue40/result-types.schema.json#/$defs/typed_value/properties/redacted/description` |

[Integration receipt and open routing decisions](RECEIPT.md).

Types and vocabulary come from the same schema nodes using PR #39’s shared inspector. Advanced assertions remain in the linked proposal schemas. Offline help follows explicit schema-node routes and local `$ref` edges; it is not a live VS Code hover or an instance-to-caret association test.
