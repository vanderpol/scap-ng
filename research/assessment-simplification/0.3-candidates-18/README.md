# 0.3.0 assessment-modernization candidate matrix

**Status:** research checkpoint only. This is an index, not a specification.

Tracking issue: #174. Every candidate semantic change is tracked by a GitHub issue before promotion.

| Candidate | Evidence | Current position | Remaining blocker before schema work |
| --- | --- | --- | --- |
| Consumer-local State (#165) | 858 top-level States -> 28 across RHEL 9 + Server 2025; all 28 survivors are unreachable | **Strong candidate**: State belongs with Test/Filter consumer | final inline syntax, lexical result/provenance identity |
| Consumer-local Object (#165) | 1,087 top-level Objects -> 98 with bounded locality | **Strong candidate**: Object local unless acquisition identity/reuse matters | classify/localize remaining Variable/Object-graph consumers; define shared-acquisition boundary |
| Bounded `foreach` (#164) | direct Object-component projection plus unary-literal-concat proof classes; exact graph desugaring | **Narrow candidate** | final syntax + schema/compiler prototype; keep converter opt-in initially |
| Named Variables (#169) | only 11.8% of representative Rules use Variables; many are plumbing | **Keep first-class** but expect fewer authored Variables | quantify survivors after locality + foreach + shared Observation extraction |
| Shared Observation artifact (#166) | Apache value export, Windows DomainRole Item export, and RHEL dconf mixed Item/value export all flatten exactly | **Strong candidate** | finalize input binding, Item/result provenance, manifest/cycle/cache rules |
| Evaluate / criteria structure (#167) | 72.3% of 1,350 representative Assessments have a trivial one-Test root; real trees reach depth 5 and repeat Test refs | **Keep named Tests + first-class composition** | owner review of authoring-only single-Test shorthand and summary-first placement |
| Conditional authoring (#173) | 19 clear environment/requirement cases, but generic six-state comparison differs in 81/216 combinations | **Native-authoring feature only** unless exact desugaring is defined | decide whether 0.3 needs a declarative case surface; no broad automatic rewrite |
| Persistent `linux.fstab` facts (#168) | 23 RHEL Assessments read fstab; live partition and persistent config are distinct | **Typed capability candidate** | collector/result semantics and conformance fixtures; no automatic graph collapse |
| Violation-query positive spelling | non-Boolean Filter results break ordinary positive equivalence | **Do not add semantic rewrite** | locality is sufficient; future shorthand only if it desugars to original graph |
| Alternative compliance paths | real production `any` cases | **Keep ordinary Boolean alternatives** | none |
| Generic Ansible-like parallel DSL | locality removes most ordinary indirection without changing semantic model | **Do not pursue as separate core language** | none unless later evidence changes |

## Immediate research order

1. Complete the exhaustive 65-package modernization census.
2. Use its residual-complexity statistics to re-measure named Variables and
   decide which candidates justify 0.3 schema work.
3. Finalize the small authoring core: consumer-local Object/State, bounded
   foreach, Observation, and retained evaluate composition.
4. Prepare compact before/after/counterexample examples for owner/Board review.

## Research exit criterion

Do not broaden the language merely to make the residual census smaller.

The modernization phase is ready to move into normative 0.3 schema/spec work
when the ordinary authoring model is coherent, every shorthand has a precise
semantic expansion or intentionally new native contract, and the remaining
complex graphs are demonstrably meaningful rather than serialization plumbing.
