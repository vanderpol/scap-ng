# SCAP-NG Research Iteration 001

**Status:** Preliminary research / architecture exploration  
**Purpose:** Preserve the initial design discussion and provide concrete prototypes for review by the OVAL Board, NIST SCAP participants, DISA, scanner developers, and content authors.

Iteration 001 is intentionally **not a draft specification**. It records the starting design direction, unresolved questions, and controlled prototype examples needed to make later decisions with evidence rather than preference.

## Contents

- `preliminary-architecture-discussion.md` — consolidated discussion and rationale from the initial SCAP-NG design work.
- `prototype-comparison.md` — criteria for comparing the two candidate content architectures.
- `prototypes/full-benchmarks/` — **primary iteration 001 prototypes**: complete seven-rule Windows and Linux benchmarks for both candidate architectures, policy-only and automated packages, matching full-scan results, manifests/signatures, and actual `.scapng` bundles.
- `prototypes/combined-rule/` and `prototypes/split-policy-assessment-binding/` — earlier focused rule fragments retained as design history; superseded by the full-benchmark examples for architecture review.
- `feedback/` — questionnaire, response format, evidence archive, and decision register.
- `notes/` — supporting observations, including analysis of representative SCAP 1.4 results.
- `tools/` — iteration-specific build tooling; reusable repository tooling remains under the root `tools/` directory.

## Prototype architectures

### A. Combined rule

Policy metadata, Check Content, applicability, and automated assessment are represented in one rule object in the automated authoring form.

### B. Split policy / assessment / binding

Policy, automation, and the mapping between them are separate authored objects.

Neither architecture is selected by this iteration.

In **both** designs, the scanner-facing automated benchmark is a single self-contained signed `.scapng` package containing the complete policy and matching automation. Scanner operators are not expected to install independent policy and automation packages.

## Full benchmark prototype coverage

Each Windows and Linux benchmark contains **seven rules**: six automation candidates plus one intentionally manual-only policy rule.

The Windows set exercises:

1. native `if / elif / else` role-dependent policy;
2. a complex nested AND/OR criteria tree and compact root-cause reporting;
3. a simple successful native security-status check;
4. a multi-assertion service check;
5. explicit Not Applicable behavior;
6. collection-permission Error behavior;
7. policy-only/manual assessment using existing Check Content.

The Linux set exercises:

1. a very large filesystem population with evidence caps and early termination;
2. effective configuration assembled from multiple SSH configuration sources;
3. typed package-version comparison;
4. an ANDed multi-value sysctl failure;
5. applicability leading to Not Applicable;
6. configuration parser/collection Error behavior;
7. policy-only/manual assessment using existing Check Content.

The full-scan result examples deliberately include Pass, Fail, Not Applicable, Error, automated, and manual results.

## Policy-only publication

Both architectures include complete policy-only `.scapng` bundles showing what a DISA-style publisher could produce without automation.

Existing `check` / STIG Check Content is treated as the default manual procedure. No duplicate questionnaire or explicit manual-assessment block is required merely to make a rule manually assessable.

## Package reproducibility

All eight package artifacts are generated from committed source by:

`research/iterations/001/tools/build_full_benchmarks.py`

and verified by:

`tools/verify_scapng_prototype_bundle.py`

The repository workflow:

`.github/workflows/build-scapng-iteration001.yml`

rebuilds and verifies every policy-only and automated bundle, including member hashes and the prototype Ed25519 manifest signature.

The prototype signing key is a public RFC 8032 test key. It demonstrates package mechanics only and provides **no publisher trust**.

## Important limitation

All rule IDs, titles, policy language, expected values, observations, and results are illustrative unless explicitly identified as sourced material. They must not be interpreted as official DISA requirements.

## Iteration workflow

Feedback should be captured using `feedback/questionnaire.md` and `feedback/response-template.md`. Returned feedback files should be placed under `feedback/responses/` unchanged as evidence. Accepted conclusions should then be reflected in `feedback/decision-register.md` with stable decision IDs.

Iteration 001 may continue evolving while it remains internal. A new numbered iteration should be created when external review or an explicit research checkpoint makes preserving the prior state useful.
