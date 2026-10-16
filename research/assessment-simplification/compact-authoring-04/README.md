# SCAP-NG 0.4 — one human-readable Assessment language

**Pre-alpha specification draft in progress — not approved, not a release.** The existing 0.3 specification, scanner bundle format and Board Discussion #213 remain unchanged.

## Joval showcase — best starting point (October 16, 2026)

**For advance sharing:** [20-minute Joval meeting overview with three embedded, source-backed NG examples](JOVAL-MEETING-2026-10-16.md). For evaluator implementers, the [focused technical notes](JOVAL-TECHNICAL-PREVIEW.md) include additional Windows, DNS and Apache examples and explicit proof boundaries.

**[Original OVAL single → modern SCAP-NG 0.4 showcase](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015)** gives ten source-backed examples as original OVAL XML, 0.4 YAML and corresponding JSON with provenance. [Joval meeting guide](JOVAL-TECHNICAL-PREVIEW.md) includes the real versus optional/proposed transformation distinction and the [conditional semantic questions](../conditional-10/JOVAL-IF-ELSE-QUESTIONS.md). The showcase's optional if/else illustration is **not** a proven automatic six-state OVAL normalization; tested collection `for_each` examples are separately identified.

## Current six-STIG YAML + JSON authoring review packet

**[Permanent pre-alpha discussion prerelease](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3)** contains all six STIG authoring conversions in **both formats**, with all 2,958 Rule choice links resolved and all 12 previously omitted shared manual Assessments included ([issue #230](https://github.com/vanderpol/scap-ng/issues/230)), including the scoped field-requirement candidate (Test/group/field) and human `and`/`or` logic. [Joval meeting reading guide](JOVAL-TECHNICAL-PREVIEW.md). All 1,396 converted Assessments and 2,144 native Tests passed the candidate overlay, explicit scope inverse, full 0.4 base and native schema checks; JSON values mirror YAML. **Pre-alpha, not Board-approved or scanner-compiled.** The revised Test-level name is `collected_items_require`; native field/record-level `require` remains distinct. The separate earlier RHEL9 preview remains historical.

**Start with [0.4 scope and release gates](0.4-SCOPE-AND-RELEASE-GATES.md).** It explicitly includes actual field names in State predicates, a human-readable `require` vocabulary, operator-as-key comparisons, native typed arrays, and Windows record fields. One **authoring** grammar is the goal, not a second optional set of hidden YAML shortcuts.

[Short Board preview](ONE-GRAMMAR-BOARD-PREVIEW.md) · [Human terminology and semantics](HUMAN-VERBIAGE-PROPOSAL.md) · [Focused draft JSON Schema fragment](assessment-language-fragment.schema.json) · [Schema validation workflow](https://github.com/vanderpol/scap-ng/actions/runs/38740807220) · [Research issue #227](https://github.com/vanderpol/scap-ng/issues/227).

## Evidence already established

- **921/921 automated-by-default Rules** across RHEL 9, Windows 11 and Windows Server 2025 can be represented in the researched single grammar. The [strict conversion CI](https://github.com/vanderpol/scap-ng/actions/runs/38737558392) covers native collection/filters, literal arrays, Windows records and exceptional quantifier pairs.
- **942 Assessments** were analyzed. **930** reconstructed identical parsed 0.3 source; **12** used a separately documented State-free matching normalization supported by the pinned OVAL result model. Do not confuse exact-source proof with model-level equivalence.
- **942/942** generated Assessment syntax fragments passed the first [candidate 0.4 grammar validation](https://github.com/vanderpol/scap-ng/actions/runs/38740807220) and **eight** focused positive/negative tests passed. **This is a focused fragment, not a complete `schema/v0.4.0/` tree** and not full capability or scanner conformance.
- [Original full 65-source quantifier census](https://github.com/vanderpol/scap-ng/actions/runs/38718081754) and [61-package reversible research modernization](https://github.com/vanderpol/scap-ng/actions/runs/38716331301) support broad applicability; macOS shell-heavy content is excluded from the primary grammar ranking. Four SQL-extension source blockers remain explicit.
- [Original research-only RHEL 9 authoring preview ZIP](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-rhel9-compact-authoring-research) records earlier staged shorthand candidates. **It is historical experiment evidence, not the proposed final one-grammar format.**

## In-scope features

**One standard** using `states: - owner_uid: {equals: 0, require: ...}`, direct field names also inside `record.fields`, an explicit requirements vocabulary at each scope, typed comparison operation names as keys, ordered State lists, static literal Object/State arrays with independent `value_match`, and a fail-closed migration compiler. No hidden defaults; no de-automation just to avoid unusual native checks. Keep the existing Benchmark/Rule/Assessment architecture, manual alternatives, provenance, result contracts, `evaluate`, shared Objects and `for_each`.

## Decisions before normative promotion

1. Ratify one clear English spelling for each **necessary** quantifier meaning, including exactly-one and negative matching. The current 20-pair enumeration guarantees migration expressibility, **not** human-readable ratification.
2. Make the full schema capability-specific, reject invalid fields, enforce typed array `value_match`, and include record/list/selector/filter contracts.
3. Establish evidence for non-exact State-free normalizations and preserve original unusual Tests unless a complete reference semantics proof justifies a rewrite.
4. Create the **full independent versioned 0.4 schema snapshot** with all mappings/ref IDs and run fast six-benchmark integration. [Current-main converter default-selector regression #226](https://github.com/vanderpol/scap-ng/issues/226) must be resolved before full release conversion claims.
5. Request owner/Board review using a concise, real before/after example set, not the large research history.

**No SCAP-NG scanner exists in pre-alpha.** Scanner differential and implementation conformance are *later milestones* and do not block authoring-language drafting or approval. The specification still requires independently testable collection/result semantics.

