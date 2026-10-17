# SCAP-NG 0.4 — next authoring-readability decision gate

**17 October 2026 — proposed working checkpoint; not a normative language change or Board decision.** Owner concern: 0.3 is not understandable enough to auditors, and repeated YAML vocabulary experiments are yielding diminishing returns. Track research in [#235](https://github.com/vanderpol/scap-ng/issues/235), semantic outcomes in [#229](https://github.com/vanderpol/scap-ng/issues/229), eventual Assessment editor in [scap-ng-editor #2](https://github.com/vanderpol/scap-ng-editor/issues/2).

## Hold steady until evidence forces a change

- Baseline: current split `require.items` / `require.match`; observed field names and native operators; structural `states.and/or` and `fields.and/or`; existing `sources/checks/evaluate` model. **Research only, not adopted `schema/v0.4.0/`.**
- Do NOT add new wrappers (`valid`, `claims`, `condition`, generic `scope`), duplicate authoring dialects, long merged cardinality aliases, or unproved missing-field defaults.
- A real improvement must make a specific common question easier **without changing original source meaning**; a shorter code count or exact dictionary inversion alone is insufficient.

## Gate A — close field presence and scope semantics (#229 / #235)

Each field/reference gets one **effective, traceable contract**: *must exist, may be absent, must not exist, or exactly one exists* (when source requires it), plus independent comparison and value/record cardinalities. The above is a conceptual classification, **not a claim that four words cover all OVAL six-state outcomes**. Never let a parent Item rule become a field or record default. Resolve State-wide shared field requirements and local exceptions with an explicit precedence model. Reject inheritance ambiguity and missing policies rather than making up a source meaning.

Run pinned original-source fixtures before changing vocabulary:

| Real assessment | Required counterexamples | What cannot be conflated |
| --- | --- | --- |
| RHEL9 `/home` nosuid | No selected mount; one mount with `rw,nosuid`; two mounts with just one compliant; incomplete/error collection | Item count vs all selected Items vs *at least one* mount-option value |
| Windows 11 SV-253495 | DomainRole records `[1]`, `[3]`, `[1,3]`, missing record, and partial/error WMI results | Whole State `or` vs OR of field membership; nested records vs root Items |
| Windows 11 user rights | Guests plus non-Guests; no trustee; duplicated trustees; missing trustee field | At least one matching Item vs all Items; scalar value vs Item identity |
| RHEL9 SV-257889 dependent initialization files | No matching non-system files; no matching root files; one file missing one of eight permission fields; collection error | Optional root Item population vs required field comparisons within present Items |
| Apache SV-214228 | A command Item exists with `stdout_line` absent, wrong, correct; no Item; missing/errored values | Required collected command Item vs optional State field |
| DNS SV-259345 | Both signature bounds; value below/within/above range; missing `stdout_line`; status `error`/incomplete; no value with source comparison | Test-level inherited State-field contract vs comparison, and absence of values vs Item absence |

Acceptance: publish a pinned fixture ledger with source ID, observation shape, expected **OVAL six-state** outcome, effective field-policy origin (local/group/Test) and whether expectation is independently established or still unknown. Use existing `tests/v04-semantic-boundaries` and truth-table harness where applicable. Fix reference disagreements or explicitly block unsupported cases; do not report schema/round-trip checks as scanner results.

## Gate B — build the minimum read-only auditor preview (research-only, #235)

From the *same parsed Assessment* used in structural validation, render a one-page explanation with four questions:

1. **What is observed?** Named typed source, selector, dependencies and provenance, expandable.
2. **What is required?** Exact observed Item count, matching Item rule, required/optional/absent fields and multi-value/record scope, labeled with population names instead of vague `match`.
3. **How can it pass?** Named display-only branches of the original `evaluate` tree, preserving full `and`/`or`, repeated check references and six-state behavior (not procedural `if/else`).
4. **What is unresolved?** Missing/unknown/error/incomplete interpretations, provenance not shown, or semantics without an independently proven contract; mark `not_verified` rather than inventing an explanation.

First proof on **RHEL9 SV-257851** and **Windows 11 SV-253495**, then Linux dependent files, Apache and DNS. Output a static, self-contained Markdown/HTML page directly under github.com (not expiring Actions-only artifacts), with links to the exact source and fixture rows. No extra authoritative hand-authored policy prose. This is not semantic editor implementation or a grammar promotion.

Acceptance: all named source paths, quantified scopes, and every `evaluate` leaf are accounted for; the mixed WMI `[1,3]` example is specifically rejected by the explanation; an incomplete or unknown condition is never silently displayed as a pass/fail. Demonstrate fail-closed cases in CI. If the proof-sheet script itself is not tested, do not call the preview machine-derived.

## Gate C — a genuinely unfamiliar reader (#235 / editor #2)

Give the [answer-free blind packet](FRESH-EYES-BLIND-REVIEW-PACKET.md) to several readers who have not seen OVAL/SCAP-NG. **Do not show the expected answers or this discussion beforehand.** Compare the same real scenarios shown as (i) raw current YAML and (ii) the automatically generated auditor preview. Test: zero/multiple collected Items; value repeated; WMI `[1,3]`; optional/absent field; unknown/error; three Windows passing routes. Ask the reader to answer or mark 'cannot determine', with confidence. Collect errors, not preference votes alone.

Acceptance: no reviewer incorrectly labels a *confirmed failing* complete-case counterexample as compliant; gaps are triaged into (a) wrong semantics, (b) unclear authoring YAML, (c) unclear rendered explanation, (d) missing source evidence. A small sample is a formative usability test, not statistical proof. Change **only** the specific misleading presentation or grammar construct, and retest; don't restart a competing DSL.

## Responsibility and stop conditions

- **#229** owns original-source semantics, partial/error cases and reference fixtures. Any unknown outcome blocks a claim of faithful conversion, not necessarily unrelated reviewer research.
- **#235** owns language/presentation research, source-exact comparisons, proof sheet, blind reviewer packet, and concise accept/reject decision.
- **scap-ng-editor #2/#3** own the later guided Assessment authoring experience. Current owner-set restriction remains: do not task Codex with opinionated 0.4 semantic editor code until semantic contracts are approved, verified and owner authorizes implementation. Schema-neutral, source-preserving foundations remain a separate decision.
- **Board-facing deliverable:** ONE short summary of what improved, what failed, what evidence says, what remains blocked, and links to two complete examples. No premature '0.4 accepted' claim.

## Immediate order

**First:** complete Gate A's field-policy source-to-fixture ledger for Apache/DNS/Linux, then cross-check Windows record scopes. **Second:** gate the deterministic preview on those semantics. **Third:** run the blind test and make the vocabulary decision. **Stop** running fresh synonym or nested-wrapper experiments in parallel unless a fixture demonstrates a concrete missing capability.
