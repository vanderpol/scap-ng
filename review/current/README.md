# Current SCAP-NG review set

**Status:** pre-alpha 0.2.0 working design under human/OVAL Board review.

This directory is the navigation point for material external reviewers should evaluate together.

## Read in this order

1. [SCAP 1.4 → SCAP-NG key changes](../../board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md)
2. [0.2.0 Board review checkpoint](../../board/SCAP-NG-0.2.0-REVIEW-CHECKPOINT.md)
3. [Six small source-to-NG Board examples](../../board/review-content/0.2.0/README.md)
4. [Draft specification](../../specification/README.md)
5. [Current design contract](../../research/iterations/003/design/CURRENT-DESIGN.md)
6. [RHEL 9 full-review summary](examples/rhel9-full.md)
7. [Windows 11 full-review summary](examples/windows11-full.md)
8. [Full-current normalization evidence](evidence/full-current-normalization.md)

## Review boundary

Judge the current design from the material above, not from superseded iteration-001/002 renderers, old split-policy experiments, historical generated trees, or helper-script output taken out of context.

Reproduction tooling is under [`tools/`](../../tools/). Tool location or a passing test does not make emitted syntax normative. Human operators should use the [human-runnable tools guide](../../tools/HUMAN-RUNNABLE-SCRIPTS.md).

## 0.2.0 checkpoint

Technical schema baseline: `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

The six-case converter-produced Board pilot is present and validated, but remains pending human acceptance. Full corpus, round-trip, schema, and known-result evidence are supporting evidence rather than proof of independent scanner/live-target equivalence.

Large converted benchmarks and corpus-wide deliverables may be retained as CI artifacts with pinned source/provenance; small representative examples belong in Git.

Previous review/design states remain under [`review/iterations/`](../iterations/) and historical research paths for traceability.
