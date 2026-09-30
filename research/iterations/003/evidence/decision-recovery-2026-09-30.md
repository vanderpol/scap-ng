# Decision recovery and implementation reconciliation — 2026-09-30

**Status: recovery checkpoint; not a claim of exhaustive transcript recovery.**

Generation is paused while decisions and implementation are reconciled. This audit used visible owner corrections, targeted recovery of September 29–30 discussions, and direct inspection of committed design records and code. Search returned partial conversation evidence and some conflicting assistant descriptions. Assistant completion claims are not proof; missing evidence is recorded below rather than filled by inference. The external coworker redesign draft is not authority for our accepted design.

The current working contract is [CURRENT-DESIGN.md](../design/CURRENT-DESIGN.md). Older files that conflict with it are superseded on those points. Board ratification, owner working agreement, implemented syntax and validated behavior are separate statuses.

| Decision or requirement | Recovered authority | Repository/code finding | Disposition |
| --- | --- | --- | --- |
| Replace Policy objects with Rules; common compliance/vulnerability architecture | September 29 owner-directed 003 update; September 30 direct correction | Old split-policy generator and design guidance revived the obsolete layer | Slice corrected; guidance corrected; old workflow disabled |
| Rule owns named Assessment selection/default | Architecture correction and selector decisions | Slice now owns choices directly on Rule | Retain selector identities; proposed field names still under review |
| Explicit relative Assessment source paths; no hand-maintained index | September 30 owner acceptance, 14:12 UTC recovery | Slice resolves paths from Rule; old full tree uses IDs | Full generator migration unfinished |
| Compiled resolution uses manifest binding, not filename guessing | Same source-resolution decision | Source slice is not a compiled package | Preserve downstream distinction |
| No native `deprecated` attribute | September 30 owner correction | Stale generated baseline contained `deprecated: false` | Slice stripped; negative guards added |
| Effective deprecated OVAL Tests reject conversion | Existing owner requirement and AGENTS.md | Existing support audit and diagnostics retained | Must remain in full-regression gates |
| Native automated nodes are Tests with searchable IDs | September 30 direct feedback | Slice has `tests`, `test_title`, `test-` IDs | Narrow naming tests pass |
| Native acquisition term is Collection; Object is source terminology | September 29 acceptance recovered; September 30 direct feedback | `collect`, `object_title`, `object_values` remain in generated authoring | Readiness blocker; not fixed by mere Test rename |
| Variable may reference an existing Collection **or embed one** | September 29 owner decision recovered at 18:58 UTC; September 30 direct reconfirmation | Existing variable-dataflow document described both but weakly labeled support an idea | Both required in working design; status corrected |
| Embedded Collection is private; shared Collection stays named | Same discussion; source conversion contract | Lowering embeds Object payload for every object component | Named-reference implementation is a blocker |
| Preserve authored Object/Variable boundaries in lossless conversion | conversion-contract.md and September 29 discussion | Inline copies can erase original sharing; missing identity cannot safely be recovered by payload deduplication | Fix from original source graph/faithful IR, not stale YAML |
| Functions may nest inside named Variables; referenced intermediates become named | September 29 owner acceptance, 18:52 UTC recovery | Variable expressions and chains are partly lowered | Preserve both compact and breadcrumb authoring forms |
| One Test capability for directly associated Collection/State; mismatch rejects | September 30 owner acceptance, 16:45 UTC recovery | Direct mismatch guards exist; authoring still repeats capability | Syntax migration incomplete; Variable-only Collection typing needs explicit resolution |
| No three-layer language depth limit | Variable-depth discussion and variable-dataflow.md | Accounting iterative; native lowering still recursive with resource diagnostic | Distinguish language from host resource limits; #38 remains open |
| Variables, sets, filter States and object components must all participate in dependency closure | September 29–30 discussions and existing reports | Recent guards/accounting exist | Neither closure accounting nor successful round trip proves full runtime semantics |
| Hidden defaults become explicit only from authoritative schema/semantic sources | September 29–30 audit direction | Structural named-type resolution report exists; behavioral defaults still open | Do not conflate structural audit with evaluator conformance |
| Source Test `check` is required; never default missing value to `all` | Recovered corrective work; inspected lower_test | Missing attribute returns diagnostic | Retain as source-validity guard |
| Semantic equivalence, not byte-identical XML; classify noisy diffs | September 30 owner acceptance, 15:09 UTC recovery | Existing round-trip work separates some categories | Full round trip after grammar/default changes remains necessary |
| Profile audit across all 445 RHEL9 Rules; preserve explicit/default provenance | September 30 owner request, Issue #30 | Prior assistant claimed 445×11 comparison pass; not independently revalidated in this recovery | Treat prior pass as reported evidence, not new audit proof |
| Test/State existence scopes, item meaning, final quantifier name | September 30 discussion and terminology-review.md | Repository proposes `state_match`; slice instead uses `item_quantifier` | Exact final owner-approved wording not reliably recovered; do not declare either settled |
| Benchmark declares NG schema version; placement/inheritance | Visible earlier owner request | Benchmark currently has null version placeholder | Declaration required; precise agreed placement/version needs further evidence |
| Reviewer-first titles before detailed State predicates | September 30 owner feedback and code comments | Baseline multi-State payload ordering and regeneration disagree in places | Guard full output, not just source dictionary insertion order |
| Pre-alpha publication directly to main without recurring permission questions | Repeated direct owner instruction | Stored in AGENTS.md | Retain |

## New preflight result

Three preflight-tool regressions pass. The tool intentionally rejects the current slice with five stale-vocabulary findings across two automated Assessments. The prior fifteen narrow tests remain narrower evidence; they did not cover named Collection dataflow or full native syntax. `readiness.json` records **blocked**, not ready.

The preflight is a small negative guard, not a complete NG schema, graph-sharing verifier or evaluator. It must be expanded with actual accepted grammar and variable/reference regressions before full authoring review.

## Recovery limits and follow-through

This checkpoint does not prove every decision from the last day has been retrieved. Remaining reconciliation includes final quantifier wording, schema-version scope, runtime result and applicability decisions, full selector/profile semantics, and other Board proposals. Do not ask the owner to redesign settled features merely because retrieval is incomplete. Recover supporting records first and explicitly identify an irrecoverable gap if one remains.

No full benchmark regeneration, scanner implementation or replacement architecture was performed during this recovery. Existing research is retained. Source corrections must use pinned originals; the snapshot vocabulary transformer is not a replacement for the source converter.

Provenance: **Evidence/Audit**, based on recovered discussion summaries (not verbatim transcripts), directly visible owner corrections, repository contracts and inspected code. No external draft content was used to establish acceptance.
