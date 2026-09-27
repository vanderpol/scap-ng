# SCAP-NG Research Iteration 001

**Status:** Preliminary research / architecture exploration  
**Purpose:** Preserve the initial design discussion and provide concrete prototypes for review by the OVAL Board, NIST SCAP participants, DISA, scanner developers, and content authors.

Iteration 001 is intentionally **not a draft specification** and remains our internal working iteration until deliberately shared outside the project.

## Contents

- `preliminary-architecture-discussion.md` — consolidated architecture discussion and rationale.
- `prototype-comparison.md` — comparison criteria for the two candidate architectures.
- `prototypes/full-benchmarks/` — primary file-oriented benchmark prototypes, results, and signed bundles.
- `feedback/` — questionnaire, response template, response evidence, and decision register.
- `notes/` — supporting observations.
- `tools/` — iteration-specific package build tooling.

## Current benchmark scope

Three seven-rule benchmark families are represented:

1. Windows Client STIG-like policy
2. Windows Server STIG-like policy
3. Linux STIG-like policy

Each exists in both the combined-rule and split policy/assessment/binding candidates, and each produces policy-only and automated packages: **12 total `.scapng` bundles**.

The two Windows benchmarks intentionally demonstrate cross-STIG automation reuse. Five technical assessments are shared or parameterized across different policy rule IDs, titles, and references; one automated assessment in each Windows benchmark is benchmark-specific.

## Source rule

The repository authoring source uses individual files. Aggregate policy or assessment YAML documents are not the intended source model. See `prototypes/full-benchmarks/source-layout.md`.

## Policy-only publication

Policy-only packages show what a DISA-style publisher could provide without automation. Existing `check` / STIG Check Content is the default manual assessment procedure; no duplicate questionnaire artifact is required.

## Automated publication

Regardless of source architecture, a scanner-facing automated benchmark is a single self-contained signed `.scapng` package containing complete policy and all required automation. Shared source assessments are resolved at build time.

## Reproducibility

All packages are built from committed individual YAML files by `research/iterations/001/tools/build_full_benchmarks.py` and verified by `tools/verify_scapng_prototype_bundle.py`.

All prototype content is illustrative and is not an official DISA requirement.
