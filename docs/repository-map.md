# Audited repository map

Baseline: `9751ef0e5ae43ab728876969ff59dad538a101f0`, 34,242 tracked files. The [machine-readable summary](audit/summary.json) and [compressed per-path inventory](audit/repository-inventory.tsv.gz) classify the complete pinned tree. About 82.6% (28,267 files) are historical artifacts. Another 5,302 are generated current review candidates. These are file counts, not a claim about how much Git history or compressed repository size deletion would save.

## One visible current route

| Visitor need | Current location | Important boundary |
| --- | --- | --- |
| Understand the project | [Start here](../START-HERE.md) | Pre-alpha, no released reference scanner |
| Review and vote | [Board packet](../board/README.md) | Individual versioned yes/no Discussions; no inferred ratification |
| Read working authority | [CURRENT-DESIGN](../research/iterations/003/design/CURRENT-DESIGN.md) | Latest owner corrections override historical proposals |
| Read proposed standard | [Specification](../specification/README.md) | Draft; unresolved details remain explicit |
| Inspect native schemas | [Schema](../schema/README.md) | Structural validation is not runtime equivalence |
| Browse complete source candidates | [RHEL 9 summary](../review/current/examples/rhel9-full.md), [Windows 11 summary](../review/current/examples/windows11-full.md) | Generated review candidates, not final grammar |
| Browse latest normalization | [Normalization evidence summary](../review/current/evidence/full-current-normalization.md) | Separate converter/normalizer evidence and handled errors |
| Run current tooling | [Tools guide](../tools/README.md) | Maintained helper imports remain active; old renderers are historical |
| Recover rationale/history | [Archives](../archive/README.md), [decision reconciliation](decision-reconciliation.md) | Preserve original decisions/questions and their dates |
| Resume in another interface | [Transition](../transition/README.md) | Verify current commit/access; conversation recovery is partial |

## What “active” means

An active entry point or its dependency is different from a current review snapshot, dated validation report, exploratory example or old experimental renderer. The inventory uses separate roles for those cases. It records 130 decision/design/specification source records separately from generated payloads. It does not label all iteration 003 current or all root tools maintained native generators.

The [dependency report](audit/dependencies.json) covers all workflow files, direct existing script paths and Python import edges. The closure is conservative static evidence. Dynamic imports, externally invoked scripts and data references require additional review. Supporting tools without a static current reference are retained rather than declared unused.

## Historical dependencies retained deliberately

- `data/oval-test-support-overrides.json`: current governance reinstatement input, promoted byte-for-byte from iteration 001.
- `data/public-corpus-manifest.yaml`: pinned source/corpus evidence, promoted byte-for-byte from iteration 001.
- `tools/validate_scap14_schema_bundle.py`: byte-identical promotion of the old vendored-schema validator. Current CI uses this root entry point; the original remains archived.
- Root `scap14_benchmark_ir.py` and `scap14_rule_splitter.py`: current helpers also used by historical pipelines.
- `build_rhel9_review_slice.py`: current lowerer helper despite an older filename; its older generator entry point is not the novice full-review command.
- Old fixture-driven semantic regressions can be useful evidence without making their generated layout current.

## Implemented cleanup and future design

The front door is now README → START-HERE → Board/current specification/tools, with archive and transition routes visibly separate. Generated review payloads have been removed from `main` after preservation/tagging and replacement with stable summaries; historical iterations 001/002 are preserved through the pre-rebaseline tag and indexed archive records. Twelve historical reproduction workflows have no automatic triggers and require a false-by-default manual opt-in. Three superseded v003 jobs remain held. A new boundary/preservation workflow validates the baseline and creates the preserved tag.

A later physical promotion to top-level `design/`, `examples/` and `evidence/` should use a verified relocation map and compatibility layer, then remove old aliases after consumers move. Bulk moving now would break recorded paths and risks losing active data hidden in old trees. The present rebaseline establishes that relocation/deletion evidence before any such action.

Known navigation defect repaired: the advertised RHEL 9 generated-directory README did not exist in the audited tree. The maintained guide is now outside that generated directory. Old instructions are retained as explicitly historical text or recoverable from the pinned baseline.

[Lossless method and future removal gates](lossless-rebaseline.md). Original feedback, source defects, open Board subquestions, third-party licenses and provenance remain available.
