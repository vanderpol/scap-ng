# Changelog

This file summarizes material SCAP-NG changes by release. Each entry links to
the GitHub issue that explains the work. Research-only, deferred, and rejected
proposals are not listed as delivered features.

## 0.4.0 — Unreleased

### Native content compilation

- Added native bundle regression coverage for schema-valid manual Assessment
  alternatives: both independent authoring formats preserve the manual
  procedure/response and Rule choice without inventing an automated Test
  program. Incomplete manual responses fail native schema validation.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Extended the pinned real RHEL 9 OVAL-to-0.4 converter regression through
  schema-checked native `.scapng` construction and independent verification,
  including program/Test inventories and explicit non-scanner status. This
  closes a test gap between the version upgrader, typed authoring IR, and
  bundle compiler, without claiming semantic scanner parity.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Added a manual six-STIG release gate that compiles canonical YAML and JSON
  independently and rejects any difference in the resulting native `.scapng`
  bytes or their previously published immutable release hashes. It is not a
  routine push check, scanner conformance test, or new content release.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Added independently verifiable YAML-only and JSON-only native 0.4 authoring
  compilation, with a paired mode that compares independently compiled
  `.scapng` bytes. Invalid source, ambiguous references and incompatible
  version declarations fail closed. This is content compilation, not scanner
  execution. [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Restored `.scapng` compilation for the native 0.4.0 authoring model,
  extending the earlier manifest-authoritative compiler architecture. Every
  automated Assessment now carries a separately compiled Test dispatch and
  six-state result-expression program, with canonical member hashes and
  independent program/source verification. Native source-exact Test shapes
  are preserved rather than guessed into simplified checks. The maintained
  three-STIG fast gate compiles RHEL 9, Windows 11 and Apache 2.4 UNIX;
  a deliberate six-STIG checkpoint reuses immutable JSON/YAML source inputs
  without rerunning their expensive original OVAL conversion. These are
  **content compilation** results, not live collector/scanner conformance or
  publisher signing evidence. [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#229](https://github.com/vanderpol/scap-ng/issues/229)
- Added optional detached-CMS signing and **externally anchored** verification
  for already-compiled native 0.4 `.scapng` bundles. Verification checks the
  signer, detached signature, manifest, exact compiled Test/Result programs,
  hashes and entire logical graph; no embedded certificate is implicitly
  trusted. Published six-STIG preview bundles remain unsigned until a real
  publisher signing identity and trust policy are supplied. This proves
  package authenticity only, not live scanner correctness.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Canonical authoring checkpoint

- Kept four superseded 0.4-A r3 research workflows available for explicit
  historical diagnostics but removed their automatic push triggers; their
  frozen source archive predates the 11 shared Applicability Assessment
  restorations. Active 0.4 tools remain covered by canonical fast checks.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
- Published source-invertible, native-schema-validated 0.4.0 JSON/YAML
  authoring for six STIGs (4,012 documents, 1,390 automated Tests), after
  restoring 11 omitted shared applicability Assessments from immutable 0.3
  source. Both formats, six deterministic source-only package manifests,
  original-OVAL requirement axes, and isolated CMS test signatures passed
  the full checkpoint. This historical source-only release predates the
  distinct native compiled-bundle checkpoint; scanner parity remains open.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)
  [#251](https://github.com/vanderpol/scap-ng/issues/251)
- Split rapid 0.4 development regressions from deliberately triggered full
  six-STIG release builds. The routine integration sample validates pinned
  RHEL 9, Windows 11 and Apache 2.4 UNIX source packages without rerunning
  the complete YAML/JSON conversion for every edit.
  [#232](https://github.com/vanderpol/scap-ng/issues/232)

### Converter and authoring safeguards

- Updated the 0.4 authoring converter and typed source compiler for canonical
  `field_requirement` scopes and complete conditions. The compiler indexes
  nearest explicit field declarations; source-exact records, repeated fields,
  uncommon Test requirements and non-AND State operators retain diagnostics
  and inverse evidence. Added an original published RHEL9 OVAL → YAML/JSON →
  compiler trace. This does not establish executable scanner parity or finish
  six-STIG promotion. [#251](https://github.com/vanderpol/scap-ng/issues/251)

- Integrated the approved `field_requirement` grammar into the version-local
  Assessment schemas, with explicit Test/group/condition/field inheritance,
  complete-condition AND/OR/ONE/XOR, and implicit AND within `fields` maps.
  Rejects missing field scope and mixed legacy names on the canonical path;
  retains source-exact uncommon requirement and record fallbacks. Converter,
  compiler, editor and six-STIG promotion remain separate integration work.
  [#240](https://github.com/vanderpol/scap-ng/issues/240)
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
  [#239](https://github.com/vanderpol/scap-ng/issues/239)

- Added source-verified Object-local Filters for the 28 unambiguous
  single-operand synthetic Set cases in the six-STIG authoring corpus,
  retaining eight provenance-ambiguous cases unchanged. Conversion requires
  pinned original OVAL source classification, exact reconstruction of the
  prior authored graph, and matching ordered Filter predicates. This is not
  a scanner-execution or six-state conformance claim.
  [#248](https://github.com/vanderpol/scap-ng/issues/248)
- Extended the source-gated Filter cleanup to **19 additional Test-local
  wrappers across 14 Assessment documents**, identifying their original OVAL
  Test `object_ref` rather than relying on title equality. Together with the
  first 28, this removes **47** converter-induced singleton wrappers from
  the canonical six-STIG authoring candidate. The remaining 31 Set instances
  are retained for genuine source Set semantics or further reference proof.
  An independent whole-corpus YAML/JSON inverse guard rejects any change
  outside the proven 19 sites. This is source reconstruction, not scanner
  execution parity. [#248](https://github.com/vanderpol/scap-ng/issues/248)
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

- The 0.4 fast CI now enforces the native Result schemas' required, nonblank
  `summary` for both Rule Results and standalone Assessment Results. Top-level
  Rule Result `message` is not an alternate canonical field; earlier version
  snapshots remain unchanged. [#203](https://github.com/vanderpol/scap-ng/issues/203)
  [#205](https://github.com/vanderpol/scap-ng/issues/205)
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
