# SCAP-NG Implementation Traceability Appendix

**Status: Draft — Needs Review (0.4.0 pre-alpha).** This optional technical companion to the [Application Developer Guide](../guides/application-developer-guide.md) records candidate, testable requirements. It is not a Codex prompt, an implementation authorization, or a conformance certificate. Governing semantics belong to the exact SCAP-NG versioned specification/schema.

## Draft — Needs Review: implementation traceability

A future implementation task should cite exact **RID**, SCAP-NG version/commit, governing clause/schema, independent positive and negative fixtures, and expected result. The table is an initial traceability index, **not** a declaration that tests or implementations already exist. Detailed test cases belong in the [conformance corpus #50](https://github.com/vanderpol/scap-ng/issues/50), not duplicated here.

| RID | Source-grounded requirement to implement | Minimum acceptance evidence |
| --- | --- | --- |
| **DEV-001** | Validate serialization and version-local schema. [Conformance §3](../../specification/core/conformance.md) | Correct-version valid fixture accepted; invalid shape or mixed-version fixture rejected. |
| **DEV-002** | Resolve required logical identities and reject missing/ambiguous references. [Benchmark §§4,16](../../specification/policy/benchmark.md) | Positive linkage, missing reference and duplicate-ID negative fixtures. |
| **DEV-003** | Apply Benchmark membership, Profile and Tailoring resolution in specified order. [Benchmark §15](../../specification/policy/benchmark.md) | Selection and inheritance fixtures, including forbidden re-enablement; precedence ambiguity must be resolved before tasking. |
| **DEV-004** | Preserve Test Item existence separately from State/field matching and all defined non-Boolean outcomes. [Assessment method](../../specification/assessment/assessment-method.md) | Independent six-state, zero-Item, incomplete and error fixtures; **not yet ready as a complete conformance claim**. |
| **DEV-005** | Emit an integrity-bound compiled package and reject altered members. [Packaging §5](../../specification/package/package-and-integrity.md) | Manifest resolution test and digest-mismatch rejection; final signature format remains blocked. |
| **DEV-006** | Produce independently interpretable policy and technical results. [Results](../../specification/results/results.md) | Versioned expected-result fixtures; 0.4 draft Rule/Assessment schemas require `summary`, while projection policy, prose consistency and runtime results remain under review. |
| **DEV-007** | Preserve claimed supported legacy semantics during conversion, with explicit blockers instead of approximation. [SCAP 1.4 migration](../../specification/migration/scap-1.4-migration.md) | Original source pinned; source-exact positive/negative comparisons and unsupported-case diagnostics. |

**Readiness boundary:** implement only the rows and subsets whose source semantics and expected fixtures are resolved. A requirement with an unresolved normative choice stays **blocked**, even if an engineering approach appears obvious. Maintain separate evidence for parser/schema, semantic validator, evaluator, collector, live scan, and migration layers.

