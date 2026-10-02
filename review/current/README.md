# Current SCAP-NG review set

**Status: pre-alpha working design.**

This directory is the canonical navigation point for the material reviewers should evaluate together.

Until the lossless repository rebaseline is complete, the current review set links to authoritative files that still live at their existing paths. Those files will be consolidated here only after dependency and preservation checks show that moving them cannot lose history or break reproducibility.

## Read in this order

1. [SCAP-NG overview and visitor guide](../../START-HERE.md)
2. [Current design contract](../../research/iterations/003/design/CURRENT-DESIGN.md)
3. [Draft specification](../../specification/README.md)
4. [Native schemas and mappings](../../schema/README.md)
5. [OVAL Board review and voteable proposals](../../board/README.md)
6. Current complete examples:
   - [RHEL 9 full-review summary](examples/rhel9-full.md)
   - [Windows 11 full-review summary](examples/windows11-full.md)
7. [Full-current normalization evidence summary](evidence/full-current-normalization.md)

## Review boundary

Reviewers should judge the design from the material above, not from old generators, superseded renderers, historical prototypes, transition notes, or helper scripts.

Reproduction tooling remains available under `../../tools/`, but tooling is deliberately outside the review surface. A tool's location, age, or passing tests do not make its emitted syntax normative.

## Iterations

Previous review/design states belong under [`../iterations/`](../iterations/). They are preserved for traceability and comparison. The `current/` directory always identifies the single review set we presently want external reviewers to examine.
