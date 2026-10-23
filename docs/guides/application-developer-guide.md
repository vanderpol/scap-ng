# SCAP-NG Application Developer Guide

**Status: Draft — Needs Review (SCAP-NG 0.4.0 pre-alpha).** The current language, schemas, and implementation evidence are not a completed scanner-conformance standard. This guide is intended to become the version-pinned, testable requirements baseline for a future reference-implementation task; it does not authorize implementation or define new language behavior. Open wording and behavior questions are tracked in [#49](https://github.com/vanderpol/scap-ng/issues/49) and [#252](https://github.com/vanderpol/scap-ng/issues/252).

## 1. What an implementation consumes and produces

SCAP-NG distinguishes content **producers**, which create source or compiled content, from **consumers**, which process compiled content and produce results. An implementation may perform both roles.

| Artifact | Responsibility |
| --- | --- |
| Authoring source | Benchmark policy, Rules, referenced Assessments, and related authored data. |
| Compiled package | A self-contained, integrity-bound representation whose references resolve by logical identity, not source path. |
| Result package | Run/target/policy information and Rule-facing outcomes with distinct technical evidence and explanation. |

[Conformance roles](../../specification/core/conformance.md) · [Packaging](../../specification/package/package-and-integrity.md) · [Results](../../specification/results/results.md)

## 2. Source processing

The current [compilation model](../../specification/package/package-and-integrity.md) calls for parsing, explicit-reference resolution, schema validation, semantic validation, policy/Assessment binding resolution, normalization, and canonical output.

A producer must reject unresolved required references and invalid identity bindings; it must not guess a missing reference. Schema validation does **not** settle constraints such as Profile inheritance, effective policy, capability compatibility, or result behavior. See [conformance and semantic validation](../../specification/core/conformance.md).

The exact version matters. Use the [0.4.0 schema snapshot](../../schema/v0.4.0/README.md) for 0.4 authoring. Do not mix fields from archived 0.3 content or the separate 0.4 research overlays. Existing [converter/compiler commands](../developer/CONVERTER-COMPILER-RUNBOOK.md) document a limited source-proven implementation subset, not full supported-SCAP-1.4 coverage.

## 3. Loading and executing compiled content

The [package contract](../../specification/package/package-and-integrity.md) requires an authoritative compiled object-resolution manifest with integrity information. Runtime reference lookup uses that manifest, not directory search or source-file naming.

Conceptually, [Benchmark processing](../../specification/policy/benchmark.md) resolves the effective policy and inputs, evaluates Platform and Rule applicability, selects the applicable Assessment Methods, and produces results identifying the policy used. A consumer must distinguish policy selection and applicability from an Assessment's technical outcome.

The [Assessment contract](../../specification/assessment/assessment-method.md) separates Objects, collected Items, Test conditions and `evaluate`. Existence, value matching, completeness, and error/unknown propagation require the version's exact semantics. No ordinary Boolean simplification may be presumed to preserve six-state outcomes.

## 4. What a validation claim means

Report validation evidence at the layer actually tested:

1. Serialization and schema.
2. Cross-reference and semantic validation.
3. Evaluator behavior against independently expected observations.
4. Collection/acquisition behavior.
5. Live-target execution.
6. Legacy migration equivalence.

These are distinct claims. A compiled, hash-checked package is not proof of live collection or scanner-result correctness. [Normative conformance distinction](../../specification/core/conformance.md).

## 5. Draft — Needs Review: implementation contracts not fully settled

These items are **not** implementation mandates or conformance criteria until their governing text and tests are approved.

- **Capability collectors:** Precise Item identity, collection scope, absent values, permissions/errors, partial populations, and platform API choices need capability-by-capability contracts. API examples from legacy documentation are recommendations unless the actual collection semantics require them. See the [NTUSER source/documentation disposition](../../review/current/0.4.0-OVAL-XSD-METADATA-CROSSWALK.md).
- **Results:** Confirm final serialized `summary` naming, explanatory structure and canonical versus projected-result treatment against the versioned result schema. Current specification prose still includes older `message` references; do not silently choose one. See [Results and Evidence](../../specification/results/results.md).
- **Signing and trust:** The [package specification](../../specification/package/package-and-integrity.md) separates content and result signatures but leaves the final signature format and trust model under design.
- **Input and policy precedence:** Reconcile [Benchmark Parameters](../../specification/policy/benchmark.md) and [Profiles/Tailoring](../../specification/policy/profiles-and-tailoring.md) before implementing an ambiguous override path.
- **Unsupported/incomplete evaluation:** The [conformance specification](../../specification/core/conformance.md) requires unsupported capabilities to remain distinct from compliance failure; final standardized reason/result vocabulary remains under design.

## 6. Reference implementation requirements — Draft — Needs Review

A future implementation task should cite exact **RID**, SCAP-NG version/commit, governing clause/schema, independent positive and negative fixtures, and expected result. The table is an initial traceability index, **not** a declaration that tests or implementations already exist. Detailed test cases belong in the [conformance corpus #50](https://github.com/vanderpol/scap-ng/issues/50), not duplicated here.

| RID | Source-grounded requirement to implement | Minimum acceptance evidence |
| --- | --- | --- |
| **DEV-001** | Validate serialization and version-local schema. [Conformance §3](../../specification/core/conformance.md) | Correct-version valid fixture accepted; invalid shape or mixed-version fixture rejected. |
| **DEV-002** | Resolve required logical identities and reject missing/ambiguous references. [Benchmark §§4,16](../../specification/policy/benchmark.md) | Positive linkage, missing reference and duplicate-ID negative fixtures. |
| **DEV-003** | Apply Benchmark membership, Profile and Tailoring resolution in specified order. [Benchmark §15](../../specification/policy/benchmark.md) | Selection and inheritance fixtures, including forbidden re-enablement; precedence ambiguity must be resolved before tasking. |
| **DEV-004** | Preserve Test Item existence separately from State/field matching and all defined non-Boolean outcomes. [Assessment method](../../specification/assessment/assessment-method.md) | Independent six-state, zero-Item, incomplete and error fixtures; **not yet ready as a complete conformance claim**. |
| **DEV-005** | Emit an integrity-bound compiled package and reject altered members. [Packaging §5](../../specification/package/package-and-integrity.md) | Manifest resolution test and digest-mismatch rejection; final signature format remains blocked. |
| **DEV-006** | Produce independently interpretable policy and technical results. [Results](../../specification/results/results.md) | Versioned expected-result fixtures; **final `summary` field contract and projection policy require review**. |
| **DEV-007** | Preserve claimed supported legacy semantics during conversion, with explicit blockers instead of approximation. [SCAP 1.4 migration](../../specification/migration/scap-1.4-migration.md) | Original source pinned; source-exact positive/negative comparisons and unsupported-case diagnostics. |

**Tasking rule:** implement only the rows and subsets whose source semantics and expected fixtures are resolved. A requirement with an unresolved normative choice stays **blocked**, even if an engineering approach appears obvious. Maintain separate evidence for parser/schema, semantic validator, evaluator, collector, live scan, and migration layers.

## Appendix: source authority for SCAP 1.4 migration

SCAP 1.4 is defined by a **combined** source set, not XSD alone:

- [NIST SP 800-126 Rev. 4](https://csrc.nist.gov/pubs/sp/800/126/r4/final) — SCAP 1.4 technical specification.
- [NIST SP 800-126A Rev. 4](https://csrc.nist.gov/pubs/sp/800/126/a/r4/final) — annex governing allowed component-version updates.
- [NIST IR 7275 Rev. 4, March 2012 update](https://csrc.nist.gov/pubs/ir/7275/r4/upd1/final) — XCCDF 1.2 data and processing model.
- [NIST SCAP 1.4 release index](https://csrc.nist.gov/Projects/security-content-automation-protocol/scap-releases/scap-1-4) — component versions, schemas, and Schematron.
- [OVAL 5.12.3 definitions XSD](https://github.com/OVAL-Community/OVAL/blob/v5.12.3/oval-schemas/oval-definitions-schema.xsd) and [common XSD](https://github.com/OVAL-Community/OVAL/blob/v5.12.3/oval-schemas/oval-common-schema.xsd) — pinned OVAL semantics, including annotations.

Use the exact applicable source clause or schema element for any migration claim. XSD annotations, Schematron and normative processing prose may carry essential behavior not captured by element structure. Native NG requirements come from the accepted, version-pinned NG specification and schemas; differences must be explicit and reviewed.
