# SCAP-NG 0.2.0 OVAL Board review checkpoint

Date: 2026-10-04

**Status:** schema development frozen; six-case Board sample pilot delivered; **human/OVAL Board review pending**.

Technical schema baseline: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

Later `main` commits add Board content, tests, CI, and documentation without changing the frozen 0.2.0 schema meaning unless explicitly recorded.

## What is in the checkpoint

- Concise **[SCAP 1.4 → SCAP-NG key changes](SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)**.
- Six converter-produced **[review Assessments](review-content/0.2.0/README.md)**: family, UNIX file, Windows registry, directory filter, Windows WMI process query, and symlink resolution.
- Pinned source provenance, meaningful native IDs, mechanical and refined native forms, and independently stated expected outcomes.
- Four earlier supporting examples retained separately; they are not claimed as converter successes.
- Versioned **[Board proposals](proposals/README.md)** and published **[voting links](VOTES.md)**.

## What 0.2.0 is trying to preserve

- Used, non-deprecated OVAL semantics: Tests, Objects, States, Variables, Items, Sets, Filters, datatypes, comparisons, existence/cardinality, dependency graphs, and six-state result behavior.
- Explicit authored applicability rather than hidden scanner platform inference.
- Source behavior and defects without silent semantic repair.
- Manual assessment as a first-class assessment method.
- Clear evidence lineage and bounded result reporting.

## Important working decisions

- OVAL 5.12.3 is the current semantic baseline, with later corrections/reinstatements reviewed explicitly.
- Effectively deprecated Tests block automated conversion unless authoritatively reinstated.
- Native capability names may remove historical numeric/version suffixes while exact source identity remains in provenance.
- Migration evidence is separate from executable native content.
- Source-authored conditional behavior is allowed; automatic Boolean-to-conditional rewriting is not.
- ESX/VMware and Kubernetes additions that still need upstream semantic guidance remain deferred.

## Evidence

The six-case publication commit was `8262e7e03418c229b85db6fe5cab600c9b92b8e9`. Its repository-boundary, rebaseline-smoke, current-design-regression, and fast-five conversion workflows all completed successfully.

The exact technical baseline also passed the broader 0.2.0 freeze gates, including Self-Assertion validation and the intentional full NIWC corpus deliverable run.

These checks establish structural, conversion, and known-result evidence. They do **not** establish independent scanner equivalence, complete collector coverage, or live-target conformance.

## What the OVAL Board should review

- Semantic fidelity and readability of the six small source-to-NG examples.
- The 5.12.3-plus-reviewed-fixes baseline and any known errata/reinstatements.
- Any non-deprecated OVAL semantics that appear omitted or reinterpreted.
- Deprecated-Test handling and cleaner native capability naming.
- Applicability, record/entity, existence/cardinality, Variable/Set/Filter, and result behavior.
- Deferred/new OVAL 6 Test semantics, especially ESX/VMware.
- The separation of Rule policy, Assessment execution, evidence, and Results.

## What happens after review

Accepted examples seed the conformance corpus. Demonstrated defects become small permanent regressions before schema changes. Then the project can expand conversion coverage, add live/runtime conformance, close known converter gaps, and proceed toward editor/reference-scanner and standards work.

Schema development remains frozen unless focused evidence demonstrates a genuine defect or human/Board review accepts a required change.
