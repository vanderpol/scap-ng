# SCAP-NG 0.2.0 handoff checkpoint — content development

Date: 2026-10-03

Status: **handoff preparation, pending final 0.2.0 semantic closure and exact-head validation**.

Provenance: Evidence/Audit plus owner direction. This checkpoint records the current owner-approved sequencing and bounded remaining work. It does not claim that 0.2.0 is released, Board-ratified, or target-runtime conformant.

## Current owner direction

Content development comes before editor development.

The converted and newly authored SCAP-NG corpus should become the practical basis for later editor design and validation. Editor work must not become the source of truth for the language.

VMware ESX new-Test work is deferred pending upstream guidance from the submitter/community. Existing draft ESX work remains useful experimental evidence, but completion of the ESX family is **not a 0.2.0 blocker**.

For OVAL 6.0, focus only on genuinely **new Tests/capabilities**. Preserve the OVAL 5.12.3-derived baseline for existing semantics; do not downgrade existing behavior to match older 6.0 material or mechanically adopt unrelated OVAL 6.0 language changes.

## Remaining 0.2.0 closure work

Before handing broad content expansion to Codex, complete and record these bounded items.

Current progress at the latest documentation checkpoint: items 1–3 have semantic
dispositions; item 2 also has semantic-validator regressions. Item 1 has a focused
truth-table regression. Item 4 is in reconciliation. Item 5 remains the final gate.

1. **Direct Variable zero-value semantics — DISPOSITIONED, CI EVIDENCE PENDING**
   - Specify the expected Test behavior when a directly tested Variable resolves to zero values.
   - Add focused positive/negative/six-state conformance cases as applicable.
   - Make the result deterministic enough that downstream content authors do not invent different interpretations.

2. **Typed authored-literal policy — DISPOSITIONED/ENFORCED, CI EVIDENCE PENDING**
   - Resolve the representation/validation boundary for typed authored values, especially boolean textual values such as `"false"` versus native JSON boolean `false`.
   - Define when lexical conversion is permitted and when authoring is invalid.
   - Add independent semantic/validation tests.

3. **OVAL 6.0 new-Test disposition after ESX deferral — COMPLETE FOR 0.2.0 SCOPE**
   - Reconcile the two Kubernetes new Tests identified by the pinned audit.
   - Both Kubernetes Tests are explicitly deferred for 0.2.0; see [the disposition](kubernetes-oval6-disposition-2026-10-03.md).
   - `kubepsp_test` targets removed PodSecurityPolicy; `kubectl_test` awaits a native Kubernetes resource/API model and conformance content.
   - Do not reopen the broader OVAL 6.0 delta.

4. **Documentation/version reconciliation — IN PROGRESS**
   - Update coverage and transition language that still says large numbers of OVAL 6 Tests “remain” when those counts include deferred ESX work.
   - Reconcile schema/reference/result/result-package documentation and capability matrices with the final owner-approved scope.
   - Preserve 0.1.0 behavior and historical checkpoints.

5. **Exact-head validation and freeze checkpoint**
   - Run the maintained schema/meta-validation, semantic validation, authoring-contract, result-package, preservation and relevant bundle/compiler tests on one exact commit.
   - Require successful Windows and Linux CI for that exact technical checkpoint.
   - Record exact commit SHA, workflow evidence, source pins, known limitations and explicit deferrals.
   - That commit becomes the receiving baseline for Codex content-development work.

These are the current handoff gates. Complete live collector execution, full vendor corpus coverage, independent scanner equivalence, exhaustive #128 conformance content, signature/trust implementation, and editor development are downstream work and are not prerequisites to freezing the 0.2.0 authoring contract unless a closure test exposes a specification defect.

## Codex content-development sequence

After the checkpoint above is frozen, give Codex the maintained task in [codex-test-content-0.2.0-task.md](codex-test-content-0.2.0-task.md).

The intended order is:

1. minimal native single-feature fixtures and independent expected results;
2. small feature combinations and six-state edge cases;
3. pinned OVAL/SCAP Self-Assertion conversions;
4. representative production migration cases;
5. substantial RHEL 9, Oracle Linux 9, Windows 11 and Windows Server 2025 coverage;
6. larger/full benchmark integration and reusable cross-benchmark Assessments.

Apache, DNS and other platforms/applications should be added when they exercise distinct capabilities or complexity not covered by the four anchor platforms.

Codex should not redesign schemas merely to make a fixture pass. Every failure must first be classified as source content, converter, SCAP-NG model/schema, semantic validator, evaluator/harness, collector/platform limitation, or unresolved specification question.

## Future editor sequencing

Do **not** start the editor in parallel with initial corpus expansion.

The future editor should be designed against evidence from:
- clean native-authored SCAP-NG;
- faithful converted SCAP 1.4 content;
- difficult Assessment graphs;
- Variables/Sets/Filters;
- manual Assessments and Organizational Input;
- applicability;
- shared/reused Assessments;
- invalid fixtures and diagnostics;
- provenance and result/evidence requirements.

Codex may record authoring-usability observations during content work, including repetitive patterns, likely author mistakes, safe derivations, and documentation needs. Those observations are editor requirements/research evidence, not permission to add editor-specific language constructs.

## Specification follow-up

The detailed Codex instructions intentionally contain many specification-shaped statements. After the 0.2.0 freeze, perform a specification coverage audit against that handoff.

Anything that is a universal author/scanner requirement but exists only in Codex guidance should be promoted to the appropriate normative specification or implementation/conformance guide. Workflow-only advice should remain outside the normative core.

Desired authority hierarchy:

**specification → implementation/reference guidance → conformance content → editor**

The editor teaches and enforces SCAP-NG; it does not define SCAP-NG.

## Receiving-session first action

A receiving session should:
1. read `AGENTS.md`, `START-HERE.md`, CURRENT-DESIGN and this checkpoint;
2. report exact repository/branch/SHA;
3. verify whether the five 0.2.0 closure items above are complete at that SHA;
4. reproduce the documented baseline validation before changing content;
5. use [codex-test-content-0.2.0-task.md](codex-test-content-0.2.0-task.md) only after the frozen 0.2.0 checkpoint is identified.

Do not infer that historical experimental content is current architecture, and do not resume deferred ESX expansion without new owner/upstream direction.
