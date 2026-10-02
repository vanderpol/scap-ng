# SCAP-NG research and evidence

Start with the [visitor guide](../START-HERE.md), [current design](iterations/003/design/CURRENT-DESIGN.md) or [Board review packet](../board/README.md).

- Iterations 001 and 002 were removed from the active working tree during the lossless rebaseline. Their exact trees remain available from tag `pre-rebaseline-2026-10-02` and are indexed in `archive/README.md`.
- Iteration 003: mixed current design, current generated review candidates, earlier slices and historical source/package snapshots. Read its [status guide](iterations/003/README.md) before selecting content.
- Datastream/vulnerability directories: retained topic research, not current implementation or source-generation acceptance evidence.

[Complete inventory](../docs/audit/repository-inventory.tsv.gz) · [Decision reconciliation](../docs/decision-reconciliation.md) · [Archives](../archive/README.md).

Original historical introduction follows; its iteration list is not the current navigation authority.

---

# SCAP Next Gen Research

This directory preserves R&D related to the creation of the SCAP next-generation specification and is intended to help future users understand **how and why** the specification was created.

Research is organized into numbered iterations so the directory root remains stable and earlier reasoning remains reviewable.

## Iterations

- Historical iterations 001/002 are no longer carried in the active working tree; use the preserved tag and archive index for those materials.

Each iteration should preserve:

- the architectural assumptions being tested;
- prototype content and corresponding results;
- relevant measurements/observations;
- reviewer questions and unmodified returned feedback;
- explicit decisions and unresolved requirements.

Reusable research/conversion utilities belong in the repository-level `tools/` directory rather than being copied into every iteration.
