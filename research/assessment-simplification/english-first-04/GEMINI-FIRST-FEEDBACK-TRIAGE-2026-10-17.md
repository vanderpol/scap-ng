# First Gemini feedback — issue triage, counterexamples, next review

**17 October 2026. Research #235 / six-state gate #229.** This file records the *high-level feedback the project owner pasted from Gemini*, not a completed independent source-semantic validation. It is not an adoption decision or a statement that an actual auditor has passed the comprehension test. The original answer-free [Gemini packet](GEMINI-INDEPENDENT-REVIEW-PACKET.md) requested A1–G individual predictions, confidence, original authoring, and a source-file cross-check; **none of those answers or comparisons was present in the response supplied**. The first-pass critique is still useful for deciding what to test.

**Naming:** "v2" is the revision label of this *research packet*; it does not mean released SCAP-NG v2 or approved v0.4 syntax. The source-tested [canonical comparison examples](canonical-operators/report.md) remain the baseline.

## Evaluation of the four principal criticisms

| Feedback | Finding against actual SCAP-NG contracts | Action |
| --- | --- | --- |
| A. Collection selection and compliance assertions are mixed | **Overstated as a schema defect.** The example has separate sibling `where` and `require`: `where` selects partitions; `require.items` determines what zero selected Items means. A complete, successful zero-Item acquisition with `items: at_least_one` is a failed existence requirement, **not** an implicit pass or not-applicable. Incomplete/error acquisition is a separate semantic stage. A source Set/filter has distinct before/after semantics, so a generic `target` wrapper cannot blindly fuse them. | **Retain the current single-check grammar for now.** Test a `select`/`assert` split side-by-side in **complete** Windows/Linux cases if independent reviewers demonstrably misread the present separation. Do not add wrappers solely to look organized. |
| B. `and`/`or` give no six-state propagation definition | **Correct concern for novice comprehension, incorrect claim about existing specification.** [Assessment Method](../../../specification/assessment/assessment-method.md) already requires inherited OVAL 5.12.3 result tables for `true`, `false`, `error`, `unknown`, `not_evaluated`, `not_applicable`. The source-model allows a decisive OR true to win over an error child, according to the authoritative truth table. This is *not* ordinary Boolean short-circuit or a new per-check switch. Runtime/evidence parity and some zero-cardinality cases remain open. | **Keep ordinary `and`/`or` as the author language** and give editor/auditor previews a source-derived six-state explanation. Add explicit mixed-error fixtures; do not infer every OR with an error returns error. |
| C. `all_state_fields_exist: true` floats outside `require` | **Confirmed real readability/design debt.** The complete DNS example has it outside `require`, while Apache uses a field-level optional matcher and Linux uses group field presence. A check excerpt omitting the inherited rule is actively misleading. | **Highest-priority grammar revision target.** Define one effective, typed field-presence policy and explicit precedence for individual field, State group, Test (plus record isolation). Then prove exact lowering; consider local `presence` at the smallest meaningful scope. `exists: true` alone is not a proven OVAL cardinality/error contract. Never silently move/delete old flags. |
| D. Root Item vs nested record matching | **Legitimate comprehension risk, not license to flatten.** `matching_items` and `matching_records` are exploratory scope-specific names; `states.or` still combines *whole State predicates*. For one WMI root Item with records [1,3], neither "all records 1" nor "all records 3" branch is satisfied on complete data; this differs from "every record is in [1,3]". | Retain separate Item/State/record populations and the OR tree; show the entire predicate in editor/proof sheet and insist the outside reviewer predicts the mixed case. Do not invent an `in` shortcut. |

## The requested `select` / `assert` proposal — two testable layouts

**Present research shape — selection and requirement already separated, minimum nesting:**

~~~yaml
inspect: linux.partition
where:
  mount_point: {matches_regex: '.*\/home'}
require:
  items: at_least_one
  matching_items: all
  mount_options: {at_least_one_value_equals: nosuid}
~~~

**Gemini-style structural regrouping — speculative only, no AST or migration proof:**

~~~yaml
select:
  inspect: linux.partition
  where:
    mount_point: {matches_regex: '.*\/home'}
assert:
  items: at_least_one
  matching_items: all
  mount_options: {at_least_one_value_equals: nosuid}
~~~

The regrouping adds **two wrappers** and one indentation level without changing what this source-backed Test does. Its value is **not proven**; maybe a beginner immediately recognizes "select" vs "assert", or maybe the larger nesting makes full Windows Set/foreach content worse. No full-corpus source-equivalent compiler lowering exists for it. If tested, compare comprehension and successful new-check authoring on **full** samples, not merely aesthetics on this easy snippet.

## What changes in the review loop

1. **Keep** `inspect/where/require` and `items/matching_items` as the minimum trial surface. Explicit `matching_records` stays a candidate, not a source-proved rename.
2. **Prioritize** the DNS, Apache and Linux field-presence effective contract (Test, State group, leaf field, records). Use the original source expressions and the six-state truth fixtures; don't invent a simple `exists` Boolean mapping.
3. **Maintain** the `and`/`or` truth contract in a **single reference location**, with a deterministic generated explanation per Assessment. The author should not need to write error aggregation manually.
4. **No new YAML revision just to satisfy feedback A.** Only change selection structure if a blind reviewer can identify a specific wrong outcome caused by its current placement.
5. **External independence remains incomplete:** Gemini did not provide blind A1–G classifications, confidence or Part 2 source comparison. Request **those exact missing outputs** before treating the feedback as an independent comprehension/semantics result.

## Next Gemini challenge, without revealing the answers

Send *only* the original [answer-free packet](GEMINI-INDEPENDENT-REVIEW-PACKET.md) in a fresh conversation or ask Gemini to continue **Part 1** of that packet **without showing this triage**. Insist on A1–G per-scenario outcomes, confidence, what cannot be inferred, and the Part 1B authoring examples **before** any Part 2 source file read. Then request the source-file comparison. A general list of architectural pros/cons is insufficient.

## Stop condition

**Not reached.** There is one confirmed presentational debt (field-presence placement), plus unresolved original six-state/evidence edge fixtures, possible record comprehension failures and missing independent scenario-level answers. The first Gemini critique is constructive but **does not prove** that the candidate fails or passes its semantic and novice-author gates. Repeat changes and the original traps until no new *material* problems appear in outside reviews and the source-backed fixtures close, not until reviews run out of cosmetic suggestions.

Sources: [iterated self-review](ITERATED-READABILITY-REVIEW-2026-10-17.md), [old independent blind packet](FRESH-EYES-BLIND-REVIEW-PACKET.md), [baseline full source-backed examples](canonical-operators/report.md), [Gate A/B/C](NEXT-READABILITY-DECISION-GATE.md), [separate 0.3 selection/filter contract](../../../specification/assessment/selection-and-filters.md).
