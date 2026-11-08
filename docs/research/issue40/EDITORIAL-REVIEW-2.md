# Editorial review batch 2

**No canonical edits or normative approval.**

**28 new descriptions, all pending editorial review.** Jack decides marked semantic questions; no independent editorial approval is claimed.

Native pin: `7354a24cdbfe18321153ccaef5d772801a10cd71`. Full schema URIs use `https://scap-ng.dev/schema/v0.4.0/`; every file/pointer and source hash is recorded in [editorial-batch-2.json](editorial-batch-2.json).

56 positive/negative syntax witnesses were checked against the pinned definitions, including parent-context cases. They do not execute collection, evaluation or transformations and do not establish runtime equivalence.

## Edited author-facing candidates

| Case / element | `author_description` | Classification / disposition |
| --- | --- | --- |
| [01 Assessment.mode](#case-01) | Selects whether the Assessment uses a manual procedure or automated Tests. | editorial; pending editorial review |
| [02 Assessment.tests](#case-02) | Defines the named Tests available to this Assessment. | editorial; pending editorial review |
| [03 Input.cardinality](#case-03) | Sets how many values a supplied Input may contain. | editorial; pending editorial review |
| [04 Input.required](#case-04) | Specifies whether this Input must be supplied. | editorial; pending editorial review |
| [05 Input.constraints.allowed](#case-05) | Lists the permitted values for this Input. | editorial; pending editorial review |
| [06 Variable.kind](#case-06) | Distinguishes a derived Variable from a constant literal. | editorial; pending editorial review |
| [07 Variable.datatype](#case-07) | Declares the datatype of this Variable’s values. | **semantic decision needed**; pending editorial review |
| [08 Variable literal](#case-08) | Supplies a literal value, list of values, or explicitly typed value. | editorial; pending editorial review |
| [09 Variable collected values](#case-09) | Reads a field from the Items collected by an Object. | editorial; pending editorial review |
| [10 evaluate.test](#case-10) | Uses a named Test’s outcome in this expression. | editorial; pending editorial review |
| [11 evaluate.assessment](#case-11) | Uses a referenced Assessment’s outcome in this expression. | editorial; pending editorial review |
| [12 evaluate.if](#case-12) | Tests the condition that selects a conditional branch. | editorial; pending editorial review |
| [13 evaluate.else_if](#case-13) | Selects the first true alternative branch when preceding conditions are false. | editorial; pending editorial review |
| [14 evaluate.and](#case-14) | Combines expression outcomes using logical AND. | editorial; pending editorial review |
| [15 evaluate.or](#case-15) | Combines expression outcomes using logical OR. | editorial; pending editorial review |
| [16 evaluate.one](#case-16) | Requires exactly one child expression to be true. | **semantic decision needed**; pending editorial review |
| [17 evaluate.xor](#case-17) | Combines expression outcomes using exclusive OR. | **semantic decision needed**; pending editorial review |
| [18 evaluate.not_evaluated](#case-18) | Records why this branch could not be evaluated. | editorial; pending editorial review |
| [19 evaluate.not_applicable](#case-19) | Records why this branch does not apply. | editorial; pending editorial review |
| [20 Existence-only Require](#case-20) | Checks whether the required number of Items exists without comparing fields. | editorial; pending editorial review |
| [21 Confirmed field absence](#case-21) | Requires confirmed absence of the field’s values. | editorial; pending editorial review |
| [22 Require.fields](#case-22) | Requires all listed field conditions to hold for an Item. | editorial; pending editorial review |
| [23 Technical outcome](#case-23) | Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable. | editorial; pending editorial review |
| [24 Collection status](#case-24) | Reports the outcome of collecting an Object’s Items. | editorial; pending editorial review |
| [25 Value redaction](#case-25) | Indicates that the value was intentionally omitted from the reported evidence. | editorial; pending editorial review |
| [26 Collection Item references](#case-26) | Identifies the Items retained or referenced by this collection result. | editorial; pending editorial review |
| [27 Result evidence retention](#case-27) | Records the effective per-Test Item retention limit and its source. | editorial; pending editorial review |
| [28 Assessment.evidence](#case-28) | Defines the publisher’s evidence requirements and guidance for this Assessment. | editorial; pending editorial review |

## Sources, initial drafts and engineering notes

Open a case for its exact pointer, existing local/inherited help, original Codex proposal and separate engineering note. Source verification is an editorial prerequisite, not approval to install a description.

<a id="case-01"></a>
<details>
<summary>01 — Assessment.mode</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/mode`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Select a manual or automated Assessment.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Selects whether the Assessment uses a manual procedure or automated Tests.

**Separate `engineering_note`:** The parent conditional requires procedure for manual mode and specification/tests/evaluate for automated mode. This choice does not establish execution support.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/mode`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-02"></a>
<details>
<summary>02 — Assessment.tests</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/tests`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** Named Tests. A capability defines its Test source shape: commonly an Object, but clean native capabilities MAY consume another first-class source such as a Variable directly.

**Codex proposal:** Declares named automated Tests and their acquisition and Require conditions.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Defines the named Tests available to this Assessment.

**Separate `engineering_note`:** Describe the Test registry here; acquisition sources remain capability-dependent. Test IDs end in -test. Source selectors and Require conditions are not new semantics. Syntax does not resolve evaluate references.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/tests`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-03"></a>
<details>
<summary>03 — Input.cardinality</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** Allowed number of supplied values. This is independent from whether the Input must be provided: a provided empty population is distinct from an omitted binding.

**Codex proposal:** Declare the permitted population size of a supplied Input.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Sets how many values a supplied Input may contain.

**Separate `engineering_note`:** Provision and value count are independent; zero values when provided are distinct from omission. Schema witnesses validate the declaration, not actual binding populations. Preserve the existing required flag as separate authority.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/cardinality`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-04"></a>
<details>
<summary>04 — Input.required</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** Whether an invocation must supply this Input. False permits omission, never an invented default or empty population. Optional consumers must be dominated by an explicit input_provided conditional guard.

**Codex proposal:** Declare whether invocation must supply this Input.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Specifies whether this Input must be supplied.

**Separate `engineering_note`:** False permits omission without inventing a default. Optional consumers need the accepted direct input_provided guard; this leaf does not enforce reference dominance. The witness intentionally allows required true with zero_or_more cardinality.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/required`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-05"></a>
<details>
<summary>05 — Input.constraints.allowed</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** Explicit allowed values in the declared domain; no casts or defaults.

**Codex proposal:** Restrict supplied Input values to an explicit list.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Lists the permitted values for this Input.

**Separate `engineering_note`:** No conversion or defaults. The declaration shape accepts mixed scalar/object entries; domain membership and datatype agreement need semantic validation. This does not promise JSON Schema enforces binding compatibility.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/inputs/additionalProperties/properties/constraints/properties/allowed`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-06"></a>
<details>
<summary>06 — Variable.kind</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/kind`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/variable-expression.schema.json)

**Existing local wording:** Use `local` for a derived value or `constant` for a literal declaration.

**Codex proposal:** Choose local derivation or a constant literal declaration.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Distinguishes a derived Variable from a constant literal.

**Separate `engineering_note`:** The constant branch requires a literal expression; local may also use literals. Do not imply local must be a transform or that this keyword alone executes a function.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/kind`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-07"></a>
<details>
<summary>07 — Variable.datatype</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/datatype`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/variable-expression.schema.json)

**Existing local wording:** Datatype promised by this Variable. The expression must produce compatible values.

**Codex proposal:** Declare the datatype promised by a Variable expression.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Declares the datatype of this Variable’s values.

**Separate `engineering_note`:** The enum is enforced, but full declaration-to-expression compatibility and casts are not established by these witnesses. Retain a semantic hold for the strength of this promise; do not imply coercion or complete tag/payload validation.

**Classification:** semantic_decision_needed; **editorial status:** pending_editorial_review; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/datatype`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-08"></a>
<details>
<summary>08 — Variable literal</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/variable-expression.schema.json)

**Existing local wording:** A scalar, ordered list, or explicitly typed value. Use the typed form when the datatype matters; lists preserve their supplied order and duplicates.

**Codex proposal:** Supply literal scalar, list or typed data.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Supplies a literal value, list of values, or explicitly typed value.

**Separate `engineering_note`:** Use this single expression-node authority for the duplicate constant-declaration literal shape; do not copy help into both. Lists preserve order and duplicates under the existing description. Casting and status semantics are not introduced.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/0/properties/literal`; related consumers: `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/allOf/0/then/properties/expression/properties/literal`.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-09"></a>
<details>
<summary>09 — Variable collected values</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/variable-expression.schema.json)

**Existing local wording:** Read the selected field from the collected Object. Field availability, multiplicity, and collection status are semantic/runtime concerns.

**Codex proposal:** Read one named field from an Object collection.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Reads a field from the Items collected by an Object.

**Separate `engineering_note`:** This operation selects one field from collected Items; missing values, multiplicity, result ordering and status propagation remain engineering questions, not claims in this sentence. Object reference resolution is separate.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/2/properties/values`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-10"></a>
<details>
<summary>10 — evaluate.test</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/0/properties/test`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Refer to a local Test outcome in evaluation.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Uses a named Test’s outcome in this expression.

**Separate `engineering_note`:** The name pattern is checked here, but existence and scope resolution are semantic checks. This names an expression operand, not the shared acquisition reference or a stored finalized Result.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/0/properties/test`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-11"></a>
<details>
<summary>11 — evaluate.assessment</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/1/properties/assessment`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Refer to an Assessment dependency outcome.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Uses a referenced Assessment’s outcome in this expression.

**Separate `engineering_note`:** The string leaf does not enforce dependency declaration, resolution, version or cycle rules. Assessment.dependencies separately declares aliases. Do not promise automatic discovery or reading stored Results.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/1/properties/assessment`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-12"></a>
<details>
<summary>12 — evaluate.if</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/2/properties/if`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Select a conditional branch using an outcome or Input provision guard.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Tests the condition that selects a conditional branch.

**Separate `engineering_note`:** The condition accepts an expression or direct Input presence guard. then and else are required on the containing conditional; no default else or Boolean collapse of error/unknown is inferred.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/2/properties/if`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-13"></a>
<details>
<summary>13 — evaluate.else_if</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** Ordered alternative branches. A conditional evaluator chooses the first true condition, evaluates only its then expression and skips later branches. Indeterminate conditions propagate rather than falling through.

**Codex proposal:** Ordered conditional alternatives, first true condition selects its then branch.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Selects the first true alternative branch when preceding conditions are false.

**Separate `engineering_note`:** The existing native description explicitly defines first-true selection, skipped later branches and propagation of indeterminate conditions. This wording retains that contract without advertising fall-through for unknown/error. Else_if is the actual spelling.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/2/properties/else_if`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-14"></a>
<details>
<summary>14 — evaluate.and</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/4/properties/and`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** Logical AND of complete Test outcomes; separate from Test Item matching.

**Codex proposal:** Apply logical AND to child outcomes.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Combines expression outcomes using logical AND.

**Separate `engineering_note`:** This operates on expression outcomes, including nested expressions and Assessment references; it is separate from Item/field quantifiers. No new six-state truth table or short-circuit guarantee is proposed.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/4/properties/and`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-15"></a>
<details>
<summary>15 — evaluate.or</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/5/properties/or`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** Logical OR of complete Test outcomes; separate from Test Item matching.

**Codex proposal:** Apply logical OR to child outcomes.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Combines expression outcomes using logical OR.

**Separate `engineering_note`:** This operates on expression outcomes, including nested expressions and Assessment references; it is separate from Item/field quantifiers. No new six-state truth table or short-circuit guarantee is proposed.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/5/properties/or`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-16"></a>
<details>
<summary>16 — evaluate.one</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/8/properties/one`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Apply logical ONE to child outcomes.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Requires exactly one child expression to be true.

**Separate `engineering_note`:** The active grammar supports this operator and a nonempty recursive operand list. Confirm multi-state truth/indeterminate aggregation before clearing this proposed meaning; structural acceptance alone proves neither truth tables nor evaluation order.

**Classification:** semantic_decision_needed; **editorial status:** pending_editorial_review; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/8/properties/one`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-17"></a>
<details>
<summary>17 — evaluate.xor</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/9/properties/xor`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** Logical XOR of complete Test outcomes; separate from Test Item matching.

**Codex proposal:** Apply logical XOR to child outcomes.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Combines expression outcomes using exclusive OR.

**Separate `engineering_note`:** The active grammar supports this operator and a nonempty recursive operand list. Confirm multi-state truth/indeterminate aggregation before clearing this proposed meaning; structural acceptance alone proves neither truth tables nor evaluation order.

**Classification:** semantic_decision_needed; **editorial status:** pending_editorial_review; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/9/properties/xor`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-18"></a>
<details>
<summary>18 — evaluate.not_evaluated</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** Author-declared, evidence-backed inability to complete a branch. Not a substitute for a failed check, a collection error, or a proven not-applicable condition.

**Codex proposal:** Declare an evidence-backed inability to complete a branch.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Records why this branch could not be evaluated.

**Separate `engineering_note`:** The existing contract distinguishes this declared limitation from failed checks, collection errors and proven non-applicability. Nonblank reason is required; optional follow_up directs review. A runtime outcome is not executed by this syntax witness.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/6/properties/not_evaluated`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-19"></a>
<details>
<summary>19 — evaluate.not_applicable</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/expression.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Declare a reasoned non-applicable branch.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Records why this branch does not apply.

**Separate `engineering_note`:** The form requires a nonblank reason. Syntax does not establish the applicability predicate, truth table or adequacy of supporting evidence; do not use this form to mask unknown/error outcomes.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/expression/oneOf/7/properties/not_applicable`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-20"></a>
<details>
<summary>20 — Existence-only Require</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/item_presence_requirement`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment-language.schema.json)

**Existing local wording:** Checks population existence without comparing State predicates; corresponds to State-free OVAL check_existence.

**Codex proposal:** Check selected Item population existence without comparing fields.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Checks whether the required number of Items exists without comparing fields.

**Separate `engineering_note`:** This is the distinct comparator-free Require alternative, not the comparison branch reviewed in batch 1. It forbids items_satisfying and field predicates; source OVAL attributes remain provenance, not new vocabulary.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/item_presence_requirement`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-21"></a>
<details>
<summary>21 — Confirmed field absence</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/absence_only_field_predicate`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment-language.schema.json)

**Existing local wording:** The only comparator-free field condition is confirmed absence, not an empty value or failed collection.

**Codex proposal:** Express confirmed absence using values_found none alone.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Requires confirmed absence of the field’s values.

**Separate `engineering_note`:** Distinct from the generic field-predicate summary in batch 1: this is the sole comparator-free field alternative. Empty strings and error/not_collected statuses are not confirmed absence. Any comparator or values_matching alongside none is forbidden.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/absence_only_field_predicate`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-22"></a>
<details>
<summary>22 — Require.fields</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment-language.schema.json)

**Existing local wording:** One complete condition; distinct fields are combined with logical AND.

**Codex proposal:** Combine named field predicates into one complete condition.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Requires all listed field conditions to hold for an Item.

**Separate `engineering_note`:** The existing fields description defines implicit AND of distinct fields; Item satisfaction quantification remains separate. Proposed single owner for analogous fields mappings in canonical_condition and canonical_inherited_condition; no text copying or reference rewrites are applied.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields`; related consumers: `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_condition/oneOf/0/properties/fields`, `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_inherited_condition/oneOf/0/properties/fields`.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-23"></a>
<details>
<summary>23 — Technical outcome</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/technical_outcome`

**Source file:** [schema/result-types.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/result-types.schema.json)

**Existing local wording:** Six-state technical Assessment/Test outcome. Informational is deliberately not a seventh technical truth value.

**Codex proposal:** Record the six-state Assessment or Test technical outcome.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Reports whether a Test or Assessment is true, false, errored, unknown, unevaluated, or inapplicable.

**Separate `engineering_note`:** This shared definition owns technical outcome help for Result consumers. The constraint table retains all six exact enum spellings. No Rule pass/fail mapping or new multi-state truth table is implied.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/technical_outcome`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-24"></a>
<details>
<summary>24 — Collection status</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#/properties/status`

**Source file:** [schema/collection-result.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/collection-result.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Record the collection outcome separately from Boolean evaluation.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Reports the outcome of collecting an Object’s Items.

**Separate `engineering_note`:** Show all six enum spellings in the constraint table. does_not_exist and not_collected remain separate statuses even though this sentence summarizes rather than enumerates them. Error/incomplete require nonblank diagnostics and stop_reason; incomplete requires population_complete false. No mapping to technical outcomes is inferred.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#/properties/status`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-25"></a>
<details>
<summary>25 — Value redaction</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/redacted`

**Source file:** [schema/result-types.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/result-types.schema.json)

**Existing local wording:** When true, the value has been intentionally omitted from emitted results/evidence. A redacted typed value SHALL NOT carry a value property.

**Codex proposal:** Indicate intentional omission of a value from results.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Indicates that the value was intentionally omitted from the reported evidence.

**Separate `engineering_note`:** True forbids the value property; this is distinct from a collection error or missing source value. False does not require value for every datatype/status. No new redaction policy or acquisition behavior is proposed.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/redacted`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-26"></a>
<details>
<summary>26 — Collection Item references</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#/properties/item_refs`

**Source file:** [schema/collection-result.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/collection-result.schema.json)

**Existing local wording:** Identities of Items retained or materially referenced in this result. An evidence cap SHALL NOT require enumeration of every collected Item ID; evaluated population and truncation are reported via Assessment/Test summary and collection completeness.

**Codex proposal:** List retained or materially referenced Item identities.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Identifies the Items retained or referenced by this collection result.

**Separate `engineering_note`:** The existing description explicitly permits bounded retention without enumerating the full evaluated population. This list is evidence references, not a collection count or completeness proof. Reference existence/identity checks are outside this array shape.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#/properties/item_refs`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-27"></a>
<details>
<summary>27 — Result evidence retention</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention`

**Source file:** [schema/assessment-result.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment-result.schema.json)

**Existing local wording:** Effective application/run-controlled retained Item limit, never an evaluation threshold and never a reason to fork Benchmark/Assessment content. An operator override changes reporting volume only, subject to separately enforced resource limits and reported_elements/redaction.

**Codex proposal:** Describe the effective reporting limit and how it was selected.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Records the effective per-Test Item retention limit and its source.

**Separate `engineering_note`:** This controls reporting volume, not evaluation thresholds. Null maximum_items requests no item-count cap while resource safety/redaction still apply. operator_override requires override_reason; other sources forbid override metadata. No default cap is invented.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-result.schema.json#/properties/assessment_result/properties/evidence_retention`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-28"></a>
<details>
<summary>28 — Assessment.evidence</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/evidence`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/7354a24cdbfe18321153ccaef5d772801a10cd71/schema/assessment.schema.json)

**Existing local wording:** Publisher-authored evidence requirements/guidance for this Assessment. This is source policy metadata, not collected runtime evidence; observed evidence belongs in Assessment Results or referenced evidence artifacts.

**Codex proposal:** Provide publisher-authored evidence guidance rather than observations.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Defines the publisher’s evidence requirements and guidance for this Assessment.

**Separate `engineering_note`:** This source policy metadata is separate from observed runtime evidence in Results/artifacts. Array entry shapes remain unconstrained here; the sentence does not promise enforcement of a guidance format.

**Classification:** editorial; **editorial status:** pending_editorial_review; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/evidence`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

## Review gate

Approve style separately from behavior. A semantic-decision row remains pending even if its sentence reads well. The batch 1 foreach case remains withheld until placement is decided. None of these candidates is added to the bulk patch bundle, installed in an editor or written to a canonical schema.

**Stop for editorial review.** No bulk shortening of the 1,580 findings, schema edit, editor repin, migration or merge.
