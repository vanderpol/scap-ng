# Changelog

This file summarizes material SCAP-NG changes by release. Each entry links to
the GitHub issue that explains the work. Research-only, deferred, and rejected
proposals are not listed as delivered features.

## 0.4.0 — Unreleased

### Converter and authoring safeguards

- Added source-verified Object-local Filters for the 28 unambiguous
  single-operand synthetic Set cases in the six-STIG authoring corpus,
  retaining eight provenance-ambiguous cases unchanged. Conversion requires
  pinned original OVAL source classification, exact reconstruction of the
  prior authored graph, and matching ordered Filter predicates. This is not
  a scanner-execution or six-state conformance claim.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
- Added version-local Filter validation and canonical YAML/JSON generation
  regression checks to reject disappearing/altered Filters and newly
  introduced synthetic one-operand Sets. Earlier published authoring archives
  remain immutable.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)

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
- Renamed the expected-value quantifier to `value_match` in 0.3 for
  Variables, literal arrays and direct Organizational Inputs; preserved OVAL
  `var_check` meaning and independent observed `match`/`existence`.
  [#194](https://github.com/vanderpol/scap-ng/issues/194)
- Resolved native Rule, Assessment, dependency and applicability authoring
  references by logical ID at compilation; transitional source-path support
  remains for imported content. [#199](https://github.com/vanderpol/scap-ng/issues/199)
- Removed redundant `assessment_choices.default` from native 0.3 Rules; the required `default_assessment_choice` now names the actual publisher check, preserving Tailoring selection and manual-only checks. Frozen 0.2.0 is unchanged. [#217](https://github.com/vanderpol/scap-ng/issues/217)
- Added owner-approved 0.3 concise datatype authoring: native scalar literals
  omit redundant comparison types; specialized OVAL comparisons use explicit
  typed operators such as `version_greater_than_or_equal`, never `compare_as`.
  The compiler reconstructs canonical typed predicates before existing
  capability/schema validation and scanner bundle emission; variable/input
  contracts stay typed. Historical 0.2 is unchanged. Source-only six-STIG
  parity and separate OVAL runtime conformance remain explicit checkpoints.
  [#200](https://github.com/vanderpol/scap-ng/issues/200)
- Added typed compact Rule Result findings and Test-centered bounded
  Assessment evidence without claiming actual scanner results.
  [#203](https://github.com/vanderpol/scap-ng/issues/203) [#205](https://github.com/vanderpol/scap-ng/issues/205)
- Added schema-level restrictions, compiler linkage checks and typed policy
  freezing for direct expected-State Organizational Inputs. Native scanner
  evaluation conformance remains an open gate.
  [#193](https://github.com/vanderpol/scap-ng/issues/193)

## Earlier checkpoints

SCAP-NG 0.2.0 is the frozen earlier review baseline. Its exact technical state
and review material remain preserved in the repository; this changelog will not
retroactively invent issue linkage for historical commits.
