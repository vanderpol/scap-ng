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
- selected full benchmark examples used to demonstrate real-world coverage;
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
