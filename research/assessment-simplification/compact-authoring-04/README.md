# Compact SCAP-NG authoring research (0.4)

**Research only, not accepted syntax.** Canonical 0.3 and [Board Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213) are unchanged.

**Corpus work completed:** [Measured 65-source findings](FINDINGS.md) · [source OVAL proof](https://github.com/vanderpol/scap-ng/actions/runs/38718081754) · [61-converted-package structural proof](https://github.com/vanderpol/scap-ng/actions/runs/38716331301). This includes a separate macOS and shell-command accounting stratum and an exact compiler/source-layer distinction.

**NEW — full RHEL 9 authoring preview:** [RHEL9-PREVIEW.md](RHEL9-PREVIEW.md) · [download the research authoring ZIP](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-rhel9-compact-authoring-research). All **445** Rule files are included; **417 (93.7%)** default to automated, with manual tailoring alternatives for **all 445**. The experiment resolves shared Assessments by their Rule references, compacts **574/574** Field predicates and exactly re-expands **423/423** selected automated/applicability Assessment files. **269/417** automated Rules have all their `existence`/`match` pairs shortened by the three research presets; **148** retain other valid pairs explicitly. No new 0.4 grammar is approved.

**Current 0.4 recommendation for review:** [**One proposed human-readable authoring grammar**](ONE-GRAMMAR-BOARD-PREVIEW.md), with [full vocabulary, real RHEL/Windows examples and proof limitations](HUMAN-VERBIAGE-PROPOSAL.md). [Strict 3-benchmark verification](https://github.com/vanderpol/scap-ng/actions/runs/38737558392) covers **921/921 default-automated Rules**, preserving Object Set filters, nested Windows records, expected-value arrays and collector-only `selection_match`. **930/942** Assessment YAMLs lower to identical parsed 0.3 originals; **12** have State-free match normalization supported by the reference-result model but awaiting live differential testing. **Not approved syntax.**

## Question

Should common authoring shorthand use a separately versioned, discoverable compact YAML grammar, or should an editor/template system generate the existing explicit canonical YAML? Do **not** add undocumented mixed-in shortcuts or hidden defaults to the canonical format.

## Evidence and plan

The [six-STIG compiler prototype](https://github.com/vanderpol/scap-ng/actions/runs/38713548458) reversibly expanded 318/318 parsed automated Assessments. The [full modernization baseline](../full-corpus-modernization-19/README.md) accounted for 65 source packages, with 61 generated and four known SQL-extension blockers.

The [full-source shorthand research workflow](https://github.com/vanderpol/scap-ng/blob/main/.github/workflows/research-04-full-corpus-shorthand.yml) runs a new, scoped analysis at pinned NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`. **Converter baseline pinned:** `be317e37a3b2f7abad6ae0eebfccc8cfda33dc90`, the successfully verified October 7 full-0.3 census revision. A later converter audit regression blocking all 65 is tracked separately in [#226](https://github.com/vanderpol/scap-ng/issues/226); these measurements do **not** claim the current converter on `main` passes the full corpus. It reports existence/match pairs, absence-only checks, comparison operations, private capability repetition, one-State Tests and single-Test evaluate roots. Exact re-expansion of all candidate changes to parsed 0.3 YAML is required.

**Sampling rule:** Per the project owner's source-quality concern, macOS is counted separately and excluded from the primary structured-OVAL conclusions because its content largely wraps existing shell commands. Non-macOS shell-command capabilities are also counted separately. The primary scorecard covers structured OVAL-derived checks.

## Candidate shortlist

1. Explicit existence/match presets for frequent, proven pairs.
2. State-free absence-only `require: none_exist`.
3. Scalar comparison aliases such as `equals: 0` and `matches_regex: '...'`.
4. Single-Test / one-State boilerplate and private capability binding.
5. Source-only shared discovery modules (a separate, already demonstrated maintainability benefit).

These are **candidates**, not adopted features. The developer tools must accept explicit longhand, reject contradictory shorthand and compile the short form into the fully specified canonical representation. No scanner syntax or evaluator changes.

## Board decision gate

Compare three to five real examples across canonical YAML, explicitly versioned compact YAML, and editor-generated canonical YAML. Publish per-capability prevalence and exact reverse-proof status. Favor author comprehension and lossless conversion over line reduction; preserve complex multi-Test and Variable/Set/filter logic when semantically necessary.

[Research issue #225](https://github.com/vanderpol/scap-ng/issues/225) · [existing quantifier investigation #224](https://github.com/vanderpol/scap-ng/issues/224)
