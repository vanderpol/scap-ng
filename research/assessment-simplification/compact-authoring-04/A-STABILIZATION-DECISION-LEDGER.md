# 0.4-A consolidation — what is proven, what is still a choice

**18 October 2026 · Research review, not approval or a new specification.**  
**Goal:** stabilize **one** 0.4-A Assessment authoring grammar, then build its native compiler. Do not start another language proposal or extend the Linux scanner spike before the contract is selected.

## Verified baseline

- [Corrected six-STIG r3 authoring release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-joval-meeting-preview-20261015-r3): six source-backed sets in YAML/JSON; all **2,958 Rule choice** links resolve.
- [Independent JSON-only source and schema check](https://github.com/vanderpol/scap-ng/actions/runs/38830995691): **4,001 documents, 1,567 Rules, 2,422 Assessment IDs, 872 distinct automated Assessments, 1,375 distinct Tests**. The 1,396 Assessment / 2,144 Test figures are *per-benchmark occurrences* and must never be substituted for unique documents.
- [Source reconstruction ledger](CONFORMANCE-STATUS-2026-10-15.md): **1,384 source-exact** parsed Assessment reconstructions; **12** State-free, reference-model-equivalent cases separately classified. This is **not** a scanner result or proof of OVAL runtime equivalence.
- [Six-state boundary tests](INCOMPLETE-ITEM-SEMANTICS-REVIEW.md) caught actual incorrect shortcuts for incomplete collections. Schema/round-trip equivalence alone is insufficient.

## Carry forward into 0.4-A (evidence-supported; adoption status matters)

| Candidate | Current evidence | Promotion status / needed decision |
| --- | --- | --- |
| **Single grammar** with observed field-name State keys and comparator-as-key, including Object selectors | Version-local [0.4 Assessment schema](../../../schema/v0.4.0/assessment.schema.json), 100 native capability schemas, source inversion fixtures (#227, #228) | **Base draft exists**; retain one syntax, not parallel English/OVAL authoring grammars |
| **Explicit distinct Item and field requirements** | Real RHEL `/home` `nosuid` uses Item `at_least_one_exists_and_all_match` but option-field `at_least_one_exists_and_some_match`; record/member rules remain distinct | **Meaning essential**, exact human wording not finally reviewed |
| **Scoped State-field requirement inheritance** and `and/or` aliases | [Six-STIG candidate CI](https://github.com/vanderpol/scap-ng/actions/runs/38808020283): 2,550 declarations reduced to 1,444, 1,106 saved; reversible structural proofs, plus 512 bounded scope combinations | **Research overlay only**; requires owner approval and explicit negative/record inheritance tests |
| **Test key `collected_items_require`** (r3) rather than base draft `require` | [#227](https://github.com/vanderpol/scap-ng/issues/227): candidate separates Test population from `state_fields_require`; r3 validates through expansion, not directly against unchanged base syntax | **Unresolved source-of-truth naming conflict. Decide before compiler freeze.** |
| **Common/exact-one requirement names** | [One-grammar research](ONE-GRAMMAR-DECISION.md) reconstructs pinned pairs, including State-free `only_one_exists` vs State-bearing `only_one_exists_and_matches` | **Likely keep semantics**, review rare negatives instead of approving all mechanically composed names |
| **Named Variables, optional build-time source reuse** | [#223](https://github.com/vanderpol/scap-ng/issues/223): Apache 11-Variable reuse module expands identically in 15 Assessments, reducing 154 duplicate declarations in experiment | **Promising non-runtime authoring optimization**, not yet generic parser/import contract; no claim of faster scanning |
| **`for_each`, Set/filter, Windows record and evaluation graphs** | Source-backed six-STIG structural examples and [#229](https://github.com/vanderpol/scap-ng/issues/229) fixture matrix | **Preserve source graphs** unless each rewrite has independent six-outcome semantic proof |
| **Procedural `if/then/else` substitution** | The [conditional study](ASSESSMENT-REVIEW-OVERVIEW.md) differs from source `OR(AND(G,P),AND(NOT G,Q))` in **81/216** generic three-input outcome combinations | **Not safe as a generic source rewrite**. Keep original Boolean expressions |
| **More English-first / B / Gemini-inspired grammar changes** | [#235](https://github.com/vanderpol/scap-ng/issues/235), [#236](https://github.com/vanderpol/scap-ng/issues/236) | **Defer until A stabilizes**; use tested insights only, no second language |

## One concrete source-preservation trap

For the RHEL 9 `/home` mount check, *all selected mount Items* must satisfy the State, while *some observed mount-option values within each Item* must equal `nosuid`. Treating both as a generic `all` quantifier silently changes compliance. Also preserve the original selector regex rather than tightening it during conversion. [Exact A-source comparison](../english-first-04/FULL-01-linux-home.md).

## Execution order / real product path

1. **Resolve the small number of actual grammar decisions** with the owner: base Test `require` versus r3 `collected_items_require`, explicit scoped inheritance, uncommon requirement names, and what is a real conditional rewrite. A decision must cite a full source-backed before/after, not only a pretty YAML excerpt.
2. **Promote only approved behavior** to the self-contained `schema/v0.4.0` draft and validators (#227/#228/#229), including negative tests for hidden defaults, incomplete evidence, duplicate/absent record data and incompatible structures.
3. **Finish independent native 0.4 YAML-only and JSON-only authoring-to-bundle compilation (#232)**. Build identical normalized graphs and deterministic manifests with all Rule/Assessment/shared references, explicit version handling and failures closed; then test the full six-STIG set. No signed result/scanner parity claim from this alone.
4. **Only then resume scanner engineering** (#238) and broaden the Linux prototype; the [focused live Linux check](https://github.com/vanderpol/scap-ng/actions/workflows/research-a-linux-mount-execution.yml) is a bounded feasibility spike, *not* the 0.4 release gate. Runtime provider/OVAL semantics and six-state parity are separate later tests.

**This page tracks the stabilization path**, not another research competition. Project gate: [#239](https://github.com/vanderpol/scap-ng/issues/239); native compiler: [#232](https://github.com/vanderpol/scap-ng/issues/232); semantic acceptance: [#229](https://github.com/vanderpol/scap-ng/issues/229).
