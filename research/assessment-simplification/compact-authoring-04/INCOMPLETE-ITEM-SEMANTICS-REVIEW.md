# Incomplete Item streams: 0.4 reference semantics review

**2026-10-15/16 · Pre-alpha research proof, not a new normative language decision.** [Conformance issue #229](https://github.com/vanderpol/scap-ng/issues/229). Source authority for generic result charts: pinned **OVAL 5.12.3 `oval-results-schema.xsd`** and the independent count-chart tests in [`tools/test_oval_result_truth_tables_exhaustive.py`](../../../tools/test_oval_result_truth_tables_exhaustive.py). This is *not* an operating scanner or proof of all 0.4 collection-capability behavior.

## The bug the added tests caught

An earlier generic helper, [`evaluate_collected_object_test`](../../../tools/oval_result_truth_tables.py), would aggregate only the **currently observed Items** and treat any aggregate `false` as final for an incomplete collection. That was incorrect for `check: at least one` and `check: only one` when no observed Item matched: a later Item might pass. Conversely, the generic helper could mark `check: at least one` **true** even when the Test required `only_one_exists`: a later Item could invalidate that existence requirement.

The corrected code checks whether the verdict is **irreversible under additional Items**, accounting for the *existence requirement and match aggregation together*. It makes no guess about how many more Items are coming.

| Incomplete observed population | Existence requirement | Matching aggregation | Safe current verdict | Why |
| --- | --- | --- | --- | --- |
| One Item; comparison `false` | `at_least_one_exists` | `at least one` | `unknown` | A future passing Item could make the check true |
| One Item; comparison `true` | `at_least_one_exists` | `at least one` | `true` | A passing witness exists and a future Item cannot remove it |
| One Item; comparison `false` | `only_one_exists` | `only one` | `false` | No additional Item leaves a failed check; any additional Item violates exact-one existence |
| One Item; comparison `true` | `only_one_exists` | `at least one` | `unknown` | A future second Item invalidates the existence condition |
| One Item; comparison `true` | `all_exist` | `at least one` | `unknown` | An unseen missing Item can invalidate `all_exist` |
| Two observed Items | `only_one_exists` | any valid check | `false` | Existence already fails |
| One observed Item | `none_exist` | no State | `false` | Absence requirement already fails |
| One Item; comparison `true` | `any_exist` | `at least one` | `true` | Both satisfied requirements are monotone after a present witness |

**Deliberately conservative:** A non-decisive incomplete population remains `unknown`, including mixed `error`/`unknown` evidence that later collection may affect. Implementers must not infer a complete collected Object from a syntactically valid Assessment or interpret `unknown` as `false`.

## Executable evidence

- [CI six-state/reference gate](https://github.com/vanderpol/scap-ng/actions/runs/38829943742) passed the independent pinned truth tables, conditional boundary fixtures and existing *exact-one/one-match* parity proof.
- [CI boundary fixtures](https://github.com/vanderpol/scap-ng/actions/runs/38829943793) passed **53 independent expected-result examples** plus a bounded exhaustive test of **1,036** partial-result / matching-mode combinations (all, at least one, only one, none satisfy; 0..3 observed Items; all six result statuses).
- [`tests/v04-semantic-boundaries/cases.json`](../../../tests/v04-semantic-boundaries/cases.json) contains the human-readable expectations; [test driver](../../../tools/test_v04_semantic_boundary_cases.py) and [pinned evaluator tests](../../../tools/test_oval_result_truth_tables.py) execute them.

## Review boundaries

- Exact OVAL schema/result-table compatibility must remain independently reviewable. These tests are **reference-model** tests; they do not establish native 0.4 scanner conformance or source-to-runtime evidence completeness.
- Nested Windows records, `for_each`, ObjectComponent error, Set filters and Variables have independent scope-specific fixtures; the corrected incomplete-stream helper does **not** automatically prove complex source graphs or arbitrary conditional normalization.
- Before normative 0.4 promotion, confirm that the adopted Test-level `require` vocabulary maps to the same existence/match pairs, define complete/incomplete Item status and provenance, and implement an independent conformance evaluator. Those remain [open decision gates](0.4-SCOPE-AND-RELEASE-GATES.md).

**Review request:** Can a vendor produce any counterexample from OVAL 5.12.3 where the table above would differ, especially mixed missing/error Items and `only_one_exists` with incomplete collection? Preserve the raw source/evidence status in a failing fixture rather than weakening the decision predicate.
