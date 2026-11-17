# Editorial review batch 1

**No canonical edits or normative approval.**

Batch 1 editorial receipt: **21 accepted descriptions** (18 as written, 3 revised), **6 semantic holds**, **1 withheld**. Uses the explicit reviewed list of 18 accepted IDs plus the three approved wording revisions. [Independent review](https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721578815) · [Owner authorization](https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721594181).

Native pin: `63110e7762f4963d3e4d407e90b9fcfd9cfe86ad`. Full schema URIs use `https://scap-ng.dev/schema/v0.4.0/`; every file/pointer and source hash is recorded in [editorial-batch.json](editorial-batch.json).

55 positive/negative syntax witnesses were checked against the pinned definitions, including parent-context cases. They do not execute collection, evaluation or transformations and do not establish runtime equivalence.

## Edited author-facing candidates

| Case / element | `author_description` | Classification / disposition |
| --- | --- | --- |
| [01 input_reference](#case-01) | Uses the value of a declared Input. | editorial; accepted as written |
| [02 variable_reference](#case-02) | Uses the value of a declared Variable. | editorial; accepted as written |
| [03 object_reference](#case-03) | Reuses a named Object for collection. | editorial; accepted as written |
| [04 evaluate](#case-04) | Combines Test and Assessment outcomes using Boolean operators and conditional expressions. | editorial; accepted with revision |
| [05 input_provided](#case-05) | Checks whether a declared Input was supplied, even if its value is empty. | editorial; accepted as written |
| [06 Variable expression](#case-06) | Defines how this Variable's values are obtained. | editorial; accepted as written |
| [07 canonical_field_predicate](#case-07) | Compares a collected field's values or checks for confirmed absence. | editorial; accepted with revision |
| [08 Comparison Require](#case-08) | Defines the Item counts and field conditions for a comparison Test. | editorial; accepted as written |
| [09 item_requirement](#case-09) | Sets how many Items must be found and how many must satisfy the comparison. | editorial; accepted as written |
| [10 items_found](#case-10) | Sets how many selected Items must exist. | editorial; accepted as written |
| [11 items_satisfying](#case-11) | Sets how many selected Items must satisfy the comparison. | editorial; accepted as written |
| [12 field_requirement](#case-12) | Sets the shared value-count requirements for fields in this comparison. | editorial; accepted as written |
| [13 values_found](#case-13) | Sets how many observed values must be present for a field. | editorial; accepted with revision |
| [14 values_matching](#case-14) | Sets how many values must match the field's condition. | editorial; accepted as written |
| [15 concat](#case-15) | Joins values from two or more components into strings, producing one result for each combination. | **semantic decision needed**; draft style acceptable semantic hold |
| [16 regex_capture](#case-16) | Extracts the first capturing group's text from each input string. | **semantic decision needed**; draft style acceptable semantic hold |
| [17 unique](#case-17) | Removes duplicate scalar values from a collection. | **semantic decision needed**; draft style acceptable semantic hold |
| [18 merge](#case-18) | Joins a collection's values into a string with the chosen ordering and separator. | **semantic decision needed**; draft style acceptable semantic hold |
| [19 set_expression](#case-19) | Combines Object collections using union, intersection, or difference. | editorial; accepted as written |
| [20 state_filter](#case-20) | Includes or excludes collected Items that match a field condition. | editorial; accepted as written |
| [21 typed_value.value](#case-21) | The value represented using its declared datatype. | **semantic decision needed**; draft style acceptable semantic hold |
| [22 typed_value.status](#case-22) | Distinguishes an existing value from absence, an error, or a value that was not collected. | editorial; accepted as written |
| [23 Collected Item document](#case-23) | Records one collected entity, its fields, and supporting provenance. | editorial; accepted as written |
| [24 Object collection result](#case-24) | Records an Object's collection outcome and supporting Item references. | editorial; accepted as written |
| [25 Assessment document](#case-25) | Defines an Assessment's metadata and its manual procedure or automated checks. | editorial; accepted as written |
| [26 Benchmark document](#case-26) | Organizes Rules, Groups, Profiles, and shared policy settings. | **semantic decision needed**; draft style acceptable semantic hold |
| [27 Organizational Input Set](#case-27) | Supplies organizational values for Parameters delegated by a Benchmark publisher. | editorial; accepted as written |
| [28 foreach_binding](#case-28) | **Withheld — no supported-placement description proposed.** | **semantic decision needed**; withheld |

## Sources, initial drafts and engineering notes

Open a case for its exact pointer, existing local/inherited help, original Codex proposal and separate engineering note. Source verification is an editorial prerequisite, not approval to install a description.

<a id="case-01"></a>
<details>
<summary>01 — input_reference</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/input_reference`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** References a declared Input instead of embedding an inline literal value.

**Draft provenance:** Phase 1 `proposal-5bb2aae148be7ea5` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Uses the value of a declared Input.

**Separate `engineering_note`:** The marker is an object with the required input identifier. Existence, provision, value typing and resolution are separate checks; this sentence does not promise that a supplied identifier resolves.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/input_reference`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-02"></a>
<details>
<summary>02 — variable_reference</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/variable_reference`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** References a Variable by identifier instead of providing a literal; identifier resolution is checked separately from this schema.

**Draft provenance:** Phase 1 `proposal-a0b0201ea83b1bb6` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Uses the value of a declared Variable.

**Separate `engineering_note`:** The variable marker and identifier pattern are explicit. Identifier existence, cycles and derived types are semantic checks; the wording does not claim that string validation resolves a declaration.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/variable_reference`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-03"></a>
<details>
<summary>03 — object_reference</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/object_reference`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Identifier of a shared Object reused at a collection site; the schema validates its spelling, not reference resolution.

**Draft provenance:** Phase 1 `proposal-2f560ae906f38a90` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Reuses a named Object for collection.

**Separate `engineering_note`:** This reference is a string ending in -object, not an object_ref wrapper. Object existence, capability compatibility and collection reuse behavior are checked separately.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/object_reference`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-04"></a>
<details>
<summary>04 — evaluate</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/evaluate`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment.schema.json)

**Existing local wording:** Combines Test outcomes with OVAL-aligned Boolean operators.

**Wording before editorial revision:** Combines Test and Assessment results using Boolean operators and conditional expressions.

**Codex proposal:** Evaluates Test or Assessment references using the Boolean groups and conditional branches defined by the shared expression grammar.

**Draft provenance:** Phase 1 `proposal-d7cc4b7a798576c6` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Combines Test and Assessment outcomes using Boolean operators and conditional expressions.

**Separate `engineering_note`:** The accepted expression grammar includes and/or/one/xor/not and if/then/else with optional else_if. Input provision has a separate guard form. Do not advertise the inactive function-call vocabulary or for_each placement, and do not infer a new multi-state truth table.

**Classification:** editorial; **editorial status:** accepted_with_revision; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#/properties/assessment/properties/evaluate`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-05"></a>
<details>
<summary>05 — input_provided</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/input_presence/properties/input_provided`

**Source file:** [schema/expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/expression.schema.json)

**Existing local wording:** Declared local Input provision, not truthiness or nonemptiness. Only direct evaluate if/else_if guards; absent and provided empty remain distinct.

**Codex proposal:** Checks provision of a declared local Input, treating an absent value differently from a provided empty value.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Checks whether a declared Input was supplied, even if its value is empty.

**Separate `engineering_note`:** The native description distinguishes provision from truthiness/nonemptiness. The check belongs only in direct if/else_if guards; it is not a standalone evaluate expression or a guarantee that the supplied value is valid.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/expression.schema.json#/$defs/input_presence/properties/input_provided`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 3 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-06"></a>
<details>
<summary>06 — Variable expression</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/expression`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/variable-expression.schema.json)

**Existing local wording:** Expression that supplies this Variable’s values.

**Codex proposal:** Supplies the expression used to obtain the declared Variable values.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Defines how this Variable's values are obtained.

**Separate `engineering_note`:** The declaration selects a retained expression form. Constant declarations are restricted to literal expressions; local expressions have separate type/status obligations. No broader inactive function library is implied.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/declaration/properties/expression`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-07"></a>
<details>
<summary>07 — canonical_field_predicate</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_field_predicate`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** No local description.

**Wording before editorial revision:** Compares a collected field or checks whether it is absent.

**Codex proposal:** One field condition either compares observed values or asserts confirmed absence; local cardinality overrides must supply the complete pair required by the shared grammar.

**Draft provenance:** Phase 1 `proposal-f22db930634fb1d9` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Compares a collected field's values or checks for confirmed absence.

**Separate `engineering_note`:** Confirmed absence is comparator-free values_found: none; it forbids comparison properties. Keep complete local cardinality overrides in subordinate help, and do not equate collection errors/not_collected with confirmed absence.

**Classification:** editorial; **editorial status:** accepted_with_revision; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_field_predicate`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 3 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-08"></a>
<details>
<summary>08 — Comparison Require</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** One complete Test requirement: item_requirement gives explicit existence and satisfaction counts; conditions follow as fields/and/or/one/xor. Field cardinality must be explicit.

**Codex proposal:** Comparison requirement with independent Item counts, a complete shared field-count policy and one field condition or Boolean condition group.

**Draft provenance:** Phase 1 `proposal-60cccd72a7dca171` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Defines the Item counts and field conditions for a comparison Test.

**Separate `engineering_note`:** Item-presence-only requirements use a separate definition. The comparison form has independent Item policy, a complete shared field policy and a selected field/group condition; conditional occurrences remain in constraint help, not this sentence.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-09"></a>
<details>
<summary>09 — item_requirement</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** Explicit Item existence and satisfaction quantifiers; the two decisions remain independent.

**Codex proposal:** Sets the independent existence and satisfaction quantifiers for selected Items.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Sets how many Items must be found and how many must satisfy the comparison.

**Separate `engineering_note`:** items_found and items_satisfying are distinct required members in this comparison context. These are quantifier choices, not numeric literals or a count of serialized evidence rows.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-10"></a>
<details>
<summary>10 — items_found</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_found`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** Selected-Item existence requirement (OVAL Test check_existence). Both source all_exist and at_least_one_exists map to one_or_more; preserve their distinct source spellings only in provenance.

**Codex proposal:** Selected-Item existence requirement. Editors may suggest `one_or_more` for new authoring and must serialize an explicit value.

**Draft provenance:** Phase 1 `proposal-8a895f25bc073287` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Sets how many selected Items must exist.

**Separate `engineering_note`:** The accepted quantifier vocabulary is distinct from field-value requirements. Do not copy historical existence spellings into author help, infer runtime defaults, or substitute retained evidence-list length for selected population.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_found`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-11"></a>
<details>
<summary>11 — items_satisfying</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_satisfying`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** How many collected Items must satisfy the complete condition (OVAL Test check). Never conflated with items_found.

**Codex proposal:** How many collected Items must satisfy the complete condition. Editors may suggest `every` for new authoring and must serialize an explicit value.

**Draft provenance:** Phase 1 `proposal-ec829eb0a7c1af80` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Sets how many selected Items must satisfy the comparison.

**Separate `engineering_note`:** This quantifies Items meeting the complete condition, independently of Items found. Empty/unknown/error behavior is not redefined by the shorter description; the default annotation is an authoring concern.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement/properties/items_satisfying`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-12"></a>
<details>
<summary>12 — field_requirement</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** Required shared values_found/values_matching pair for comparison Tests. The editor may offer these defaults but must serialize the complete pair. A closer complete pair overrides it; no runtime default.

**Codex proposal:** Provides a complete field-count policy that nested conditions can override only as a complete pair.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Sets the shared value-count requirements for fields in this comparison.

**Separate `engineering_note`:** The values_found/values_matching pair is inherited together; a closer complete pair overrides it. Its authoring default annotation must not be presented as automatic runtime insertion.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-13"></a>
<details>
<summary>13 — values_found</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/paired_requirement/properties/values_found`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** No local description.

**Existing inherited wording:** State field/record existence cardinality. Preserve the OVAL entity/record all_exist distinction pending separate evidence review.

**Inherited source:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/existence_cardinality`

**Wording before editorial revision:** Sets how many values a field must have.

**Codex proposal:** Specifies the field-value existence cardinality under the enclosing policy.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Sets how many observed values must be present for a field.

**Separate `engineering_note`:** Read this leaf in its parent context: the shared paired requirement forbids none, even though the referenced existence-cardinality definition allows it elsewhere. Standalone confirmed absence belongs on an individual field predicate.

**Classification:** editorial; **editorial status:** accepted_with_revision; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/paired_requirement/properties/values_found`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-14"></a>
<details>
<summary>14 — values_matching</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/paired_requirement/properties/values_matching`

**Source file:** [schema/assessment-language.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment-language.schema.json)

**Existing local wording:** No local description.

**Existing inherited wording:** Consistent 0.4 authoring cardinality vocabulary. 'every' means all relevant results satisfy the specified comparison; source OVAL lexical values belong in provenance only.

**Inherited source:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/cardinality`

**Codex proposal:** Specifies the match cardinality for the observed values of one field.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Sets how many values must match the field's condition.

**Separate `engineering_note`:** Value matching and value existence are independent decisions but are inherited as one policy pair. This sentence adds no rule that an unavailable value matches, fails or becomes an empty string.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment-language.schema.json#/$defs/paired_requirement/properties/values_matching`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-15"></a>
<details>
<summary>15 — concat</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/variable-expression.schema.json)

**Existing local wording:** Concatenate two or more components in order. Multiple values produce the Cartesian product of component values. Components follow inherited source casting rules when a string conversion is required; incompatible values produce an error. A missing or nonexistent component yields the inherited source status; Error, Incomplete, Not Collected, and Not Applicable statuses are not silently converted to strings.

**Codex proposal:** Concatenate at least two ordered component expressions, taking the Cartesian product of multivalued components; native casting and unavailable-component status mappings require explicit confirmation.

**Draft provenance:** Phase 1 `proposal-815bd1572af318cf` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Joins values from two or more components into strings, producing one result for each combination.

**Separate `engineering_note`:** Existing native annotations state component order and Cartesian combinations. Casting, output representation and no-value/error-status mappings remain pending semantic review; examples demonstrate syntax only, not executed results.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/3/properties/concat`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 3 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-16"></a>
<details>
<summary>16 — regex_capture</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/variable-expression.schema.json)

**Existing local wording:** Capture text from each input string using the first capturing group. The source regex dialect and first-match behavior are retained; inputs with no capture group or no match produce an empty string under the inherited function contract.

**Codex proposal:** Extract the first capture from each input string; confirm the native regex dialect, no-match rule and status mapping before treating inherited behavior as normative.

**Draft provenance:** Phase 1 `proposal-17cfec5c72280003` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Extracts the first capturing group's text from each input string.

**Separate `engineering_note`:** The current native annotation specifies the first group but delegates regex dialect, no-match/no-group behavior and statuses to inherited rules. The pattern member is only a string constraint; validating it does not prove capture semantics.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/4/properties/regex_capture`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 3 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-17"></a>
<details>
<summary>17 — unique</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/unique`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/variable-expression.schema.json)

**Existing local wording:** Remove duplicate scalar values from one expression or from multiple ordered component populations. Multiple components are flattened in source order before first-occurrence deduplication; duplicates and diagnostic statuses are preserved. Record data is not a supported transformation operand.

**Codex proposal:** Remove duplicate scalar values from the input; equality, ordering and unavailable-value propagation require an explicit native contract.

**Draft provenance:** Phase 1 `proposal-fae2ce17d5dede78` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Removes duplicate scalar values from a collection.

**Separate `engineering_note`:** The native description excludes record operands, although the expression reference does not by itself close every operand type. Equality, ordering and unavailable-value propagation remain pending; no deduplication runtime is executed.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/5/properties/unique`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-18"></a>
<details>
<summary>18 — merge</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge`

**Source file:** [schema/variable-expression.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/variable-expression.schema.json)

**Existing local wording:** Combine one or more ordered input populations into one string using an explicit delimiter, sort mode, and order. document preserves flattened input order; other modes sort before joining. Duplicates are preserved unless a separate unique expression removes them.

**Codex proposal:** Sorts or preserves input order and joins the values with the explicit delimiter.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Joins a collection's values into a string with the chosen ordering and separator.

**Separate `engineering_note`:** delimiter, sort, order and values are explicit required inputs; duplicates are not implicitly removed. Sorting edge cases, casting and unavailable/error behavior need semantic confirmation before unqualified publication.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/variable-expression.schema.json#/$defs/expression/oneOf/12/properties/merge`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-19"></a>
<details>
<summary>19 — set_expression</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/set_expression`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** Set composition compatible with OVAL 5.12.3 set semantics. A single operand is valid for union, intersection, or difference and evaluates to that operand after its filters are applied; difference is limited to at most two operands.

**Codex proposal:** Composes Object collections with the chosen set operator and explicit operands.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Combines Object collections using union, intersection, or difference.

**Separate `engineering_note`:** The native operator choices and operand shapes are explicit: one operand is permitted and difference has at most two. This sentence does not establish new Item identity, duplicate, filter-error or ordering rules.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/set_expression`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-20"></a>
<details>
<summary>20 — state_filter</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/state_filter`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** One field-key predicate with an explicit include/exclude Set filter action.

**Codex proposal:** Applies a field predicate with an explicit include or exclude action to collected Items.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Includes or excludes collected Items that match a field condition.

**Separate `engineering_note`:** This is a collection-stage include/exclude action, not the compliance decision itself. The exclude choice is an editor authoring suggestion, not a runtime default; unknown/error predicate outcomes are not newly defined here.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/state_filter`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-21"></a>
<details>
<summary>21 — typed_value.value</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/value`

**Source file:** [schema/result-types.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/result-types.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Payload whose representation is constrained for records; this generic schema does not fully constrain non-record datatype/value consistency.

**Draft provenance:** Phase 1 `proposal-eabe639e340a4f69` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** The value represented using its declared datatype.

**Separate `engineering_note`:** This describes intended representation, not a validation guarantee: generic 0.4 does not fully enforce non-record tag/payload consistency. Status/redaction can prohibit the payload, and record rules can require it; the intent/enforcement distinction needs semantic review.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/value`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-22"></a>
<details>
<summary>22 — typed_value.status</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/status`

**Source file:** [schema/result-types.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/result-types.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** Choose one of `exists`, `does_not_exist`, `error`, `not_collected`.

**Draft provenance:** Phase 1 `proposal-08007277fc053ddd` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Distinguishes an existing value from absence, an error, or a value that was not collected.

**Separate `engineering_note`:** The four labels are exists, does_not_exist, error and not_collected. These are value statuses, not Boolean comparison results; propagation into Test outcomes remains a separate contract.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/result-types.schema.json#/$defs/typed_value/properties/status`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-23"></a>
<details>
<summary>23 — Collected Item document</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/collected-item.schema.json#`

**Source file:** [schema/collected-item.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/collected-item.schema.json)

**Existing local wording:** Reusable runtime Item shape. Missing Items are absent from the collection, not represented as synthetic does_not_exist Items. Collection-level absence and field-level statuses remain separate.

**Codex proposal:** Records the fields and provenance of one entity acquired by a collector.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Records one collected entity, its fields, and supporting provenance.

**Separate `engineering_note`:** The record requires id, capability, status, fields and provenance. Missing Items are omitted rather than emitted as synthetic does_not_exist Items; open provenance shape does not guarantee complete evidence.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/collected-item.schema.json#`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-24"></a>
<details>
<summary>24 — Object collection result</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#`

**Source file:** [schema/collection-result.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/collection-result.schema.json)

**Existing local wording:** Runtime result of evaluating an authored Object and producing Items. Collection status is intentionally not Boolean.

**Codex proposal:** Records an Object collection outcome and the identities of retained or referenced Items.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Records an Object's collection outcome and supporting Item references.

**Separate `engineering_note`:** Collection status is not Boolean. item_refs can represent retained/materially referenced evidence rather than every collected Item; logical/population completeness and error reporting remain separate fields.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/collection-result.schema.json#`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 1 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-25"></a>
<details>
<summary>25 — Assessment document</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#`

**Source file:** [schema/assessment.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/assessment.schema.json)

**Existing local wording:** Pre-alpha 0.4 Assessment single authoring grammar. Source conversion must emit this native grammar.

**Codex proposal:** Defines the metadata and mode-specific content of a manual or automated Assessment.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Defines an Assessment's metadata and its manual procedure or automated checks.

**Separate `engineering_note`:** The mode branches distinguish a manual procedure from automated tests/evaluate and require different fields. This sentence introduces no new execution mode, branch syntax or default policy.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/assessment.schema.json#`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 1 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-26"></a>
<details>
<summary>26 — Benchmark document</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/benchmark.schema.json#`

**Source file:** [schema/benchmark.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/benchmark.schema.json)

**Existing local wording:** No local description.

**Codex proposal:** When this object is present, `benchmark` must be supplied. Its semantic purpose requires owner review.

**Draft provenance:** Phase 1 `proposal-5a7a7b5d15ce5e9c` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Organizes Rules, Groups, Profiles, and shared policy settings.

**Separate `engineering_note`:** These named sections are required, but their internal policy objects are partly opaque. Confirm the organizing relationship before installing this sentence as normative; it does not define profile inheritance, selection precedence or scoring behavior. Only section-shape witnesses are supplied, not a complete Benchmark example.

**Classification:** semantic_decision_needed; **editorial status:** draft_style_acceptable_semantic_hold; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/benchmark.schema.json#`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 2 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-27"></a>
<details>
<summary>27 — Organizational Input Set</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/organizational-input.schema.json#`

**Source file:** [schema/organizational-input.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/organizational-input.schema.json)

**Existing local wording:** External organization-supplied policy data for Parameters intentionally left unresolved by a Benchmark publisher.

**Codex proposal:** Supplies organization-defined policy values for Parameters intentionally delegated by a Benchmark publisher.

**Draft provenance:** New bounded Codex draft from the pinned native sources; no earlier gap proposal is attributed to it.

**Edited `author_description`:** Supplies organizational values for Parameters delegated by a Benchmark publisher.

**Separate `engineering_note`:** The existing root description limits this data to Parameters intentionally left unresolved by the publisher. Benchmark constraints remain authoritative; this wording does not permit overriding publisher-defined values or claim that this generic value map enforces all types/cardinalities.

**Classification:** editorial; **editorial status:** accepted_as_written; **semantic status:** no_new_semantics_claimed.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/organizational-input.schema.json#`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 1 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

<a id="case-28"></a>
<details>
<summary>28 — foreach_binding</summary>

**Exact schema pointer:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/foreach_binding`

**Source file:** [schema/capability-common.schema.json](https://github.com/vanderpol/scap-ng/blob/63110e7762f4963d3e4d407e90b9fcfd9cfe86ad/schema/capability-common.schema.json)

**Existing local wording:** Native 0.4 collection-expansion foreach binding. The source is one named shared/referenceable Object. Chaining is permitted: a source Object may itself use for_each, creating correlated lexical lineage. Independent multi-source Cartesian expansion is not implicit.

**Codex proposal:** Shared Item-lineage binding with explicit item and in properties; an authored placement is not reachable from the frozen Assessment schema.

**Draft provenance:** Phase 1 `proposal-9ec72a60ca2efd9d` at `823ac12fbd0b5eaa7096ef4c6855ee25ff4f49a2`

**Edited `author_description`:** Withheld.

**Separate `engineering_note`:** No author-facing description is approved or offered. Neither foreach helper is reachable from accepted Assessment authoring; resolve placement/activation with Jack before advertising support or providing an authored for_each example.

**Classification:** semantic_decision_needed; **editorial status:** withheld; **semantic status:** pending_semantic_review.

**Proposed description authority:** `https://scap-ng.dev/schema/v0.4.0/capability-common.schema.json#/$defs/foreach_binding`; related consumers: none separately bound in this worksheet.

**Source/syntax checks:** 0 witnesses; exact instances, target/parent pointers and expected validity are in the machine sheet.

</details>

## Review gate

Approve style separately from behavior. A semantic-decision row remains pending even if its sentence reads well. The batch 1 foreach case remains withheld until placement is decided. The bulk patch and frozen schemas remain unchanged. Eight approved descriptions are demonstrated only in the [isolated next-version proposal](../../pilots/approved-annotations/RECEIPT.md); no production editor installation is authorized.

**Stop for editorial review.** No bulk shortening of the 1,580 findings, schema edit, editor repin, migration or merge.
