# SCAP-NG 0.2.0 OVAL Board review checkpoint

Date: 2026-10-04

Status: **SCHEMA DEVELOPMENT STOPPED / BOARD PACKAGE PREPARED — SAMPLE ASSESSMENT CONTENT PENDING**

Technical schema baseline:

`7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`

Current repository `main` may be a later non-semantic descendant containing maintenance, branch-management, CI-policy, focused-regression, and handoff documentation. The technical schema meaning for this checkpoint is the exact baseline above.

## Purpose

This checkpoint deliberately stops further SCAP-NG 0.2.0 schema development and shifts the project from agent-driven language evolution to human/OVAL Board review.

The goal is not to claim that 0.2.0 is perfect. The goal is to present a coherent, tested draft that can be independently reviewed before additional language semantics are introduced.

## Required sample Assessment content

The OVAL Board checkpoint is **not complete for delivery** until the bounded Codex pilot contributes **5–10 human-reviewable SCAP-NG 0.2.0 sample Assessments** under:

`board/review-content/0.2.0/`

Those samples are part of the Board checkpoint itself, not a later unrelated content-development activity.

The set SHALL include:
- native-authored examples that are easy for a human reviewer to understand;
- converted examples that demonstrate preservation of existing OVAL semantics;
- at least one nontrivial example using references/dependencies such as Variables, Sets, Filters, or equivalent graph behavior;
- at least one result/evidence example showing why the Assessment reached its expected result;
- provenance back to the original OVAL/SCAP source where converted;
- independently stated expected results;
- concise notes explaining what language feature each sample demonstrates.

Prefer small examples over entire benchmarks. The purpose is to let Board members inspect the proposed language directly without reverse-engineering large generated content.

The sample set SHALL be human-reviewed before the checkpoint is labeled ready for external Board delivery. After acceptance, these same samples SHOULD seed the canonical conformance corpus rather than being re-created independently.


The 0.2.0 baseline has substantial automated evidence and targeted semantic review, but it has **not** received an exhaustive independent human audit of every capability and interaction.

Going forward:
- machine-green does not mean human-accepted;
- semantic changes use the review packet in `MAINTAINING.md`;
- defects are reduced to small permanent fixtures in `tests/focused-regressions/`;
- unresolved semantics are presented for human/Board review instead of silently encoded by an agent.

## Evidence already completed

The exact 0.2.0 technical baseline passed:

- Current-design regression contracts on Ubuntu and Windows:
  https://github.com/vanderpol/scap-ng/actions/runs/37217182532
- Rebaseline smoke regression:
  https://github.com/vanderpol/scap-ng/actions/runs/37217182619
- OVAL Self-Assertion semantic validation:
  https://github.com/vanderpol/scap-ng/actions/runs/37217182564
- Repository preservation/current-archive boundary validation:
  https://github.com/vanderpol/scap-ng/actions/runs/37217182523
- Full NIWC Current native normalize/compile deliverable run:
  https://github.com/vanderpol/scap-ng/actions/runs/37217182538

The maintained fast integration lane also passed:
https://github.com/vanderpol/scap-ng/actions/runs/37217710436

The 65-benchmark NIWC corpus is now manual-only and reserved for intentional deliverables, freezes/releases, and OVAL Board review checkpoints.

## What 0.2.0 is trying to preserve

Core principles include:

- preserve non-deprecated OVAL semantics used by current content or SCAP 1.4 validation evidence unless there is an explicit documented reason not to;
- reject effectively deprecated OVAL Tests rather than silently carrying them forward;
- maintain OVAL platform-family distinctions where collected-data semantics materially differ;
- preserve Variables, Sets, Filters, existence/cardinality behavior, datatypes, comparison semantics, dependency graphs, and evidence lineage;
- keep applicability explicit and authored rather than relying on hidden scanner platform classification;
- separate Rule/policy meaning from Assessment implementation;
- keep manual assessment first-class;
- preserve source defects as source defects instead of silently repairing them during conversion;
- keep migration provenance separate from native executable syntax;
- support understandable results/evidence and bounded evidence collection.

## Notable 0.2.0 decisions for Board review

1. **Native capability naming.** OVAL source identities remain durable provenance, while reviewed native names may remove historical version suffixes where semantics justify it. Example: supported `windows:wmi57_test` maps to native `windows.wmi.query`; deprecated `windows:wmi_test` remains a migration blocker.

2. **Deprecated Test policy.** Effectively deprecated Tests do not become native SCAP-NG capabilities unless later OVAL governance explicitly reinstates them.

3. **OVAL 5.12.3 baseline with selective OVAL 6 review.** Existing semantics are based on 5.12.3 plus later known corrections/reinstatements. OVAL 6.0 is used primarily to identify genuinely new Tests rather than as a wholesale replacement baseline.

4. **ESX deferral.** New ESX/VMware Tests remain deferred pending upstream/contributor guidance.

5. **Kubernetes deferral.** `kubepsp_test` and `kubectl_test` remain deferred for 0.2.0.

6. **Source-invalid content handling.** Invalid source OVAL is quarantined and reported; conversion does not silently repair it.

7. **Result/evidence layers.** Schema validity, semantic validity, known-result evaluator conformance, collection/acquisition conformance, live-target execution, and migration equivalence are distinct evidence levels.

8. **Human review over automation.** Automated evidence is necessary but not sufficient to accept future language semantics.

## Specific questions for OVAL Board/community feedback

Feedback is especially requested on:

- whether the OVAL 5.12.3 + documented later reinstatement approach is a reasonable semantic baseline;
- whether reviewed removal of historical numeric Test suffixes in native naming is acceptable when source OVAL identity remains in provenance;
- whether any non-deprecated OVAL Test/Object/State semantics appear unintentionally omitted or reinterpreted;
- whether the deprecated-Test exclusion/reinstatement policy matches current OVAL governance intent;
- whether ESX new-Test semantics should remain deferred pending clarification from the original contributor;
- whether there are known OVAL 5.12.3 errata or genuinely new OVAL 6.0 Test semantics that should influence a later schema version;
- whether the separation of Rule policy, Assessment logic, collected evidence, and Results creates interoperability concerns.

## Review method

For any issue found during Board/human review:

1. create the smallest possible reproducer;
2. state expected behavior independently;
3. classify the defect/question;
4. fix and test against the small fixture;
5. retain it permanently as a regression;
6. use focused tests and the fast integration lane during development;
7. defer the full 65-benchmark confirmation until the next intentional deliverable/checkpoint.

## What reviewers should not infer

This checkpoint does not claim:
- OVAL Board approval;
- exhaustive human audit;
- complete live collector coverage;
- independent scanner equivalence;
- complete vendor/target conformance;
- final trust/signature or privacy profiles;
- editor completion;
- final external-standard status.

## Next phase

The immediate implementation activity is the bounded 5–10 case content/conformance pilot in:
`transition/codex-test-content-0.2.0-task.md`

The pilot's accepted output is a **required part of this OVAL Board checkpoint** and must be staged under `board/review-content/0.2.0/` with expected results, provenance, and reviewer notes.

The pilot must stop for human review before scale-out. Once the samples are accepted, update this checkpoint to **READY FOR OVAL BOARD DELIVERY**. Schema development remains stopped unless a focused reproducer demonstrates a genuine defect or the OVAL Board/human review accepts a required change.
