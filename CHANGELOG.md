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

- Made private Objects and States consumer-local and reserved `shared_objects:`
  for reusable/referenceable acquisition identity. [#165](https://github.com/vanderpol/scap-ng/issues/165)
- Standardized meaningful internal component IDs with required type suffixes
  (`-object`, `-state`, `-variable`, `-test`, `-input`) and schema
  enforcement. [#190](https://github.com/vanderpol/scap-ng/issues/190)
- Added native scalar/typed literal collections for exact removal of static
  Variable plumbing. [#188](https://github.com/vanderpol/scap-ng/issues/188)
- Added collection `for_each`, including correlated nested lineage semantics,
  while keeping Test/evaluate aggregation separate. [#164](https://github.com/vanderpol/scap-ng/issues/164) [#189](https://github.com/vanderpol/scap-ng/issues/189)
- Canonicalized 0.3 existence/match/comparison/filesystem vocabulary and shorter
  benchmark-local Assessment names. [#151](https://github.com/vanderpol/scap-ng/issues/151)
- Kept explicit named-Test + `evaluate` composition unchanged for 0.3; redesign
  is deferred. [#167](https://github.com/vanderpol/scap-ng/issues/167)
- Deferred shared Observation beyond normative 0.3 while retaining its production
  evidence for the next design cycle. [#166](https://github.com/vanderpol/scap-ng/issues/166)
- Kept one explicit `reported_elements` model and one canonical result contract;
  hidden reporting defaults and normative thin/full result profiles are out.
  [#125](https://github.com/vanderpol/scap-ng/issues/125) [#170](https://github.com/vanderpol/scap-ng/issues/170) [#177](https://github.com/vanderpol/scap-ng/issues/177)

## Earlier checkpoints

SCAP-NG 0.2.0 is the frozen earlier review baseline. Its exact technical state
and review material remain preserved in the repository; this changelog will not
retroactively invent issue linkage for historical commits.
