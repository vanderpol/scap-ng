# SCAP-NG 0.4 — exceptional OVAL semantics retention gate

**Research decision packet (not an approved language change) — 17 October 2026; Issues #235 and #229.**

## Proposed engineering policy

Support the smallest authoring vocabulary that expresses actual security intent. Do **not** expose an OVAL-specific keyword solely to improve a source-Dictionary roundtrip. A rare feature can be:

1. **Native core:** meaningful and regularly encountered, with a stable and discoverable meaning.
2. **Native advanced, same grammar:** rare but legitimate; expose only when an Assessment requires it, without a second legacy language or misleading defaults.
3. **Converter-only compatibility/lowering:** an inherited semantic distinction not worth everyday author-facing vocabulary; reproduce original source behavior through a proven lowering, explicit result/evidence policy or source-faithful compatibility adapter.
4. **Proposal for deprecation:** demonstrably unnecessary or contradictory, with source-backed analysis, exact replacement or an explicit migration error. **Never** silently rewrite to shell/manual or change scanner truth outcomes just to increase the coverage percentage.

Feature frequency is a **triage signal, not a drop rule**. In 1,375 Tests, one occurrence = 0.073% (larger than the owner's illustrative 0.01%). Proven six-state behavior and a single dangerous false-compliant result outweigh frequency.

## Evidence populations — do not mix denominators

- **2,140** original OVAL Test identities counted within the six pinned source-STIG archives: **1,818 DISA** and **322 NIWC/NAVWAR**, stratified by original `oval:mil.disa.stig...` versus `oval:navy.navwar...` Test ID.
- **1,375** distinct native Tests within **872** curated automated Assessments. Original package content can include Test definitions not selected into these native Assessments; shared native Assessments are not an additional STIG.
- The original [source-author census](reports/source-oval-author-edge-census.md) and [source candidate ledger](reports/source-oval-author-edge-census.json) distinguish them. The 201 native `all_exist` cases have **198 DISA and three NIWC single-Test-ID candidates**, matched on original Test comment and existence mode. This is **not a verified original-ID reference retained by the converter**.

## Candidate retention review

Counts refer to *native Tests* unless explicitly labeled original source or State-field observations. These are evaluations to review, **not specifications**.

| Feature/case | Observed use | Value to content authors | Proposed native disposition |
| --- | ---: | --- | --- |
| Ordinary at-least-one existence | 993 Tests | Common, predictable | **Core**; explicit `items` requirement rather than hidden default |
| Optional Item presence (`any_exist`) | 71 Tests; 116 DISA + 5 NIWC original source Tests | “If present, it must match”; absence isn't a policy violation in some checks | **Core** natural conditional requirement, retain six-state error behavior |
| None exist | 103 Tests | Prohibitions and disallowed resources | **Core**; presence vs `none of the existing Items match` must stay distinct |
| Test `all_exist` | 201 Tests; original source 356 DISA + 5 NIWC | Often redundant under complete collection of *real* existing Items; differs on partial/error | **Candidate to remove as normal author-facing choice**, NOT automatic source rewrite. Preserve incomplete and mixed-status behavior in importer/runtime |
| Exactly-one existence | 7 Tests; original source 8 DISA + 4 NIWC | Can detect duplicated lines, unexpected multiple query results or two banners | **Advanced, same grammar** until target-specific cardinality analysis proves redundancy |
| At least one exists and exactly one Item matches | 21 Tests | Security intent can require only one compliant record instead of all | **Advanced, same grammar**, not replaced by “some” or “all” |
| Exactly one exists and exactly one matches | 2 Tests | Two quantifiers can be redundant under fully observed single-Item population, but partial/status differences exist | **Normalization candidate after exact proof**; no new named shortcut in the core menu |
| Optional Items + at least one matches | 1 Test | Edge case where an empty set can pass despite a positive match rule | **Investigate** precise empty/error behavior and author intent; avoid special one-off keyword until justified |
| All exist + none match | 1 Test | Combines old Test existence with a negative Item State comparison | **Legacy-combination candidate**; preserve negatives and incomplete flags; do not conflate with `none_exist` |
| Optional Items + none match | 3 Tests | “If present, no Item may match this forbidden condition” | **Core negation concept**, but do not multiply paired alias names |
| Field absence/existence | 42 explicit `none_exist` State-field requirements of 915; 22 `at_least_one_exists_and_none_match` | Real missing field differs from no parent Item; nested scope matters | **Core scoped field capability**, not an OVAL Test existence keyword |
| Field exactly-one-match among values | 2 explicit requirements | Multi-valued entity data can require exact cardinality | **Advanced, same grammar** with unambiguous *field values* scope |
| Multiple State alternatives | 128 Tests | Genuine alternative acceptable configurations | **Retain**; avoid collapsing independent records into uncorrelated fields |
| Logical conditions | 219 Tests | AND/OR/NOT indispensable | **Retain**; use consistent meaning of nested scope |
| Nested records | 66 Tests | Typed structured WMI/cmdlet data | **Retain**, make records readable and prohibit misleading scalar shorthand |
| Expected value quantifier | 19 Tests | A Test value array or variable may require one, all or exactly one expected value | **Advanced, same grammar**; never silently replace OVAL `var_check` |
| `none_exist` with attached State | 1 source Test | Contradiction with OVAL Test contract | **Source/converter defect investigation**; not grounds to create a native language feature |

The 98% goal is a **review gate**: the earlier fixed-dropdown experiment reached 98.51% complete explicit requirement-mode coverage of unique Assessments with two narrowly scoped additions, 99.31% with three, but this is **not** proof the whole grammar can express or execute 98% of the Assessments. [Mode census](reports/fixed-requirements-six-stig.md).

## Real NIWC cases that resist blanket deprecation

- `oval:navy.navwar.niwcatlantic.scc.linux:tst:25777901` — expected single occurrence of command-line notice/banner in RHEL 9. Original `only_one_exists`. Is the “one” truly essential or an overly strict uniqueness assumption? Inspect original collector selector and policy text; don't change results without proof.
- `oval:navy.navwar.niwcatlantic.scc.windows:tst:25326601` — “Review Installed OS via PowerShell.” Original Test `only_one_exists`, `check="only one"`. Multiple records may indicate a query/cardinality problem, not an extra OS. Needs an explicit single-record contract if simplified.
- `oval:navy.navwar.niwcatlantic.scc.windows:tst:25329601` — “Review the Windows time service configuration via PowerShell,” likewise exact-one source behavior.
- `oval:navy.navwar.niwcatlantic.scc.rhel9os:tst:25824103` — optional collected crypto-policy configuration with a State (NIWC `any_exist`). “May be absent” must not silently imply that a present violation is allowed.
- `oval:navy.navwar.niwcatlantic.scc.windows:tst:25329301` — Bluetooth notification `all_exist`, illustrating a NIWC use of a legacy Test existence option. Modern authors can still use legacy vocabulary without proving it is necessary.

## Proof obligations before pruning

1. **Source provenance:** Join the original XCCDF Rule → OVAL Definition → Test/Object/State/Variable IDs, noting mixed DISA/NIWC closures. A source-comment match is not proof of identity.
2. **Audience readability:** Give security auditors the short English requirement and authored YAML independently; the expected interpretation must match on required values, Item cardinality, missing fields and nested records.
3. **Six outcomes:** Exhaustively or property-test `true/false/unknown/error/not_evaluated/not_applicable` for complete/incomplete/missing collections, errors, multiple Items, missing fields and duplicates.
4. **Lossless lowering:** If a removed keyword is replaced by a composition, prove compiler expansion against the original Test, Object, State, Variable and result evidence—not a syntactic roundtrip alone.
5. **Controlled removal:** If an OVAL semantic has no proven native equivalent, source conversion must report the exact blocker or use an explicitly reviewable compatibility mechanism. Never silently change policy or mark unsupported as compliant.
6. **Large-corpus follow-up:** Only at an intentional 65-benchmark release checkpoint, measure true near-0.01% prevalence and vendor distribution, rather than repeatedly running the heavyweight gate during design.

**Working recommendation:** Put optional, prohibited and “at least one and all match” into the simple authoring surface; keep exact cardinalities/negation/records in one clearly scoped advanced grammar. Move inherited `all_exist` toward converter-only handling **if** the native real-Item + result-status model survives these tests. Do not finalize these choices solely because the new YAML has fewer lines.
