# Full-benchmark reviewer handoff gates (iteration 003)

Recorded 2026-09-30. These gates apply independently to **RHEL 9** and
**Windows 11**. Do not substitute iteration-001 Windows output for the
iteration-003 native split Rule/Assessment conversion.

## Review-ready definition

A full native benchmark becomes a candidate for project-owner review when:

1. **Pinned source and accounting:** its pinned published XCCDF/STIG source,
   source checksum/revision, benchmark version, full Rule count, selectable
   automated/manual checks, Profiles, Values/Parameters, Groups, fixes,
   applicability, and exceptions are accounted for. Any unconverted Rule or
   unsupported construct has a source-specific diagnostic.
2. **Native design:** Benchmark owns Profiles/Groups/Parameters. Each Rule is
   the policy/assertion object and exposes named Assessment selections using
   explicit relative Assessment paths plus applicability IDs. Those source
   references resolve without filename guessing. No separate Policy object is
   required. No XCCDF/OVAL/CPE XML serialization leaks into executable native
   source; lineage remains in evidence.
3. **Faithfulness:** supported assessments retain Test and State distinct
   existence semantics, variables, filtering, behaviors, sets, result
   propagation, applicability, and platform capabilities. No silent
   downgrade; deprecated OVAL test blockers are explicit.
4. **Validation:** source conversion scripts run to completion; native
   cleanliness, assessment reference resolution, package integrity,
   representative schema/Schematron and semantic round-trip gates pass.
   Remaining warning classes are enumerated, with impact stated.
5. **Review UX:** a reviewer README names entry points to benchmark,
   representative policy and assessment files, full check-text/remediation
   lookup, a provenance ledger, and exact commands/artifact links to
   reproduce results. It distinguishes manual tests from automated checks.

Review can proceed with *documented* nonblocking warnings; no blanket
"100% lossless" claim is warranted without the relevant conformance proof.

## Reviewer feedback 2026-09-30 — current blockers and resolved items

- [#30 Profile selection and inherited defaults](https://github.com/vanderpol/scap-ng/issues/30): compact publisher Profiles remain the intended representation. Current RHEL 9 full-review generation performs an independent effective-selection audit across Benchmark/Group/Rule defaults, Profile actions and `extends`; any mismatch blocks generation. This is no longer a known RHEL 9 handoff blocker when the current full-review workflow is green.
- [#31](https://github.com/vanderpol/scap-ng/issues/31) is **superseded and closed**. The project intentionally replaced the intermediate Policy object with Rule-owned policy/assertion semantics. The authoritative chain is Benchmark → Rule → selected Assessment. RHEL 9 current review source uses explicit relative Rule → Assessment paths and validates them.
- Remaining handoff blockers are benchmark-specific conversion/semantic blockers, unresolved source constructs, or failed readiness checks—not absence of a separate Policy layer.
- [Source README](../source/split-rule-assessment/README.md) documents the current Rule-owned source model. Passing schema/package/round-trip checks still does not establish target execution equivalence.

## Snapshot: RHEL 9

- Current reviewer source path:
  `research/iterations/003/review/rhel9-current-full/`
- Historical generated conversion evidence also remains under
  `research/iterations/003/source/split-rule-assessment/rhel9-full/`.
- Pinned converted benchmark shows **445 Rules**. Committed package summary
  shows **879 assessment objects**, **1326 logical objects**, and 1327 members.
- Current diagnostics summary: **0 ERROR, 0 FATAL**, **736 WARN**.
  Warning categories: **468 OVAL_OBJECT_COMMENT_MISSING** and **268
  OVAL_STATE_COMMENT_MISSING**. These reflect absence of descriptive source
  comments; do not silently synthesize fictitious source labels.
- **Publishing correction verified:** `v003-rhel9-full.yml` run
  [36716375732](https://github.com/vanderpol/scap-ng/actions/runs/36716375732)
  completed successfully at source commit `314a02e` on 2026-09-30.
  Committed `benchmark.yaml`, `diagnostics.json`, and package-summary evidence
  are available. This establishes successful generation and publishing,
  **not** final assessment-level losslessness or design-review readiness.
- Current full-review generation pins the source revision/checksum, accounts
  for all 445 Rules, verifies Rule Assessment selections, Profiles, grouping,
  applicability references, source metadata, native cleanliness, relative
  references, reverse OVAL schema validity and semantic round-trip parity.
- Remaining limitation: these are source/representation handoff gates, not
  target-runtime execution equivalence. That limitation SHALL be stated to
  reviewers rather than used to delay useful source review indefinitely.

## Snapshot: Windows 11

- Current reviewer source path:
  `research/iterations/003/review/windows11-current-full/`
- Source is pinned to NIWC revision
  `8c8e5dff860af6b1290ee9273a282db24278f8d5` and Windows 11 V2R10
  archive SHA256
  `e4b8d55b58aa80124bd0974977af4c7f7bde35c748e2940e02857419292d8c3d`.
- Current full-review workflow run
  [36794192423](https://github.com/vanderpol/scap-ng/actions/runs/36794192423)
  completed successfully and published commit
  `fa144b75c`.
- The review contains **257 Rules** and **767 native YAML files**.
  Native validation reports relative-reference resolution, native cleanliness,
  presentation ordering and Group membership all passed.
- Component-resolved source splitting accounted for **246 Rules with OVAL**
  and **11 source-manual/no-OVAL Rules**, with zero unresolved references,
  zero ambiguous OVAL Definition references and zero schema-invalid Rule
  closures.
- Rule source audit compares all **257 source/native Rules** with
  `issues: []`.
- Profile selection audit compares all **11 Profiles** with
  `mismatch_count: 0` for every Profile and `issues: []`.
- Supported automated Assessments carry reverse omni-schema validation and
  semantic representation-comparator evidence.
- One source Rule, `SV-253476`, uses deprecated OVAL
  `windows.user_test`. Per project policy, its `default` and
  `automated` source selectors are not converted to automated NG content.
  The published source manual Assessment is used as the native default/manual
  choice instead.
- The same deprecated Test type occurs in the Rule's
  `local_enabled_administrators` applicability source. That automated
  applicability Assessment is intentionally omitted and the source manual
  procedure owns the applicability decision. Both exceptions are explicit in
  `evidence.json`; no round-trip-equivalence claim is made for those skipped
  deprecated paths.
- This is a candidate for owner **source/design review**. Target-runtime
  evaluator equivalence remains a separate conformance gate and is not implied
  by successful source conversion/round-trip evidence.

## Notification decision

Notify the owner *for each independently ready benchmark* with direct
links to the complete native source and review instructions, version/source
pin, rule counts, validation results, and remaining issues. Never notify
based only on the existence of an old converter output or a green smoke
workflow.
