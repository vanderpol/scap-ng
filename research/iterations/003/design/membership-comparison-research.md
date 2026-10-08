# Membership comparisons (`in` / `not_in`) — research only

**Status:** exploratory; **not accepted 0.3 syntax or conversion behavior**. See [issue #195](https://github.com/vanderpol/scap-ng/issues/195). This document does not modify normative requirements, schema, converter, or examples.

## Why investigate

Authors find `value_match` / `variable_match` versus `match` difficult to distinguish. Common checks ask whether a collected scalar belongs to an approved set. Candidate:

```yaml
state:
  field: hostname
  operation: in
  value:
    input: required_time_sources
```

Intended reading: *each evaluated hostname is one of the approved hostnames*. This does **not** itself say how multiple collected Items, multiple observed entity instances, or multiple States are aggregated; existing independent Test/State scopes must remain explicit.

## Broader candidate use cases to survey

| Example | Candidate authoring intent | Complication to study |
| --- | --- | --- |
| Approved NTP/DNS servers | hostname `in` approved set | cardinality, repeated observed hostnames |
| SSH algorithms/ciphers | algorithm `in` policy allowlist | ordered lists versus allowed membership |
| Package names/versions | name `in` set | version ranges require comparison rather than membership |
| Windows group/right memberships | principal `in` allowed group | absence/exact-set/subset versus element membership |
| File permissions / allowed owners | UID `in` set | scalar equivalence and type coercion |
| Forbidden accounts/ports | value `not_in` denylist | missing collection and negatives |
| Enumerated configuration settings | setting `in` options | string normalization, case folding |

These are **hypotheses for corpus analysis**, not counted occurrences. Measure actual eligible Test/State comparisons across pinned NIWC 65-benchmark content; report rule IDs, original operation, value source, quantity of values, required quantifiers, and exclusion rationale.

## OVAL translation research (not automatic equivalence claims)

OVAL 5.12.3 comparison and aggregation are separate: State entity `operation` compares values; `var_check` combines comparisons against multiple Variable values; `entity_check` combines multiple observed entity instances; State/Test operators and `check` combine at higher levels. SCAP-NG additionally represents explicit `match`, `existence`, and the expected-value quantifier currently called `variable_match`.

| Candidate NG expression | OVAL-shaped analog to investigate | Safe mapping only when |
| --- | --- | --- |
| `observed in [a,b]` | State entity `operation="equals"` with Variable values `a,b`, `var_check="at least one"` | value is scalar, equality types match, expected set nonempty, and every relevant aggregation/result state preserves behavior |
| `observed not_in [a,b]` | Equal comparisons combined with `var_check="none satisfy"`, **not** automatically OVAL `operation="not equal"` with `var_check="at least one"` | negative behavior, missing data and six-state tables match |
| `allowed_set subset_of observed_set` | OVAL subset/set semantics where supported | never confuse containment of one element with subset of two sets |
| `observed in org_input` | OVAL external Variable binding plus appropriate State operation / `var_check` | input resolution/provenance happens first and no legacy semantics are lost |

The table is a conceptual crosswalk only. Establish exact OVAL enum spellings and truth-table outcomes from pinned OVAL 5.12.3 specifications/conformance material **before** declaring formal translation. In particular, OVAL `var_check` and NG quantifier spelling are not presumed identical.

## Non-negotiable semantic questions

1. Is membership legal only for scalar observed values, or also arrays/records? Avoid hidden flattening or Cartesian matching.
2. Define equality precisely: data type, case sensitivity, Unicode/normalization, path/version syntax, duplicate entries.
3. Define empty approved set, missing input, invalid/unapproved/expired input, and unknown/error/not-evaluated/not-applicable states.
4. Preserve separate source collection completeness, existence, entity-instance aggregation, per-State and per-Test logic. `not_in` must not become a misleading pass when collection failed.
5. Decide whether `in` is a first-class operation or explicitly expanded authoring sugar with a provable equivalence rule. Do not hide default quantifiers merely because syntax is shorter.
6. Avoid collision with existing `subset_of` / `superset_of` operations. Evaluate use in Object selectors separately from State predicates; collection targeting must not be accidentally broadened.
7. Where OVAL has `pattern match`, inequality, all/none/one quantifiers, or correlated multi-value comparisons, membership alone may not be lossless. Keep the richer form.

## Suggested investigation and evidence

- Create a **read-only census** of real examples from Linux, Windows, DNS, Apache and all pinned NIWC benchmarks, separated by scalar/literal-array/runtime-variable/organization-input sources.
- Produce at least five paired before/after examples with rule IDs and exact OVAL source, including at least two **not eligible** for membership conversion.
- Build an independent six-state truth-table comparison for equality + expected-value aggregation versus membership and its negation, including empty and incomplete populations.
- Quantify potential removal of quantifier noise and Variables independently of file-size and runtime claims.
- Write an explicit OVAL 5.12.3 → NG mapping and reverse explanatory crosswalk; any non-equivalence must be documented, not inferred away.

**Decision gate:** present findings and mapping to the project owner / OVAL Board before modifying normative schema, converter, compiler, or showcase examples. Keep #194's broad rename proposal separate pending this research.
