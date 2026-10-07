# Changelog

This file summarizes material SCAP-NG changes by release. Each entry links to
the GitHub issue that explains the work. Research-only, deferred, and rejected
proposals are not listed as delivered features.

## 0.3.0 — Unreleased

### Governance and review process

- Defined the SCAP-NG core objectives and bidirectional objective-to-issue
  traceability so release work can be evaluated against explicit project goals
  rather than feature novelty alone. [#174](https://github.com/vanderpol/scap-ng/issues/174)
- Simplified repository documentation and navigation, including a single active
  review entry point and clearer separation of specification, review,
  governance, and historical material. [#182](https://github.com/vanderpol/scap-ng/issues/182)
- Rebuilt the 0.3 examples surface as a reviewer-facing SCAP-NG feature tour,
  with embedded SCAP 1.4 comparisons and schema-validated 0.3 Scan, Benchmark,
  automated Assessment, bounded-evidence, and Manual Assessment Result examples.
  [#187](https://github.com/vanderpol/scap-ng/issues/187) [#128](https://github.com/vanderpol/scap-ng/issues/128)
- Established the specification as a prerelease/release artifact rather than a
  continuously edited design notebook; accepted changes are normalized into the
  specification at release checkpoints. [#180](https://github.com/vanderpol/scap-ng/issues/180)
- Required every new commit to reference a GitHub issue that records why the
  work exists. [#181](https://github.com/vanderpol/scap-ng/issues/181)
- Established this issue-linked release changelog process. [#181](https://github.com/vanderpol/scap-ng/issues/181)

### Language, schema, and results

No unreviewed 0.3 research proposal is listed here as a delivered feature.
Accepted 0.3 language/schema/result changes will be added as they pass the human
promotion gate.

## Earlier checkpoints

SCAP-NG 0.2.0 is the frozen earlier review baseline. Its exact technical state
and review material remain preserved in the repository; this changelog will not
retroactively invent issue linkage for historical commits.
