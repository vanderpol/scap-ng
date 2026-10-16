# Joval technical review — October 16, 2026

**Goal:** get implementation-level criticism of the **0.4 pre-alpha Assessment authoring proposal**; **not** a request for approval, certification or a new Board vote. Budget: **20 minutes**. Start here; use the longer [technical notes](JOVAL-TECHNICAL-PREVIEW.md) only if needed.

## Open these two downloads

1. [Ten real OVAL-single → NG side-by-side comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015). Start with its `SHOWCASE-START-HERE.md`; the paired XML and native YAML/JSON are source-backed. An additional `for_each` example and the `if/else` illustration are *clearly marked optional research*, **not automatically emitted lossless rewrites**.
2. [Corrected six-STIG r3 complete YAML + JSON authoring preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3). Do **not** use r2: r3 restores 12 shared manual Assessments. All 2,958 Rule choice links resolve.

## Show, then ask

| Time | Real example | Specific question for Joval |
| --- | --- | --- |
| 0–3 min | One-grammar motivation | Are acquisition, collected-item cardinality, scalar field requirements and record-member requirements clearly separated? |
| 3–8 min | Windows 11 **SV-253254**, two permitted registry State alternatives; **SV-253274**, absent `stderr_line` exception | Does `collected_items_require` versus `state_fields_require` and leaf `require` preserve the *correct population* at each level, including missing/error/unknown fields? |
| 8–12 min | Windows 11 **SV-253495**, five user-right checks and two nested WMI-record checks | What real-world same-record / record-member / quantifier counterexample could break the proposed scoping? No implicit inheritance from scalar fields into records. |
| 12–16 min | RHEL 9 **SV-257889** ObjectComponent/`for_each`; Windows Server 2025 **SV-278001** branch-shaped source graph | What extra conditions justify a *lossless* `for_each` rewrite? Should source `OR(AND(G,P),AND(NOT G,Q))` remain explicit? Procedural `if` differs in **81/216** generic six-state inputs. |
| 16–20 min | Reference boundary findings | Request 1–3 source-backed counterexamples: incomplete Item collection, `only_one_exists`, error/unknown/NA, non-Boolean Filters, and source evidence/collection side effects. Record exact case, expected result and follow-up owner. |

## Assertions we can defend

- Six source-backed Benchmark conversions and downstream validation/**0.3 compilation** passed: [CI 38829943744](https://github.com/vanderpol/scap-ng/actions/runs/38829943744). Stale XCCDF selector and old comparison-test assertions were corrected without relaxing source identity or operations ([#226](https://github.com/vanderpol/scap-ng/issues/226), [closed #231](https://github.com/vanderpol/scap-ng/issues/231)).
- The r3 **0.4 authoring proposal** passed independent JSON-only schema and static references: **4,001 documents**, **872 unique automated Assessments**, **1,375 unique Test nodes**, **2,958 choice references**, **zero unresolved** ([CI 38830995691](https://github.com/vanderpol/scap-ng/actions/runs/38830995691)). **1,396 Assessments / 2,144 Tests** are repeated *per-Benchmark conversion occurrences*, not distinct archive files.
- Source reconstruction is not scanner execution. The six-state reference tests include [53 expected-result boundary fixtures + 1,036 bounded partial-result combinations](https://github.com/vanderpol/scap-ng/actions/runs/38829943793). An incorrect premature verdict on incomplete Item populations was detected and fixed; [technical explanation](INCOMPLETE-ITEM-SEMANTICS-REVIEW.md).
- The proposed scope inheritance, English cardinality labels and `and/or` aliases are **not ratified into the base 0.4 schema**. This meeting is to criticize the *candidate*, not silently promote it.
- **Not yet proven:** an independent JSON-to-signed-`.scapng` build ([#232](https://github.com/vanderpol/scap-ng/issues/232)); six-state scanner interoperability ([#229](https://github.com/vanderpol/scap-ng/issues/229)); unrestricted conversion of `if/else`, Variables, Sets and `for_each`.

## Capture decisions before leaving

Record each counterexample as: **STIG/SV-ID or OVAL node → source expression and observed Item population → expected six-state result → NG candidate expression → discrepancy → relevant test fixture/issue**. Track opinions on (1) scope vocabulary, (2) exact-one and negative/optional cardinality names, (3) procedural branch versus source-faithful Boolean expressions, and (4) evidence/skip requirements. A meeting comment is *feedback*, not Board approval or normative adoption.

**Maintainers:** put semantic counterexamples in [#229](https://github.com/vanderpol/scap-ng/issues/229), grammar decisions in [#227](https://github.com/vanderpol/scap-ng/issues/227), capability/schema gaps in [#228](https://github.com/vanderpol/scap-ng/issues/228), and independent build needs in [#232](https://github.com/vanderpol/scap-ng/issues/232). Preserve the immutable r3 prerelease and current 0.3 standards.
