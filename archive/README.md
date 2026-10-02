# Preserved research history

Historical bulk is no longer required to remain in the active working tree. The exact before-cleanup repository is pinned at commit `9751ef0e5ae43ab728876969ff59dad538a101f0` and tag `pre-rebaseline-2026-10-02`.

## Removed historical trees

| Historical area | Tree SHA | Files | Bytes | Recovery |
| --- | --- | ---: | ---: | --- |
| Iteration 001 | `6650989132f8cdaefb30355e83e1546474bb5262` | 14,419 | 432,868,747 | checkout from `pre-rebaseline-2026-10-02` |
| Iteration 002 | `b2debe70139467698bbed9f27d389e3c7a04ebea` | 10,816 | 424,276,360 | checkout from `pre-rebaseline-2026-10-02` |

Iteration 001 contained two inputs still required by current work. They were promoted byte-for-byte before removal:

- `specification/migration/oval-test-support-overrides.json`
- `tests/corpus-manifest.yaml`

All other iteration-001/002 prototypes, generated comparisons, decision notes, lessons, and review artifacts remain preserved in Git history/tag rather than duplicated in the active tree.

## Remaining historical material

Iteration 003 still contains mixed current design, focused evidence, and historical source/package material. It is being reduced selectively because some current design records and regression dependencies still live there.

The separate `vanderpol/scap-ng-evidence` repository is the durable home for migrated bulk evidence. The main repository retains compact summaries, provenance maps, and representative examples.

[Decision reconciliation](../docs/decision-reconciliation.md) · [Lossless rebaseline procedure](../docs/lossless-rebaseline.md)
