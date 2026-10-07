# Deferred beyond SCAP-NG 0.3

**Status:** authoritative scope boundary for the 0.3 OVAL Board checkpoint.

The 0.3 requirement set is maintained in [#174](https://github.com/vanderpol/scap-ng/issues/174).

## Core design deferred from 0.3

Only two core assessment-language design topics are intentionally deferred:

| Item | 0.3 boundary | Why deferred |
| --- | --- | --- |
| [#166 Shared Observation](https://github.com/vanderpol/scap-ng/issues/166) | No normative Observation artifact/export/result contract in 0.3. | Production value is proven, but typed exports, execution/result provenance, binding identity, manifest dependency/cycle handling, and cache/reuse semantics need a complete interoperable contract. |
| [#167 `evaluate` redesign](https://github.com/vanderpol/scap-ng/issues/167) | Keep the existing named-Test + explicit `evaluate` model unchanged for 0.3. No implicit one-Test root, nested Test-definition model, new shorthand, or canonical placement redesign. | Real multi-Test/six-state composition still requires `evaluate`; redesigning it now would create a second canonical authoring model without enough benefit for this checkpoint. |

These are **deferred, not rejected**. Their research remains available for the next design cycle.

## Other future work outside the 0.3 core design

The following work is also not normative 0.3 language/runtime, but it is peripheral to the central authoring-modernization freeze rather than part of the core deferred design list:

- [#168 typed `linux.fstab` capability](https://github.com/vanderpol/scap-ng/issues/168)
- [#175 Organizational Input instance/database/site targeting](https://github.com/vanderpol/scap-ng/issues/175)
- [#44 broad Assessment composition/runtime collection reuse](https://github.com/vanderpol/scap-ng/issues/44)
- [#54 rich structured Manual interaction](https://github.com/vanderpol/scap-ng/issues/54)
- [#48 target ownership / organization / POC enrichment](https://github.com/vanderpol/scap-ng/issues/48)
- [#53 full deviation/adjudication lifecycle](https://github.com/vanderpol/scap-ng/issues/53)

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

The Board-review rule is simple: **Observation and evaluate redesign are the two deferred core design topics. Deferred or future work SHALL NOT appear in the normative 0.3 schema/examples/package as accepted behavior.**
