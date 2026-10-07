# 0.3.0 assessment-modernization candidate matrix

**Status:** research checkpoint only. This is an index, not a specification.

Tracking issue: #174. Every candidate semantic change is tracked by a GitHub issue before promotion.

| Candidate | Evidence | Current position | Remaining blocker before schema work |
| --- | --- | --- | --- |
| Consumer-local State (#165) | 858 top-level States -> 28 across RHEL 9 + Server 2025; all 28 survivors are unreachable | **Strong candidate**: State belongs with Test/Filter consumer | final inline syntax, lexical result/provenance identity |
| Consumer-local Object (#165) | 1,087 top-level Objects -> 98 with bounded locality | **Strong candidate**: Object local unless acquisition identity/reuse matters | classify/localize remaining Variable/Object-graph consumers; define shared-acquisition boundary |
| Bounded `foreach` (#164) | direct Object-component projection plus unary-literal-concat proof classes; exact graph desugaring | **Narrow candidate** | final syntax + schema/compiler prototype; keep converter opt-in initially |
| Named Variables (#169) | only 11.8% of representative Rules use Variables; many are plumbing | **Keep first-class** but expect fewer authored Variables | quantify survivors after locality + foreach + shared Observation extraction |
| Shared Observation artifact (#166) | Apache proof extracts identical 4-Object + 11-Variable discovery graph from 15 Rules; only 2 exports needed | **Promising candidate** | define Observation schema, typed exports, status/completeness/provenance, consumer binding, package/result type |
| Evaluate / criteria structure (#167) | 72.3% of 1,350 representative Assessments have a redundant one-Test root; 4.5% have depth > 2 | **Strong review candidate**: composition tree remains necessary, mandatory trivial root is questionable | compare implicit single-Test root, nested/local composition, Test-result identity, and source placement |
| Conditional authoring (#173) | 19 clear environment/requirement cases, but generic six-state comparison differs in 81/216 combinations | **Native-authoring feature only** unless exact desugaring is defined | decide whether 0.3 needs a declarative case surface; no broad automatic rewrite |
| Persistent `linux.fstab` facts (#168) | 23 RHEL Assessments read fstab; live partition and persistent config are distinct | **Typed capability candidate** | collector/result semantics and conformance fixtures; no automatic graph collapse |
| Violation-query positive spelling | non-Boolean Filter results break ordinary positive equivalence | **Do not add semantic rewrite** | locality is sufficient; future shorthand only if it desugars to original graph |
| Alternative compliance paths | real production `any` cases | **Keep ordinary Boolean alternatives** | none |
| Generic Ansible-like parallel DSL | locality removes most ordinary indirection without changing semantic model | **Do not pursue as separate core language** | none unless later evidence changes |

## Immediate research order

1. **Finish Object/Variable locality.** Classify the 98 surviving Objects by
   exact consumer shape. Test private Object placement inside Variables and
   other graph consumers only where re-expansion is exact.
2. **Specify Observation semantics.** Use Apache as the proving case: truthless
   producer, typed exports, status/completeness/provenance, explicit consumer
   reference, and a standalone Observation result.
3. **Re-measure named Variables.** After locality/Observation/`foreach`, count
   which Variables still have independent identity or nontrivial dataflow.
4. **Prototype the small 0.3 authoring core.** Consumer-local Object/State plus
   the narrow proven `foreach` classes; preserve a faithful graph form.
5. **Prepare one compact human-review packet.** For every proposed feature:
   one same-definition before/after example, one refusal/counterexample, measured
   coverage, and explicit migration status.

## Research exit criterion

Do not broaden the language merely to make the residual census smaller.

The modernization phase is ready to move into normative 0.3 schema/spec work
when the ordinary authoring model is coherent, every shorthand has a precise
semantic expansion or intentionally new native contract, and the remaining
complex graphs are demonstrably meaningful rather than serialization plumbing.
