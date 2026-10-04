# Repository map

This is the concise map of the current `scap-ng` repository. Historical paths are preserved for traceability, but current authority is deliberately narrow.

## Current route

| Need | Go to |
| --- | --- |
| Understand SCAP-NG | [START-HERE](../START-HERE.md) |
| See SCAP 1.4 → NG changes | [Board key changes](../board/SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md) |
| Review 0.2.0 / Board material | [Board packet](../board/README.md) |
| Read current design authority | [CURRENT-DESIGN](../research/iterations/003/design/CURRENT-DESIGN.md) |
| Read draft normative text | [Specification](../specification/README.md) |
| Inspect schemas/mappings | [Schema](../schema/README.md) |
| Review current examples/evidence | [Current review set](../review/current/README.md) |
| Run tools locally | [Human-runnable tools](../tools/HUMAN-RUNNABLE-SCRIPTS.md) |
| Change semantics safely | [MAINTAINING](../MAINTAINING.md) |
| Resume across ChatGPT/Codex | [Transition](../transition/README.md) |
| Recover older research | [Archive](../archive/README.md) |

## Directory roles

- `board/` — current Board briefing, review samples, proposals, and vote links.
- `review/current/` — curated external-review summaries/evidence.
- `specification/` — draft normative model and migration/crosswalk material.
- `schema/` — versioned native schemas and reviewed capability mappings.
- `tools/` — maintained CLIs plus internal/research helpers; see the human tool catalog before running unfamiliar scripts.
- `tests/` — focused regression/conformance fixtures.
- `research/` — design rationale and dated evidence; older iterations are not current authority.
- `transition/` — freeze/handoff/continuity records, including dated historical checkpoints.
- `archive/` — preserved historical indexes/artifacts.
- `docs/audit/` — machine-generated repository/dependency inventories and audit evidence.

## Authority rule

Latest explicit owner direction and the current design/specification override historical renderers, old generated examples, dated transition notes, and earlier experimental architectures. In particular, the current model is **Benchmark → Rule → Assessment**, not the older split-Policy design.

Passing old tests or finding a script in `tools/` does not make its syntax current. Consult [`tools/HUMAN-RUNNABLE-SCRIPTS.md`](../tools/HUMAN-RUNNABLE-SCRIPTS.md) for supported human entry points.

Detailed preservation/dependency inventories remain under `docs/audit/`; they are evidence, not the recommended navigation surface.
