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
2. **Native design:** benchmark owns Profiles/Groups/Parameters, Rules
   reference Policy checks/selectors and applicability IDs, and policy
   assessment bindings resolve. No XCCDF/OVAL/CPE XML serialization leaks
   into executable native source; lineage remains in evidence.
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

## Snapshot: RHEL 9

- Current native source path:
  `research/iterations/003/source/split-rule-assessment/rhel9-full/`
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
- Outstanding review work: check exact published source pin and complete
  Rule/selector accounting; sample the actual generated assessments against
  OVAL source for human readability, applicability, manual inputs and
  existence/variable/filter behaviors before handoff.

## Snapshot: Windows 11

- The green workflow `convert-windows11-scap14-to-ng.yml` is
  **iteration-001** evidence (257 Rules, source-pinned NIWC content);
  it is not the iteration-003 clean-native benchmark.
- No Windows 11 sibling to `rhel9-full/` existed under
  `research/iterations/003/source/split-rule-assessment/` at this
  checkpoint.
- Next: build Windows 11 with the current v003 source design and the same
  provenance/diagnostic package structure and reviewer checks as RHEL 9.
  Carry over the pinned published source, not the old generated source.
- A Windows 11 handoff notification must wait for that full v003 conversion,
  its source accounting, and its current validation evidence.

## Notification decision

Notify the owner *for each independently ready benchmark* with direct
links to the complete native source and review instructions, version/source
pin, rule counts, validation results, and remaining issues. Never notify
based only on the existence of an old converter output or a green smoke
workflow.
