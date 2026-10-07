# 0.3.0 assessment-modernization candidate matrix

**Status:** historical research checkpoint only. This is an index, not a specification.

> **Superseded for release scope:** final 0.3 IN / DEFER / OUT dispositions are maintained in [#174](https://github.com/vanderpol/scap-ng/issues/174), with the canonical deferred list in [`specification/deferred-after-0.3.md`](../../../specification/deferred-after-0.3.md). Candidate labels below record the state of the research at this checkpoint and do not override those later decisions.

Tracking issue: #174.

| Candidate | Evidence | Current position | Remaining blocker before schema work |
| --- | --- | --- | --- |
| Consumer-local State (#165) | Full corpus: 9,121 -> 435 top-level States (**95.23%** reduction) | **Strong candidate**: State belongs with its consumer unless reuse requires identity | final inline syntax and result/provenance identity |
| Consumer-local Object (#165) | Full corpus: 13,402 -> 1,197 top-level Objects (**91.07%** reduction) | **Strong candidate**: Object local unless acquisition identity/reuse matters | finalize syntax and shared-acquisition boundary |
| Bounded `foreach` (#164) | Full corpus exact v1: **22 / 6,916 Rules (0.32%)** rewritten; 200 direct projections refused/reviewed | **Narrow candidate** | classify residual Variable patterns before broadening |
| Named Variables (#169) | Full corpus: 2,250 -> 2,002 (**11.02%** reduction); first pass flagged 1,073 complex Rules, but follow-up shows many are external inputs/constants rather than derived dataflow | **Keep first-class for real dataflow; refine input/constant scope** | classify source kind, function, fan-out and chaining before final scope decision |
| Shared Observation artifact (#166) | Full corpus: **9** package artifacts, **69** consumers; Apache values, Windows DomainRole Items, RHEL/OL9 dconf mixed exports | **Strong candidate** | finalize input binding, Item/result provenance, manifest/cycle/cache rules |
| Evaluate / criteria structure (#167) | Full corpus: **4,740 / 6,916 (68.5%)** Rule roots are trivial single-Test; 147 repeat Test refs | **Keep named Tests + first-class composition** | owner review of authoring-only single-Test shorthand and summary-first placement |
| Conditional authoring (#173) | 19 clear environment/requirement cases, but generic six-state comparison differs in 81/216 combinations | **Native-authoring feature only** unless exact desugaring is defined | decide whether 0.3 needs a declarative case surface; no broad automatic rewrite |
| Persistent `linux.fstab` facts (#168) | 23 RHEL Assessments read fstab; live partition and persistent config are distinct | **Typed capability candidate** | collector/result semantics and conformance fixtures; no automatic graph collapse |
| Violation-query positive spelling | non-Boolean Filter results break ordinary positive equivalence | **Do not add semantic rewrite** | locality is sufficient; future shorthand only if it desugars to original graph |
| Alternative compliance paths | real production `any` cases | **Keep ordinary Boolean alternatives** | none |
| Generic Ansible-like parallel DSL | locality removes most ordinary indirection without changing semantic model | **Do not pursue as separate core language** | none unless later evidence changes |

## Immediate research order

1. **Deep-dive the 1,073 complex Rules with nontrivial Variable graphs.** Classify
   which flows are semantically necessary versus repeatable authoring plumbing.
2. **Review the 630 complex Set/Filter Rules** after Variable classification;
   avoid adding syntax merely to reduce the residual count.
3. **Finalize the small authoring core:** consumer-local Object/State, bounded
   foreach, Observation, and retained evaluate composition.
4. Prepare compact before/after/counterexample examples for owner/Board review.

## Research exit criterion

Do not broaden the language merely to make the residual census smaller.

The modernization phase is ready to move into normative 0.3 schema/spec work
when the ordinary authoring model is coherent, every shorthand has a precise
semantic expansion or intentionally new native contract, and the remaining
complex graphs are demonstrably meaningful rather than serialization plumbing.
