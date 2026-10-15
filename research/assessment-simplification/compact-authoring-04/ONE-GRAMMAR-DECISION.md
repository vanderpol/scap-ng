# 0.4 research: one canonical authoring grammar, not two YAML languages

**Research only. No 0.4 decision has been approved.** The project owner prefers one discoverable simplified YAML specification, with no hidden aliases. All current proofs lower exactly to the immutable 0.3 authoring source; scanner conformance for alternative test rewrites remains unproved.

## What the real RHEL 9 content says about "only one"

The [October 15 sensitivity run](https://github.com/vanderpol/scap-ng/actions/runs/38733739320) included **five** original RHEL 9 Test-level `existence: one, match: all` occurrences. Of these, **two have no States** and **three compare States**. A single label `exactly_one_all_match` would be jargon and misleading for the two State-free Tests.

Better, unambiguous human-language candidate names:

```yaml
# State-free Test: exactly one Item must exist
require: only_one_exists

# Test with an expectation: exactly one Item must exist
# and that Item must satisfy the State comparison(s)
require: only_one_exists_and_matches
```

These are **two context-dependent names for the same original pair** `existence: one`, `match: all`, with strict schema guards: `only_one_exists` requires no States; `only_one_exists_and_matches` requires one or more States. The proof rejects reverse use, and the original Test must be reconstructed byte-equivalently at the parsed mapping level. Avoid `exactly_one_matches`: it could mean exactly one of many collected Items matches instead of exactly one Item exists.

After these names, **411 / 417** RHEL 9 default-automated Rules have *all* Test/field quantifier pairs represented by the considered named syntax, versus 407/417 before the exact-one addition. Only **six source quantifier occurrences** remain explicit. The two labels covered all **five** original `one/all` pairs; no semantics were rewritten.

## Windows records are a true grammar design input, not an exception bucket

[Passing record-aware investigation](https://github.com/vanderpol/scap-ng/actions/runs/38733493967) resolved a misleading earlier count: record-valued State wrappers have **no standalone `existence` or `match` pair**. Their cardinality is inside `record:` and its named `fields:`. Treating those wrappers as missing shorthand incorrectly counted 36 Windows 11 and 59 Server 2025 record wrappers as failures.

| Five existing names + field-level absence; correct record recursion | RHEL 9 | Windows 11 | Server 2025 |
| --- | ---: | ---: | ---: |
| Rules with an automated choice | 417 | 245 | 259 |
| All Test, field and record quantifiers abbreviated | **407 (97.6%)** | **232 (94.7%)** | **238 (91.9%)** |
| Rules still having any original pair in longhand | 10 | 13 | 21 |
| Record-valued wrappers discovered | 0 | **36** | **59** |
| Original record subfield expectations counted | 0 | **38** | **60** |

This remains **source-identity proof**, not vendor runtime parity. With *seven more exact pair aliases*, all pair cases except semantic outliers are also mechanically representable: **416/417** RHEL 9, **243/245** Windows 11, and **257/259** Server 2025, with all included Assessments reconstructed exactly. **But adding seven more names is not yet recommended**. It shows the limitations are mainly shorthand vocabulary and record handling, not a need to abandon complex automated tests. Some residual source pairs still require first-principles review (e.g., `none` existence with States), and an expanded catalogue is harder for new authors to understand.

A single 0.4 grammar should allow native field-name predicates at every structural level, including `record.fields.productstate` (with exact nested types, bitwise operations, value_match, and explicit cardinality). A record's quantifier and each record field's quantifier are distinct, as are the parent Test and any Object value-array match cardinality.

## Before normatively choosing the syntax

1. **Make one schema normative.** Valid 0.4 Assessment source has field-name keys and a documented `require` contract; do *not* offer optional parallel `field:/existence:/match:` spellings in the same grammar as undocumented easter eggs. Provide one explicit 0.3/OVAL import/compiler path for legacy source migration.
2. **Give `require` readable and truthful names.** The natural exact-one labels are evidence that authors comprehend semantic phrases better than mechanical `all_match` combinations. Evaluate *negative* checks just as carefully: `none_exist` is not `none_match`.
3. **Avoid changing semantics to game coverage.** Replacing a Test with `match: none` by a negated State comparator is *not* assumed equivalent for empty collected sets, unavailable values, error/unknown/incomplete and complex AND/OR State composition. Differential proof across those outcomes is required before rewriting any STIG.
4. **Preserve valid complexity.** Keep original multi-Test evaluate trees, static Object selection arrays (`value_match` remains separate), Variables/Inputs, version operations, record subfields and manual alternatives. No opaque shell fallback may count as an improvement.
5. **Deliver one short specification + capability-specific JSON Schema.** Ensure VS Code/editor autocomplete lists every valid field and `require` choice, with enforced State versus State-free scope, clear examples and invalid fixtures.

**Recommendation:** The one-grammar approach is now strongly supported for authoring structure and all common quantifiers. Do not select the exact negative/rare-match vocabulary until semantic-differential proofs are complete. Keep 0.3 immutable.
