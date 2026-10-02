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

## Generated review products

Complete converted Benchmarks, compiled `.scapng` packages, corpus-wide reports, and other large generated review products are **CI artifacts**, not repository source. Each review entry SHALL include the **full HTTPS URL** to the exact GitHub Actions workflow run/artifact, plus the artifact name, source commit, pinned inputs, and a compact validation summary. Do not use only a relative repository link or artifact name.

Small representative source/examples belong in Git. Large generated products do not. A completed review iteration freezes the full artifact URL and provenance rather than copying the artifact back into Git.

Example current full-corpus run: https://github.com/vanderpol/scap-ng/actions/runs/37004465863

## Iterations

Previous review/design states belong under [`../iterations/`](../iterations/). They are preserved for traceability and comparison. The `current/` directory always identifies the single review set we presently want external reviewers to examine.
