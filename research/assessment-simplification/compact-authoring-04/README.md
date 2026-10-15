# Compact SCAP-NG authoring research (0.4)

**Research only, not accepted syntax.** Canonical 0.3 and [Board Discussion #213](https://github.com/vanderpol/scap-ng/discussions/213) are unchanged.

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
