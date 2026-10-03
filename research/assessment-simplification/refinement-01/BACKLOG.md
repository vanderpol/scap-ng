# Durable follow-ups

Implementation/evidence checkpoint:
`cb0bfd7e27a942650fff2d6a3bfc0ffd7082fcdd` on `main`.
Final handoff/publication metadata may be in a later commit; use directory git
history for the containing SHA. Research remains separate from schema and review
stabilization.

Checked open and closed issue titles plus related issue bodies before creating
these focused follow-ups. No external publisher issue or Board vote was opened.

| Issue | Bounded work | Evidence needed |
| --- | --- | --- |
| [#122](https://github.com/vanderpol/scap-ng/issues/122) | Validate typed DNS acquisition against scoped OVAL results | Same-target original/candidate execution, Variable-instance evidence, module/privilege/scope and mutation/error fixtures. No schema-only closure. |
| [#123](https://github.com/vanderpol/scap-ng/issues/123) | Investigate RHEL9 root xattr audit b64 coverage | Pinned source IDs, distinct b32/b64 fixture, current publisher disposition. Preserve source anomalies until separately reviewed correction. |

Existing work remains relevant rather than duplicated:

- [#24](https://github.com/vanderpol/scap-ng/issues/24): finite table tooling and
  expanded-diff author/usability trials fit the existing authoring-workflow issue.
- [#44](https://github.com/vanderpol/scap-ng/issues/44): Apache shared typed
  acquisition and consistency/cache identity inform the deferred composition
  research. This experiment does not implement cross-Assessment dependencies.
- [#26](https://github.com/vanderpol/scap-ng/issues/26) and
  [#50](https://github.com/vanderpol/scap-ng/issues/50): independent evaluator/
  target conformance and known-result corpus remain separate from synthetic
  observation tests.
- [#116](https://github.com/vanderpol/scap-ng/issues/116): source defect tracking
  provides the triage format for the focused audit candidate.

Board questions remain [unpublished version 2 candidates](DECISIONS.md). Promoting
them requires coordinated review; no reaction count is treated as ratification.
