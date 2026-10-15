# RHEL 9 — shorthand completeness is a vocabulary question

**Research-only sensitivity test**, not an adopted grammar, not a revision to the existing [downloadable three-preset preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-rhel9-compact-authoring-research).

[Passing CI, exact original 0.3 reconstruction](https://github.com/vanderpol/scap-ng/actions/runs/38730579495) · [Reproducible comparison script](https://github.com/vanderpol/scap-ng/blob/main/tools/research_04_rhel9_residual_pair_sensitivity.py) · [RHEL9 initial preview](RHEL9-PREVIEW.md).

The published 445-Rule RHEL9 source has **417 automated-by-default Rules**. In the first preview, **139/417** lacked longhand in *both* the Test/State quantifier pairs *and* the eligible comparison operators. That **does not** mean the other 278 Rules cannot benefit from shorter authoring syntax. It means a single non-whitelisted longhand expression disqualifies a Rule from that unusually strict statistic.

## Exact RHEL9 experiment

The existing three researched presets are `at_least_one_all_match` (Test or State), `at_least_one_some_match` (Test or State), and the strictly State-free Test absence `none_exist`.

Add **just two** more exact pair expansions for sensitivity comparison:

```yaml
require: all_exist_all_match    # existence: all, match: all
require: optional_all_match     # existence: optional, match: all
```

The pair names are *candidate labels*, not standard syntax. Both preserve source pairs exactly; missing Item/field semantics must be taught separately. No hidden default is inferred and no runtime technical meaning is changed.

| RHEL 9 research measurement | Initial 3 presets | With 5 |
| --- | ---: | ---: |
| Automated-by-default Rules | 417 | 417 |
| Rules with all Test/State pairs shortened | **269** | **398 (95.4%)** |
| Rules still containing explicit Test/State pair(s) | 148 | **19** |
| Rules with neither longhand pair nor non-aliased comparison | **139** | **197 (47.2%)** |
| Above, also using direct single-Test evaluation | 113 | 158 |
| Explicit Test pair *occurrences* remaining | 219 | **10** |
| Explicit State-field pair *occurrences* remaining | 12 | **12** |
| Total explicit Test/State pair occurrences remaining | 231 / 1,232 | **22 / 1,232 (1.8%)** |

The **209 eliminated pair occurrences** were 168 Tests with `all/all` and 41 with `optional/all`. The Rule totals are not additive: each Rule may contain multiple pairs and comparisons. The test rechecked exact parsed original 0.3 Assessment equality for both vocabularies, resolving shared Assessments through the complete 445-Rule Benchmark.

## Extra sensitivity: include field-level `none_exist`

[Passed CI (source-reversible on all RHEL9 referenced automated Assessments)](https://github.com/vanderpol/scap-ng/actions/runs/38731017268). This is a **sixth usage form** of an existing alias, **not a sixth name**. The original three-preset RHEL9 downloadable ZIP was not changed.

```yaml
# State-field scope: no collected entities of this field may exist
states:
  - stdout_line:
      value: forbidden
      operation: equals
      require: none_exist
```

This compiles **exactly** into a State with `field: stdout_line`, `existence: none`, `match: all`, and the unchanged `value` and `operation`. It does **not** mean "no stdout_line entity matches forbidden"; that is a *different* proposition. At **Test** scope, `none_exist` is still only allowed when there are no States, and means **no collected Items**.

| RHEL9 structured research measure | Initial 3 names | Plus `all/all` and `optional/all` | Also apply `none_exist` at field level |
| --- | ---: | ---: | ---: |
| Automated-by-default Rules | 417 | 417 | 417 |
| Rules with all Test/State pairs abbreviated | 269 | 398 | **407 (97.6%)** |
| Rules still needing at least one explicit pair | 148 | 19 | **10** |
| No explicit quantifier pair **or** non-aliased comparison | 139 | 197 | **205** |
| Remaining explicit Test pair occurrences | 219 | 10 | **10** |
| Remaining explicit field pair occurrences | 12 | 12 | **1** |
| **Total explicit pair occurrences** | 231 | 22 | **11 / 1,232 (0.9%)** |

The new field scope covered **11** individual `none/all` predicates found in **eight unique source Assessment files**; multiple Rules may reference the same shared Assessment. Before publishing results, both stages and the new scope were re-expanded into **exactly identical parsed 0.3** for every Assessment.

**Remaining source pairs:** Five Test `one/all`, three Test `optional/none`, one Test `all/none`, one Test `none/all` that retains States, and one field `one_or_more/none`. The latter five `match: none` occurrences signify **negative matching** and must not be folded into the absence alias. The `none/all` Test with States fails the no-State guard. No broader semantic equivalence has been claimed.

**Design implication:** This establishes excellent *cardinality coverage*, not proof that the resulting syntax is easier for a novice to learn or that full Assessments are concise. Five names, two different contextual meanings of `none_exist`, and several meaningfully distinct `none` cases must remain **discoverable, schema-validated and explicitly documented**. The proposal remains research only; neither 0.3 nor the Board vocabulary decision has changed.

## What the comparison means

The current preset whitelist undercounts shorthand's **coverage** and overstates its apparent difficulty. A handful of semantics-preserving pair presets cover nearly every native quantifier occurrence. On the other hand, **a 5-item preset glossary remains a second set of terms authors must memorize**, and the longhand pairs (`optional/all` and `all/all`) may be just as clear as the labels. The decision is about human comprehension, autocomplete, authoring schema discoverability and avoiding optional-syntax Easter eggs—not squeezing the last 1.8% of quantifiers.

The remaining 220 automated Rules that do not meet the dual *no-longhand-pair-and-comparison* test often have explicit typed comparison operations, dynamic Values/Variables, literal arrays or other complex expressions. They **still** use field-key syntax and any eligible shorthand, and remain automated Rules.

**Recommendation:** Treat field-name-as-key as the more promising primary 0.4 grammar improvement. Choose the small, versioned `require` preset list only if a schema-backed editor and actual readability review show it is clearer than writing `existence` and `match`. Keep original 0.3 as the canonical lowering output and do not introduce hidden defaults.
