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
| Assessment-result dependency and reuse | [Dependency](content/dependency.assessment.yaml) | Statically declared dependency, repeated reuse and result provenance |
| Conditional evaluation | [Dependency](content/dependency.assessment.yaml) | `if/then/else` without hiding which branch is selected |
| Intrinsic Assessment applicability | [Intrinsic applicability](content/intrinsic-applicability.assessment.yaml) | Assessment-level applicability distinct from Rule applicability |
| Explicit evidence projection | [Reported elements](content/reported-elements.assessment.yaml) | Explicit field list; no omitted/default reporting behavior |
| Typed Assessment input / Organizational Input consumption | [Organizational input](content/organizational-input.assessment.yaml) | Declared typed input becomes a Variable used only as expected-state data; no executable behavior is supplied by the input |
| Manual Assessment | [Manual review](content/manual.assessment.yaml) | Native human determination without OCIL workflow graphs |
| Authored result redaction | [Redaction](content/redaction.assessment.yaml) | `redact_result: true` preserves technical truth while suppressing disclosed evidence value |
| Reporting projection and redaction runtime behavior | [Reported-elements conformance fixture](../../../tests/reported-elements-0.2.0/ownership.assessment.yaml) | Canonical tested reporting source; runtime tests cover projection and redaction preservation |
| Collected Item reuse/import authoring proposal | [End-to-end walkthrough](proposals/item-reuse.md), [producer](proposals/item-reuse-producer.assessment.yaml), [consumer](proposals/item-reuse-consumer.assessment.yaml), [request binding](proposals/item-reuse-request.yaml), [materialized Item](proposals/item-reuse-materialized-item.json) | Shows the complete path from reusable collection through exact run-time binding to a locally materialized imported Item with source provenance |
| Item import/materialization | [Item-materialization conformance set](../../../tests/item-materialization-0.2.0/README.md) | Imported Item provenance and materialized evidence semantics |
| Conditional six-state result propagation | [Conditional conformance set](../../../tests/conditional-0.2.0/) | `true`, `false`, `error`, `unknown`, `not_evaluated`, and `not_applicable` scheduling |
| Assessment Result normalization | [Assessment-result conformance set](../../../tests/assessment-results-0.2.0/) | Test/State/Variable/Item lineage and dependency results |

## Remaining Assessment-language sample gaps

These are still required before the Board sample inventory can be called feature-complete:

- a concise embedded-Object example if embedded Objects remain in the final 0.2.0 authoring contract;
- finalize the collected-Item reuse authoring proposal and adopt it into the 0.2.0 schema only after the source identity/binding questions in [the proposal](proposals/item-reuse.md) are resolved;
- unsupported-capability execution/result behavior, if that remains a native Assessment contract rather than an implementation/reporting-only concern.

Policy-only concepts such as Benchmark Parameters, Profiles, Tailoring, Rule selection/scoring, and package trust are intentionally not duplicated here. Their examples belong with the policy/results specifications, although this index may link to them where an Assessment input binding crosses that boundary.

## Review rule

Every new Assessment-language feature SHALL have at least one small, human-reviewable example and automated validation. Frequently used DISA capability examples should remain separate from feature-stress examples so prevalence is not confused with language coverage.
