# SCAP-NG draft specification

**Status:** pre-alpha working draft. SCAP-NG 0.3.0 is the active development version; 0.2.0 is the frozen earlier review baseline. This is not a released standard.

This directory contains the proposed normative contract. Research records explain history/rationale; the specification describes expected content/processor behavior. Unresolved questions should remain visibly open rather than being silently normalized into requirements.

Normative terms **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** use their conventional standards meaning.

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

- Current architecture is **Benchmark → Rule → Assessment**; no separate Policy object.
- Retain established SCAP/OVAL terminology when it remains semantically accurate; introduce new terms only when the legacy concept is misleading or obsolete.
- Preserve demonstrated, non-deprecated semantics used by real/conformance content unless an explicit reviewed disposition replaces or removes them.
- Normalize away XML/packaging/inheritance machinery when its effective meaning can be represented directly.
- Prefer one clear construct per semantic purpose, explicit behavior over hidden defaults, and deterministic build-time normalization over runtime legacy machinery.
- Treat implementation complexity as a standards cost: every feature creates parser, validator, compiler, runtime, result, test, documentation, and interoperability obligations.
- Design for independent implementation: two vendors reading only the specification and conformance corpus should reach the same behavior.
- Keep migration provenance/evidence separate from executable native content.
- Keep schema validity, semantic validity, migration equivalence, collector conformance, live-target testing, human acceptance, and Board ratification distinct.

## Assessment reference

The [Assessment reference](assessment/reference/README.md) provides shared behavior, capability/field documentation, examples, and provenance. It supports the evolving specification/conformance work but does not replace normative semantics.

## Relationship to current design

The implementation/design authority is [CURRENT-DESIGN.md](../research/iterations/003/design/CURRENT-DESIGN.md). Material accepted decisions should be reconciled into this specification; historical research or old generated source does not override either document.
