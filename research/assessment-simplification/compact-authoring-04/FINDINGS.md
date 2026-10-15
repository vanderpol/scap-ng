# Full 65-benchmark shorthand research — findings

**Research status: completed pinned-source census; no language change adopted.** This is evidence for [#225](https://github.com/vanderpol/scap-ng/issues/225), not a change to SCAP-NG 0.3 or [Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213).

## Two separately verified measurements

**A. Original source OVAL 5.12.3** — [completed source census and downloadable JSON](https://github.com/vanderpol/scap-ng/actions/runs/38718081754). All **65 pinned NIWC benchmark ZIPs** at revision `8c8e5dff860af6b1290ee9273a282db24278f8d5` were inspected. Counted distinct source Test and State identities per benchmark, with explicit versus documented-default attributes recorded. One Test reused by multiple Rules counts once within its benchmark.

**B. Modernized Assessment structural opportunities** — [completed pinned-converter census and JSON](https://github.com/vanderpol/scap-ng/actions/runs/38716331301). **61/65** packages converted, with the other **four** the known `independent.sqlext` blockers. All **7,165** automated Assessments (6,916 Rule and 249 applicability), containing **12,584** Test occurrences, passed exact parsed round-trip through the already-proven 0.3 modernization and research-only source macros. Converter pin `be317e37a3b2f7abad6ae0eebfccc8cfda33dc90` is deliberate; current-main converter regression is tracked in [#226](https://github.com/vanderpol/scap-ng/issues/226).

The historical structural baseline uses a transitional authoring vocabulary, so it **cannot** independently provide trustworthy current-0.3 quantifier names or direct State comparator counts. Original OVAL gives the quantifier evidence; 61-package Assessment analysis gives independent structural repetition evidence. Do not mix their denominators.

## Main result: genuinely structured OVAL only

macOS content is separately recorded (per publisher-authoring concern); opaque `independent.shellcommand` and unsupported `independent.sqlext` are also **excluded** from the primary ranking.

| Exact source pattern | Occurrences | Proportion in its scope |
| --- | ---: | ---: |
| Test existence one-or-more + match all | **6,054 / 10,061 Tests** | **60.2%** |
| State-field existence one-or-more + match all | **7,103 / 7,211 fields** | **98.5%** |
| State-free Test requiring no Items | **692 / 10,061 Tests** | **6.9%** |

OVAL explicitly/defaults attributes in two separate scopes; 3,147 of 10,061 structured Tests inherited source existence defaults, while 7,208 of 7,211 State-field occurrences inherited entity-existence defaults. The 0.3 compiled output must still **materialize** semantics explicitly. A named shorthand is an explicit author directive, not permission to hide OVAL defaults in the canonical schema.

Ten original IIS Tests used deprecated OVAL `check="none exist"`. The [existing scoped normalizer proof](https://github.com/vanderpol/scap-ng/blob/main/tools/test_0_3_zero_existence_lowering.py) and new source audit permit substituting the inert `match: all` **only when** Test existence is `none_exist` and no States are referenced; all ten met those guards. Four other structured absence-existence Tests retain State references and are **not** claimed eligible for the State-free macro. Two OVAL IDs appear with different payloads in separately scoped components of a Windows 10 package; both payloads are counted, not conflated.

## Independent 61-package structural authoring opportunity

These are *Test occurrences or explicit macro sites*, not additive lines saved:

| Pattern | Count |
| --- | ---: |
| Test duplicates the capability of its private inline Object | **9,214 / 10,792** non-macOS, non-shell Test occurrences |
| Tests with one local State | **5,846 / 10,792** |
| Single-Test Assessment with direct `evaluate` reference | **3,912** in the structured group |
| Simple scalar equality selectors | **5,073** eligible selector occurrences |

The source-macro research verified exact parsed expansion per generated Assessment; it does **not** establish a new 0.4 standardized YAML grammar or differential scanner conformance.

## Prioritized proposals for design review

1. **Named explicit Test/field quantifier pair:** `require: at_least_one_all_match`. Very frequent and can lower to the independent existing fields at the correct scope.
2. **Absence-only requirement:** `require: none_exist` for Tests without States; do not infer it for the remaining cases.
3. **Less ceremony for one-Test/one-State checks and duplicated private capability:** compiler-generated names/references must remain stable and explicit after expansion.
4. **Typed comparison shorthand:** `equals:` and `matches_regex:` for scalar-only values, preserving exact operations, datatypes and regex bytes.
5. **Source-only reusable discovery modules:** independent [15/15 Apache import proof](../variable-readability-04/BOARD-DESIGN-OPTIONS.md) removed 154 duplicate declarations from research authoring; it is a maintainability feature, not a new evaluator or promise of runtime reuse.

**Recommendation:** Compare these in the [short Board preview](BOARD-PREVIEW.md), then choose **editor/templates emitting canonical YAML** versus a **distinct versioned compact YAML authoring schema with autocomplete**. Do not mix undocumented aliases into canonical 0.3. A real readability assessment and combined lowering/conformance proof are still needed before normative 0.4 adoption.
