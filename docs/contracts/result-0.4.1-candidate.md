# SCAP-NG 0.4.1 minimal Result implementation candidate

**Draft; final owner review required.** This is the coordinated canonical
contract receipt for RI Issue #43. It does not modify frozen 0.4.0 schemas or
historical Result bytes.

The single proposed 0.4.1 contract is
`proposed-schema/result-0.4.1/assessment-result.schema.json`, SHA-256
`1a3b4b68d4b54bdc71f66460e74dd8eb184d7fbec10bbc63941aee28e96adab2`.
The optional diagnostic sidecar is
`proposed-schema/result-0.4.1/result-diagnostic.schema.json`, SHA-256
`7f322797deb2cd105e32f896e2a32c2f50a1723e7a2a510f30160f84049a7406`.

The contract requires essential Assessment identity, target, purpose/class,
outcome, completeness, authority context, authored Object/Require references,
cardinality and conditional typed comparisons. A terminal authored Test expression is represented with `operator: "test"`; `and` and `or` are reserved for authored groups, so the Result never fabricates grouping semantics. It forbids expected/observed
values when no actual value comparison occurred. It preserves distinct Items,
multivalue values, missing/error/unknown/incomplete semantics and redaction.

The coordinated RI candidate is documented in
[RI `result-0.4.1-candidate.md`](https://github.com/vanderpol/scap-ng-ri/blob/codex/result-0.4.1-candidate-ri/docs/result-0.4.1-candidate.md).
An actual root-backed PASS and normal-user UNKNOWN RI receipt are retained in
RI `docs/evidence/result-0.4.1/`.

The canonical fixture set under `docs/contracts/evidence/result-0.4.1/`
contains 10 cases covering the approved conformance dimensions. Variables and
Inputs fixtures establish the Result contract; they do not claim new native
collector support.

The optional diagnostic contract is digest-bound and cannot alter production
Result truth. Text/HTML consumers must work from the canonical Result alone.
Final approval is still required before this 0.4.1 schema is treated as a
released canonical contract.
