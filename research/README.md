# SCAP-NG research and evidence

Start with the [visitor guide](../START-HERE.md), [current design](iterations/003/design/CURRENT-DESIGN.md) or [Board review packet](../board/README.md).

- Iteration 001: archived architecture prototypes, generated comparisons and original lessons/decision registers.
- Iteration 002: archived source-design experiments and 19 decision notes; some directions were superseded.
- Iteration 003: mixed current design, current generated review candidates, earlier slices and historical source/package snapshots. Read its [status guide](iterations/003/README.md) before selecting content.
- Datastream/vulnerability directories: retained topic research, not current implementation or source-generation acceptance evidence.

[Complete inventory](../docs/audit/repository-inventory.tsv.gz) · [Decision reconciliation](../docs/decision-reconciliation.md) · [Archives](../archive/README.md).

Original historical introduction follows; its iteration list is not the current navigation authority.

---

# SCAP Next Gen Research

This directory preserves R&D related to the creation of the SCAP next-generation specification and is intended to help future users understand **how and why** the specification was created.

Research is organized into numbered iterations so the directory root remains stable and earlier reasoning remains reviewable.

## Iterations

- `iterations/001/` — preliminary architecture discussion, controlled combined-vs-split prototypes, initial Windows/Linux result examples, stakeholder questionnaire, and decision register.

Each iteration should preserve:

- the architectural assumptions being tested;
- prototype content and corresponding results;
- relevant measurements/observations;
- reviewer questions and unmodified returned feedback;
- explicit decisions and unresolved requirements.

Reusable research/conversion utilities belong in the repository-level `tools/` directory rather than being copied into every iteration.
