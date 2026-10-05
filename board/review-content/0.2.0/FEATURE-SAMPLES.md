# SCAP-NG 0.2.0 Assessment feature samples

This index is the single Board-facing inventory of Assessment-language examples. It deliberately links to existing validated fixtures instead of copying the same example into multiple directories.

The sample set has two goals:

1. show the capability patterns most often encountered in current DISA-derived content; and
2. demonstrate the SCAP-NG language features that are easy to miss in trivial Object/State/Test examples.

A feature is not considered covered merely because a schema permits it. It needs reviewable source content and validation evidence.

| Assessment feature | Canonical sample | Coverage intent |
| --- | --- | --- |
| Explicit Object / State / Test | [UNIX file](content/unix-file.assessment.yaml) | Basic resource selection, comparison, existence and Test aggregation |
| Direct Variable Test | [Constants](content/constants.assessment.yaml) | `variable.value` without a redundant Object |
| Constant and multi-value Variables | [Constants](content/constants.assessment.yaml) | Typed one/many values |
| Variable components and concatenation | [Concat](content/concat.assessment.yaml) | Derived Variable dataflow and Cartesian results |
| Additional Variable functions | [Variable functions](content/variable-functions.assessment.yaml) | Compact Self-Assertion-derived `split`, `substring`, and `regex_capture` examples with direct `variable.value` Tests |
| Object-component Variable, chained Variables and arithmetic | [Filter](content/filter.assessment.yaml) | Non-trivial dataflow feeding collection filtering |
| Set union and intersection | [Filter](content/filter.assessment.yaml) | Nested Set composition |
| Set difference | [Set difference](content/set-difference.assessment.yaml) | Explicit subtraction of one reusable Object/Set from another |
| State-backed Set filter | [Directory filter](content/directory-filter.assessment.yaml) | EXCLUDE filtering with a Variable-backed State |
| Explicit Test existence/item quantifiers | [Registry](content/registry.assessment.yaml), [Directory filter](content/directory-filter.assessment.yaml) | No hidden OVAL-style Test defaults |
| Variable comparison quantifier | [Directory filter](content/directory-filter.assessment.yaml) | Explicit `variable_match` |
| Multiple State aggregation | [Multi-State](content/multi-state.assessment.yaml) | Explicit `states_match`; omission is invalid when multiple States are present |
| Correlated record fields | [Windows WMI query](content/windows-process-query.assessment.yaml) | Whole-record correlation rather than independent field matching |
| Assessment-result dependency and reuse | [Assessment result dependency](content/assessment-result-dependency.assessment.yaml), [Dependency stress case](content/dependency.assessment.yaml) | Statically declared dependency, simple consumption, repeated reuse and result provenance |
| Conditional evaluation | [Conditional evaluation](content/conditional-evaluation.assessment.yaml), [Dependency stress case](content/dependency.assessment.yaml) | Focused local conditional plus dependent-Assessment branching without hiding which branch is selected |
| Intrinsic Assessment applicability | [Intrinsic applicability](content/intrinsic-applicability.assessment.yaml) | Assessment-level applicability distinct from Rule applicability |
| Explicit evidence projection | [Explicit field list](content/reported-elements.assessment.yaml), [compared fields](content/reported-elements-compared.assessment.yaml) | Explicit reporting modes; no omitted/default reporting behavior |
| Typed Assessment input / Organizational Input consumption | [Organizational input](content/organizational-input.assessment.yaml) | Declared typed input becomes a Variable used only as expected-state data; no executable behavior is supplied by the input |
| Manual Assessment | [Manual review](content/manual.assessment.yaml) | Native human determination without OCIL workflow graphs |
| Authored result redaction | [Redaction](content/redaction.assessment.yaml) | `redact_result: true` preserves technical truth while suppressing disclosed evidence value |
| Reporting projection and redaction runtime behavior | [Reported-elements conformance fixture](../../../tests/reported-elements-0.2.0/ownership.assessment.yaml) | Canonical tested reporting source; runtime tests cover projection and redaction preservation |
| Collected Item reuse/import authoring proposal | [End-to-end walkthrough](proposals/item-reuse.md), [producer](proposals/item-reuse-producer.assessment.yaml), [consumer](proposals/item-reuse-consumer.assessment.yaml), [request binding](proposals/item-reuse-request.yaml), [materialized Item](proposals/item-reuse-materialized-item.json) | Shows the complete path from reusable collection through exact run-time binding to a locally materialized imported Item with source provenance |
| Item import/materialization | [Item-materialization conformance set](../../../tests/item-materialization-0.2.0/README.md) | Imported Item provenance and materialized evidence semantics |
| Conditional six-state result propagation | [Conditional conformance set](../../../tests/conditional-0.2.0/) | `true`, `false`, `error`, `unknown`, `not_evaluated`, and `not_applicable` scheduling |
| Assessment Result normalization | [Assessment-result conformance set](../../../tests/assessment-results-0.2.0/) | Test/State/Variable/Item lineage and dependency results |


