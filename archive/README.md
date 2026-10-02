# Preserved research history

No historical payload has been deleted or relocated in this rebaseline. Existing links, source fixtures, evidence, feedback and generated experiments retain their original paths.

The exact before-cleanup tree is pinned at commit `9751ef0e5ae43ab728876969ff59dad538a101f0`. The preservation workflow establishes tag `pre-rebaseline-2026-10-02` and refuses to overwrite a different target. Check the [preservation workflow](https://github.com/vanderpol/scap-ng/actions/workflows/repository-boundaries.yml) before relying on the tag.

| Historical area | What is retained | How to use it |
| --- | --- | --- |
| [Iteration 001](../research/iterations/001/README.md) | Combined/split/Ansible-inspired prototypes, source conversion, reuse evidence, lessons, original decision register and reviewer questions | Design history and pinned experiment evidence |
| [Iteration 002](../research/iterations/002/README.md) | Source-model experiments, 19 decision notes and generated comparisons | Reconcile each decision with the latest working design |
| [Iteration 003 source](../research/iterations/003/source/) and [packages](../research/iterations/003/packages/) | Superseded full-generation and separate-Policy experiments | Historical baseline; current review candidates are under iteration-003 `review/` |
| [Earlier focused reviews](../research/iterations/003/review/) | Dataflow, terminology and diagnostic slices alongside current full reviews | Read the individual status; earlier slices are not latest-grammar acceptance evidence |
| [Historical tools](../docs/audit/dependencies.json) | Older renderers, runners and workflow relationships | Explicit historical reproduction only; maintained shared helpers remain active |

[Complete per-path inventory](../docs/audit/repository-inventory.tsv.gz) · [Decision reconciliation](../docs/decision-reconciliation.md) · [Lossless rebaseline procedure](../docs/lossless-rebaseline.md)

An archived location does not make every file obsolete. The OVAL support override ledger, corpus manifest and vendored-schema validator at iteration-001 paths remain support inputs and are recorded as exceptions. Neither those inputs nor source licenses may be removed merely because surrounding generated material is historical.
