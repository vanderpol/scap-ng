# SCAP-NG draft specification

**Status:** pre-alpha working draft. SCAP-NG 0.3.0 is the active development version; 0.2.0 is the frozen earlier review baseline. This is not a released standard.

This directory contains the proposed normative contract. Research records explain history/rationale; the specification describes expected content/processor behavior. Unresolved questions should remain visibly open rather than being silently normalized into requirements.

## Start here

1. [Core objectives](objectives.md)
2. [Source and result examples](examples/README.md)
3. [Terminology](terminology.md)
4. [Requirements index](requirements-index.md)
5. [Conformance and validation](core/conformance.md)
6. [Benchmark, Rule, and Group model](policy/benchmark.md)
7. [Platform and applicability](policy/platform-and-applicability.md)
8. [Profiles and Tailoring](policy/profiles-and-tailoring.md)
9. [Policy resolution/evaluation order](policy/policy-resolution.md)
10. [Parameters and Organizational Input](policy/parameters-and-organizational-input.md)
11. [Assessment method](assessment/assessment-method.md)
12. [Manual assessment](assessment/manual-assessment.md)
13. [Packaging and integrity](package/package-and-integrity.md)
14. [Results and evidence](results/results.md)
15. [SCAP 1.4 migration](migration/scap-1.4-migration.md)
16. [OVAL 5.12.3 migration mapping](migration/oval-5.12.3-to-ng.md)
17. [OVAL capability crosswalk](migration/oval-5.12.3-capability-crosswalk.md)
18. [Security considerations](security/security-considerations.md)
19. [SCAP 1.4 concept crosswalk](crosswalk/scap-1.4-concept-crosswalk.md)
20. [SP 800-126r4 concept review](crosswalk/sp800-126r4-concept-review.md)

## Core design principles

- A **Benchmark** contains policy **Rules**; a Rule references one or more **Assessments** that define how the requirement is evaluated.
- SCAP-NG preserves the meaning of supported SCAP 1.4 and OVAL content while using simpler native structures instead of reproducing XML and legacy packaging mechanics.
- Behavior that can affect an assessment result is explicit. Content should not depend on hidden defaults or vendor-specific assumptions.
- Established SCAP and OVAL concepts and terminology are reused when they remain accurate; new concepts are introduced only when they provide a clear benefit.
- Content is modular and reusable. Shared Assessments, Observations, or collected facts must not change policy meaning, provenance, or assessment results.
- Results explain both **what happened and why**, with clear completeness and bounded evidence rather than unnecessary result volume.
- Independent implementations should reach the same meaning and results from the specification and conformance material; schema validation alone is not proof of conformance.

## Assessment reference

The [Assessment reference](assessment/reference/README.md) provides shared behavior, capability/field documentation, examples, and provenance. It supports the evolving specification/conformance work but does not replace normative semantics.

## Relationship to current design

The implementation/design authority is [CURRENT-DESIGN.md](../research/iterations/003/design/CURRENT-DESIGN.md). Material accepted decisions should be reconciled into this specification; historical research or old generated source does not override either document.
