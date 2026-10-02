# SCAP-NG review surface

This directory is the single entry point for material we want external reviewers to examine.

If you are an OVAL Board member, content author, scanner implementer, or other reviewer, start here. You should not need to understand the repository's development tooling or historical layout to review SCAP-NG.

## Directory contract

- `current/` — the current coherent review set. Material here is intended to be read together.
- `iterations/` — preserved earlier review sets and design iterations. These remain useful for history and comparison, but are not the current design unless explicitly referenced from `current/`.
- `README.md` — this navigation and status contract.

## What belongs in the review surface

Reviewable output includes:

- the current architecture/design explanation;
- normative or near-normative specification text;
- schemas that define the proposed authoring/result contract;
- small, understandable examples;
- small representative benchmark/rule/assessment samples used to demonstrate real-world coverage;
- stable full-URL references to complete generated review artifacts produced by CI;
- Board decision questions and links to their GitHub Discussions;
- validation/equivalence summaries needed to understand what has and has not been demonstrated.

The review surface should favor clarity over exhaustive project history.

## What does not belong here

Development infrastructure stays outside `review/`, including:

- converters and migration utilities;
- validators and repository-normalization tools;
- test harnesses and CI helpers;
- generated scratch/intermediate data;
- transition notes for ChatGPT/Codex continuity;
- bulk source corpora and third-party source material.

Those materials may be linked when they provide evidence, but reviewers should not have to browse them to understand the design.

## Current migration status

The repository is being losslessly rebaselined. Existing authoritative material currently remains in `specification/`, `schema/`, `board/`, and selected `research/iterations/003/` locations while preservation and dependency checks are completed.

During that migration, `review/current/` is the canonical navigation layer. A file is not considered current merely because it exists elsewhere in the repository.

No historical material is deleted as part of establishing this review surface.


## Review lifecycle — hard rule

The review surface has one active target and immutable completed baselines.

1. `review/current/` is the **only** active external review target.
2. When a review cycle is declared complete, copy/freeze that exact reviewed state under the next immutable `review/iterations/NNN/` directory.
3. A completed iteration SHALL NOT be edited to incorporate later design changes. Corrections discovered later belong in a new `review/current/` cycle.
4. After freezing an iteration, rebuild `review/current/` from the accepted baseline plus the next proposed changes.
5. Review iterations are provenance checkpoints, not release numbers.
6. Alpha, beta, release-candidate, and stable releases SHALL be promoted from a specific completed review iteration. A release SHALL record the source review iteration and commit/tag from which it was produced.
7. Do not create a release directly from an unreviewed or partially reviewed working tree merely because the implementation is functional.
8. Tools, tests, CI helpers, conversion scratch data, transition notes, and bulk source corpora SHALL remain outside the review surface.
9. New reviewable artifacts SHALL enter through `review/current/`; do not create parallel active review trees elsewhere in the repository.
10. Complete generated/compiled review products SHALL normally be published as GitHub Actions artifacts (or another explicitly approved non-Git evidence store) and referenced from the review set by the **full HTTPS URL** to the exact workflow run/artifact. Do not use only an artifact name or repository-relative path.
11. Do not recommit large generated products to Git solely for review. Git SHALL retain compact summaries, manifests, hashes/provenance, and small representative samples needed to understand the design.
12. A frozen `review/iterations/NNN/` checkpoint SHALL record the full artifact URL, artifact name, source commit, input pins, and validation status. It does not duplicate bulk generated artifacts into Git.
