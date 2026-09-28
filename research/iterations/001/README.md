# SCAP-NG Research Iteration 001

**Status:** complete research archive — native source design continues in `../002/`.


**Status:** Preliminary research / architecture exploration  
**Purpose:** Preserve the initial design discussion and provide concrete prototypes for review by the OVAL Board, NIST SCAP participants, DISA, scanner developers, and content authors.

Iteration 001 is intentionally **not a draft specification** and remains our internal working iteration until deliberately shared outside the project.

**SCAP 1.4 forward conversion is a hard requirement for supported, non-obsolete source semantics.** SCAP-NG deliberately excludes OVAL tests whose **effective current status remains deprecated** after applying documented OVAL Community reinstatement decisions; affected definitions must be corrected in SCAP 1.4 before conversion. A historical OVAL 5.12.x `deprecated_info` annotation alone is not sufficient when later governance explicitly reinstated a test. Every architecture and authoring-syntax experiment must otherwise remain capable of representing converted SCAP 1.4 content through the same faithful semantic model.

Published migration evidence is scoped to the pinned NIWC Atlantic `scap-content-library/Current` corpus. The first depth pass focuses on RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025; the final conversion gate covers every individual benchmark in the pinned `Current/` tree.

> The generated YAML in iteration 001 is fidelity-first migration evidence, not proposed final SCAP-NG authoring syntax. Iteration 002 is the clean native-source design effort.


## Contents

- `preliminary-architecture-discussion.md` — consolidated architecture discussion and rationale.
- `prototype-comparison.md` — comparison criteria for the two candidate architectures.
- `lessons-learned.md` — implementation-derived lessons and requirements discovered while building iteration 001.
- `result-explanation-model.md` — structured decisive-outcome explanation model for Pass/Fail diagnostics.
- `complex-oval-prototype-backlog.md` — ranked real-world OVAL cases selected for semantic stress testing.
- `real-world-oval-findings.md` — requirements and observations learned from pinned published NIWC STIG migration cases.
- `oval-self-assertion-findings.md` — separate OVAL 5.12.3 language-conformance findings from the pinned Self-Assertion corpus.
- `scap14-public-corpus-conversion-requirement.md` — hard pre-specification conversion gates for the versioned public SCAP 1.4 corpus.
- `semantic-ir.md` — one faithful SCAP 1.4 semantic model feeding all authoring/rendering formats.
- `four-anchor-reuse-methodology.md` — rule mapping, exact assessment reuse, parameterization-candidate, and maintenance-cost methodology across RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025.
- `public-corpus-manifest.yaml` — pinned public sources used for repeatable conversion coverage.
- `prototypes/full-benchmarks/` — primary file-oriented benchmark prototypes, results, and signed bundles.
- `board-review/` — internal evidence package for comparing the three candidate YAML forms using four real published benchmarks, measured reuse, Windows migration blockers, and decision questions.
- `feedback/` — questionnaire, response template, response evidence, and decision register.
- `notes/` — supporting observations.
- `tools/` — iteration-specific package build, splitting, semantic-IR, normalization, and rendering tooling.
- `generated/niwc-rule-splits/` — 1,333 schema-valid per-rule OVAL splits plus semantic IR for the four published priority benchmarks.
- `generated/native-normalizations/` — generated native-semantic normalization examples and cross-platform semantic-fingerprint comparisons.
- `generated/four-anchor-reuse/` — deep reuse analysis and representative three-format reuse views for RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025.
- `generated/full-corpus-reuse/` — compact reuse/fan-out, Check Text mapping, parameterization-candidate, and deprecated-source-debt evidence across all 65 individual signed benchmarks in the pinned NIWC corpus.
- `showcases/rhel9-sv-258179/` — flagship complex published OVAL case, including the distinction between faithful conversion and a policy-review normalization candidate.

## Current benchmark evidence

Iteration 001 now uses two complementary evidence sets.

### Deep four-anchor conversion

The published RHEL 9, Oracle Linux 9, Windows 11, and Windows Server 2025
benchmarks are converted from pinned signed SCAP 1.4 packages into one canonical
SCAP-NG semantic model and rendered in all three YAML forms:

1. combined rule with shared technical bases / policy overlays;
2. split policy / assessment / binding;
3. Ansible-inspired authoring with no Ansible runtime dependency.

All four pass rule/accounting and three-rendering semantic-equivalence checks.
Representative exact-reuse groups are committed for Linux and Windows.

### Full signed-benchmark reuse survey

All 65 individual signed benchmark ZIPs in the pinned NIWC `Current/` corpus
are processed through the same OVAL semantic fingerprint model for compact
reuse/mapping analysis.

The survey covers 8,892 XCCDF rules and 7,084 supported automated assessments.
It finds 3,413 unique exact technical assessments, with 3,671 total duplicate
assessment-definition units avoidable (51.82%). Of those, 3,639 units are
avoidable specifically through cross-benchmark reuse.

The original three seven-rule Windows Client, Windows Server, and Linux
prototype families remain useful controlled fixtures for result-model and
language experiments, but they are no longer the primary evidence for the
format decision.

## Source rule

The repository authoring source uses individual files. Aggregate policy or assessment YAML documents are not the intended source model. See `prototypes/full-benchmarks/source-layout.md`.

## Policy-only publication

Policy-only packages show what a DISA-style publisher could provide without automation. Existing `check` / STIG Check Content is the default manual assessment procedure; no duplicate questionnaire artifact is required.

## Automated publication

Regardless of source architecture, a scanner-facing automated benchmark is a single self-contained signed `.scapng` package containing complete policy and all required automation. Shared source assessments are resolved at build time.

## Reproducibility

All packages are built from committed individual YAML files by `research/iterations/001/tools/build_full_benchmarks.py` and verified by `tools/verify_scapng_prototype_bundle.py`.

All prototype content is illustrative and is not an official DISA requirement.
