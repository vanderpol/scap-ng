# Deferred beyond SCAP-NG 0.3

**Status:** authoritative scope boundary for the 0.3 OVAL Board checkpoint.

The 0.3 requirement set is maintained in [#174](https://github.com/vanderpol/scap-ng/issues/174). This page lists work that remains valuable but is **not normative 0.3 language/runtime**.

## Deferred semantic/runtime work

| Item | 0.3 boundary | Why deferred |
| --- | --- | --- |
| [#166 Shared Observation](https://github.com/vanderpol/scap-ng/issues/166) | No normative Observation artifact/export/result contract in 0.3. | Production value is proven, but typed exports, execution/result provenance, binding identity, manifest dependency/cycle handling, and cache/reuse semantics need a complete interoperable contract. |
| [#168 Typed `linux.fstab` capability](https://github.com/vanderpol/scap-ng/issues/168) | Existing faithful checks remain; no new persistent-mount capability in 0.3. | Useful native capability, but domain-specific and requires its own collection/order/duplicate/completeness/result semantics. |
| [#175 Organizational Input instance targeting](https://github.com/vanderpol/scap-ng/issues/175) | Organizational Input supplies expected policy State only; database/site/product-instance routing remains outside core 0.3. | Portable cross-product targeting semantics are not yet demonstrated. |
| [#44 Broad Assessment composition/runtime collection reuse](https://github.com/vanderpol/scap-ng/issues/44) | No general cross-Assessment import/include/runtime-cache language in 0.3. | Binding, execution DAG, cache identity, short-circuiting, result reuse, evidence, and cycle semantics are too large to add safely now. |
| [#54 Rich structured Manual interaction](https://github.com/vanderpol/scap-ng/issues/54) | 0.3 keeps simple Manual Assessment procedure + normalized outcome + provenance. | Typed multi-question/branching OCIL-like flows are useful but not required for the dominant STIG manual case. |
| [#48 Target ownership / organization / POC metadata](https://github.com/vanderpol/scap-ng/issues/48) | Optional enterprise enrichment does not block the 0.3 core result contract. | Valuable for aggregation/routing, but not part of assessment truth and can mature independently. |
| [#53 Full deviation/adjudication lifecycle](https://github.com/vanderpol/scap-ng/issues/53) | 0.3 preserves the principle that technical truth is not erased by policy disposition; the complete standing-deviation lifecycle/scoring model is later work. | Scope, expiration, revocation, scoring, effective outcome, and adjudication vocabulary need separate policy/results design. |

## Explicitly out, not deferred

These questions are resolved for 0.3 and should **not** be carried forward as if they are merely waiting for more implementation:

- [#47 XCCDF Value/Parameter clone](https://github.com/vanderpol/scap-ng/issues/47) — **OUT** as a native abstraction; preserve migration semantics through typed native inputs/Tailoring/Organizational Input.
- [#170 hidden capability-specific `reported_elements` defaults](https://github.com/vanderpol/scap-ng/issues/170) — **OUT**; effective reporting behavior must remain explicit/author-visible.
- [#177 normative thin/full result profiles](https://github.com/vanderpol/scap-ng/issues/177) — **OUT**; use one canonical result contract with bounded evidence/projections.
- [#178 dedicated shared-applicability artifact](https://github.com/vanderpol/scap-ng/issues/178) — **OUT**; use ordinary applicability Assessments/reuse instead.

## Not release blockers

Optional tooling can continue without changing 0.3 semantics:

- HTML rendering (#158)
- XLSX manual-audit output (#159)
- repository normalization/deduplication tooling (#41)

The rule for the Board checkpoint is simple: **deferred work may be shown as future research, but it SHALL NOT appear in the normative 0.3 schema/examples/package as accepted behavior.**
