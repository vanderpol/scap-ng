# SCAP-NG 0.4 — one human-readable Assessment language

**Pre-alpha specification draft in progress — not approved, not a release.** The existing 0.3 specification, scanner bundle format and Board Discussion #213 remain unchanged.

## Start here — technical review for any audience

- **[Short 0.4 overview](ASSESSMENT-REVIEW-OVERVIEW.md)** — three embedded real NG Test examples: Linux mount selection, Windows registry alternatives, and user-right cardinality. Suitable as the main pre-read.
- **[Detailed technical examples](ASSESSMENT-REVIEW-TECHNICAL.md)** — Windows WMI record scoping, DNS exact-one checks, Apache Variables, proof boundaries, and guidance on Test versus private/shared Object titles.
- **[Conditional semantics questions](../conditional-10/CONDITIONAL-REVIEW-QUESTIONS.md)** — six-state behavior, `if/else` versus faithful OVAL Boolean graphs, and evidence collection.

**Optional full content:** [ten original OVAL → NG YAML/JSON comparisons](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-oval-to-ng-showcase-20261015) and [six-STIG r3 authoring preview](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3) (YAML + JSON). The release tags are historical immutable identifiers, not audience restrictions. r3 contains all six representative STIGs, repairs 12 shared manual Assessment files, and resolves all 2,958 Rule Assessment-choice links. Both are **pre-alpha research**, not scanner-conformant 0.4 binaries.

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

