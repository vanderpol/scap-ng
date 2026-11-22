# Issue #87 conformance gap matrix

This matrix separates authoring/schema proof, independent semantic-oracle proof,
and runtime qualification. It is intentionally falsifiable; green schema gates
do not imply scanner equivalence.

| Issue #87 requirement | Current evidence | Status / remaining gap |
| --- | --- | --- |
| Exact canonical 0.4.1 pin and closure | `manifest.json`, 145-resource digest, source `860d63e...` | **Proved for the pinned branch**; current `main` drift is a repinning hold and must not be silently mixed. |
| Exhaustive schema/mapping inventory | `schema-coverage.json`, 104 mappings, fields, enums, constraints, refs | **Proved as inventory**; occurrence-level executable semantic coverage is not claimed. |
| Schema-valid Assessment per active capability | 104 generated Assessments; offline Draft 2020-12 validation | **Proved structurally**; collector support/runtime semantics unproved. |
| Field coverage | Source mappings → authored positive Assessments → positive fixtures: 710/710/710 | **Proved structurally and witness-linked**. |
| Comparison operators | Source language → authored operator suite: 67/67 | **Proved as typed schema-valid witnesses**; independent runtime operator behavior remains unqualified. |
| Selector alternatives | Source mappings → authored selector suite: 94/94, no duplicate/missing witnesses | **Proved structurally**; enum boundaries and acquisition behavior remain open. |
| Cardinality layers | All five cardinality tokens; Model A oracle covers Item/field/value folds | **Proved for approved Model A domain**; empty/indeterminate population semantics remain open. |
| Variable/Evaluate/Require interactions | Core Evaluate suite plus independent 15-case Model A oracle | **Partially proved**: known nonempty integer/string equality and aliases; broader functions, datatypes, and rollups remain open. |
| FALSE/UNKNOWN/ERROR/NOT_APPLICABLE/NOT_EVALUATED | Typed fixtures/status Assessments and strict receipt outcome checks | **Authoring/status witness proved**; canonical propagation precedence is not complete and requires normative/runtime qualification. |
| Disabled/profile behavior | Schema-valid Benchmark/Profile/Tailoring witnesses | **Policy structure proved**; scanner application and result accounting remain unqualified. |
| Enum/constraint boundaries | Selector sentinel mutation audit; capability semantic-validator inventory | **Partial**: only schema-backed selector sentinel rejection is exercised; 141 enum nodes and 10,960 constraint occurrences need targeted boundary families. |
| Deterministic evidence/replay | Fixed clock/locale/order, hashes, fixture-linked strict receipts | **Proved for portable fixtures**; real-host evidence is excluded. |
| Independent expected-result justification | Separate expected documents, strict oracle, Model A oracle, adversarial regressions | **Proved for documented scopes**; no RI output is treated as oracle input. |
| Platform/capability execution | Capability mappings and source witnesses | **Unproved**; scanner-neutral execution belongs to RI #196. |
| Scale/concurrency (100K/1M Items) | None | **Unproved**, evidence issue #3 / RI execution work. |
| Independent multi-scanner corroboration | None | **Unproved**, intentionally excluded from this repository increment. |

## RI #196 handoff requirements

An RI adapter must consume the exact manifest and selected fixture variant,
execute the authored Assessment without rewriting it, and emit a receipt that
passes `conformance/tools/oracle.py`. The receipt must bind schema commit,
fixture/expected hashes, exact Test outcome keys, typed evidence, decisive reason,
and provenance. It must report unsupported acquisition, incomplete/error/unknown
status, permission boundaries, resource limits, and cancellation explicitly.
A passing schema or portable oracle check alone is never an RI execution receipt.
