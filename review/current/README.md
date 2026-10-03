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

The [Assessment reference](../../specification/assessment/reference/README.md)
now provides shared behavior and initial `unix.file`/`variable.value` field
guides. It remains incomplete; its examples distinguish structural/synthetic
evidence from target execution, and 0.2.0 is still a partial draft.

## Review boundary

Reviewers should judge the design from the material above, not from old generators, superseded renderers, historical prototypes, transition notes, or helper scripts.

Reproduction tooling remains available under `../../tools/`, but tooling is deliberately outside the review surface. A tool's location, age, or passing tests do not make its emitted syntax normative.

## Generated review products

Complete converted Benchmarks, compiled `.scapng` packages, corpus-wide reports, and other large generated review products are **CI artifacts**, not repository source. Each review entry SHALL include the **full HTTPS URL** to the exact GitHub Actions workflow run/artifact, plus the artifact name, source commit, pinned inputs, and a compact validation summary. Do not use only a relative repository link or artifact name.

Small representative source/examples belong in Git. Large generated products do not. A completed review iteration freezes the full artifact URL and provenance rather than copying the artifact back into Git.

## Full NIWC Current review build

- Workflow run: https://github.com/vanderpol/scap-ng/actions/runs/37083265100
- Artifact name: `niwc-current-full-review`
- Direct artifact download: https://github.com/vanderpol/scap-ng/actions/runs/37083265100/artifacts/11260426828
- Result: **success**. 65 source packages accounted for; 63 native Benchmarks and compiled bundles; 2 source/conversion blockers retained in evidence. Schema, Assessment graph and package graph checks report zero invalid documents/graphs before and after normalization.
- SCAP-NG source commit: `5acbd67af155668440615b0d6b1f6412805caa10`
- Pinned NIWC source revision: `8c8e5dff860af6b1290ee9273a282db24278f8d5`
- Scope: all 65 pinned NIWC Current SCAP 1.4 packages are accounted for. Successfully converted packages are included under `source/`, exact-semantics normalized trees under `normalized/`, compiled readable bundles under `packages/`, and blocked-package/validation/provenance details under `evidence/`.

The workflow run above is the canonical download location for this review cycle. Open the run and download the `niwc-current-full-review` artifact.


## Iterations

Previous review/design states belong under [`../iterations/`](../iterations/). They are preserved for traceability and comparison. The `current/` directory always identifies the single review set we presently want external reviewers to examine.