## New NG feature samples

These examples highlight SCAP-NG capabilities that are not merely one-for-one OVAL Test-family translations. They are the quickest place for a reviewer to see what the NG model adds or makes explicit.

| New NG feature | Focused sample | What to review |
| --- | --- | --- |
| Explicit semantic choices / no hidden defaults | [UNIX file](content/unix-file.assessment.yaml), [Directory filter](content/directory-filter.assessment.yaml), [reported-elements samples](content/reported-elements.assessment.yaml) | Collection behaviors, existence/check quantifiers, filters, and reporting choices are authored explicitly rather than supplied by invisible NG defaults |
| Source-authored conditional evaluation | [Conditional evaluation](content/conditional-evaluation.assessment.yaml) | Explicit condition, then, and else branches; branch selection is authored and reviewable rather than inferred by the scanner |
| Assessment-result dependency/reuse | [Assessment result dependency](content/assessment-result-dependency.assessment.yaml) | Static dependency declaration and consumption of another Assessment's technical result without copying its Tests/Objects |
| Intrinsic Assessment applicability | [Intrinsic applicability](content/intrinsic-applicability.assessment.yaml) | Applicability is ordinary authored Assessment logic, separate from Rule/platform naming metadata |
| Standalone applicability Assessment | [Standalone applicability](content/standalone-applicability.assessment.yaml) | A reusable Assessment can exist specifically to determine applicability, using the same ordinary Test/Object/State/Variable language |
| Explicit not_applicable result branch | [Conditional not applicable](content/conditional-not-applicable.assessment.yaml), [dependency stress case](content/dependency.assessment.yaml) | Authored branch can produce a reasoned technical not_applicable outcome without conflating that with scanner-side platform magic |
| Explicit evidence projection | [Explicit field list](content/reported-elements.assessment.yaml), [compared fields](content/reported-elements-compared.assessment.yaml) | Together with existing `all` samples, these demonstrate all three explicit reporting modes; omission is not a hidden reporting default |
| Evidence redaction | [Redaction](content/redaction.assessment.yaml) | Technical truth is retained while a sensitive result value is deliberately withheld |
| Typed Organizational Input consumption | [Organizational input](content/organizational-input.assessment.yaml) | Organization-supplied policy data is typed and can feed expected State only; it does not alter executable behavior |
| Manual Assessment | [Manual review](content/manual.assessment.yaml) | Native human determination without carrying forward OCIL workflow structure |
| Collected Item reuse/import | [Item reuse proposal](proposals/item-reuse.md) | Proposed author/runtime split for reusing collected observations while retaining local evaluation and complete provenance |
| Item materialization and import provenance | [Conformance set](../../../tests/item-materialization-0.2.0/README.md) | Result-side import/materialization contract, explicit scope, local IDs, and source lineage |
| Bounded evidence/completeness behavior | [Assessment-result conformance set](../../../tests/assessment-results-0.2.0/) | Results distinguish technical truth from how much evidence was retained/materialized |

The first eight rows are current 0.2.0 authoring/result concepts. Collected Item reuse authoring remains a proposal even though the result-side import/materialization contract is already exercised by conformance fixtures. Future-iteration ideas, such as target-scoped Organizational Input resolution, are intentionally excluded from the 0.2.0 sample corpus until their semantics are reviewed.

## Remaining Assessment-language sample gaps

These are still required before the Board sample inventory can be called feature-complete:

- a concise embedded-Object example if embedded Objects remain in the final 0.2.0 authoring contract;
- finalize the collected-Item reuse authoring proposal and adopt it into the 0.2.0 schema only after the source identity/binding questions in [the proposal](proposals/item-reuse.md) are resolved;

Runtime conditions such as an unsupported collector/capability are Result semantics, not authored Assessment-language features. They belong in the Result conformance inventory rather than being represented as fake source syntax here.

Policy-only concepts such as Benchmark Parameters, Profiles, Tailoring, Rule selection/scoring, and package trust are intentionally not duplicated here. Their examples belong with the policy/results specifications, although this index may link to them where an Assessment input binding crosses that boundary.

## Review rule

Every new Assessment-language feature SHALL have at least one small, human-reviewable example and automated validation. Frequently used DISA capability examples should remain separate from feature-stress examples so prevalence is not confused with language coverage.
