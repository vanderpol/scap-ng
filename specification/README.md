# SCAP-NG Draft Specification

**Status:** pre-alpha working draft

This directory contains emerging normative SCAP-NG specification text.

Material here is intentionally more normative and implementation-facing than
the design history under `research/`. Research records explain how and why a
decision was reached; specification text defines the behavior that conforming
content and processors are expected to implement.

Until a formal SCAP-NG release is published, all normative language in this
directory remains subject to revision.

Normative terms **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, and
**MAY** are used in their conventional standards sense.

<!-- reading-order:start -->
## Read the specification in order

The specification is organized as a continuous document even though its
sections are stored in subdirectories. Start here and follow the ordered links
below; every page also contains **Previous · Contents · Next** navigation.

1. [SCAP-NG Terminology](terminology.md)
2. [SCAP-NG Requirements Index](requirements-index.md)
3. [Conformance and Validation](core/conformance.md)
4. [Benchmark, Rule, and Group Model](policy/benchmark.md)
5. [Platform Specification and Applicability](policy/platform-and-applicability.md)
6. [Profiles and Tailoring](policy/profiles-and-tailoring.md)
7. [Policy Resolution and Evaluation Order](policy/policy-resolution.md)
8. [Parameters, Tailoring Values, and Organizational Input](policy/parameters-and-organizational-input.md)
9. [Assessment Method](assessment/assessment-method.md)
10. [Manual Assessment](assessment/manual-assessment.md)
11. [Source, Compilation, Packaging, and Integrity](package/package-and-integrity.md)
12. [Results and Evidence](results/results.md)
13. [SCAP 1.4 to SCAP-NG Migration](migration/scap-1.4-migration.md)
14. [OVAL 5.12.3 to SCAP-NG Migration Mapping](migration/oval-5.12.3-to-ng.md)
15. [OVAL 5.12.3 Test-Type to SCAP-NG Capability Crosswalk](migration/oval-5.12.3-capability-crosswalk.md)
16. [Security Considerations](security/security-considerations.md)
17. [SCAP 1.4 to SCAP-NG Concept Crosswalk](crosswalk/scap-1.4-concept-crosswalk.md)
18. [SP 800-126r4 Concept Review for SCAP-NG](crosswalk/sp800-126r4-concept-review.md)
<!-- reading-order:end -->

## Start here

- `requirements-index.md` — current normative-area inventory and open issues.
- `crosswalk/sp800-126r4-concept-review.md` — informative completeness review
  against NIST SP 800-126 Rev. 4 / SCAP 1.4.

## Normative sections

### Core

- `core/conformance.md` — producer/consumer roles, validation, conformance
  claims, unsupported content handling.

### Policy

- `policy/benchmark.md` — Benchmark, Rule, Group, identity, extensions.
- `policy/platform-and-applicability.md` — Platform specification,
  Rule applicability, applicability catalogs.
- `policy/profiles-and-tailoring.md` — publisher Profiles and external
  Tailoring.
- `policy/policy-resolution.md` — deterministic composition/evaluation order
  for Benchmark, Profile, Tailoring, inputs, Platform, applicability, and Rule
  Assessment.
- `policy/parameters-and-organizational-input.md` — typed policy values,
  Organizational Input, safe Assessment bindings.

### Assessment

- `assessment/assessment-method.md` — Assessment binding, modality,
  capabilities, reuse, explicit semantics.
- `assessment/manual-assessment.md` — procedure-only Check Text baseline and
  default manual-result behavior.

### Results

- `results/results.md` — target identity, Rule results, deterministic
  messages, failure reasons, evidence, completeness, SIEM projection.

### Packaging and execution

- `package/package-and-integrity.md` — source versus compiled form,
  reference resolution, self-contained scanner packages, integrity/signing.

### Migration

- `migration/scap-1.4-migration.md` — lossless-first SCAP 1.4 migration and
  optional native refactoring.

### Security

- `security/security-considerations.md` — untrusted content, executable
  capability boundaries, policy-data isolation, sensitive results.

## Relationship to research

A specification requirement SHOULD be backed by a research decision, migration
example, production requirement, interoperability requirement, or other
documented rationale.

Unresolved design questions SHOULD remain in `research/` or be explicitly
marked open in the specification rather than being silently converted into
normative requirements.

### OVAL 5.12.3 migration

- `migration/oval-5.12.3-to-ng.md` — normative construct mapping from OVAL
  Definition/Test/Object/State/Variable semantics into SCAP-NG.
- `migration/oval-5.12.3-capability-crosswalk.md` — OVAL 5.12.3 Test-type to
  provisional SCAP-NG Capability inventory.


## Evolutionary design principle

SCAP-NG is an evolutionary successor to SCAP 1.4, not a terminology reset.

Before introducing a new normative term, object type, processing concept, or
semantic distinction, specification work SHOULD first review the corresponding
NIST SCAP, XCCDF, OVAL, CPE, ARF, and related standards terminology.

When an existing standards term remains semantically accurate and useful,
SCAP-NG SHOULD retain or deliberately adapt that term rather than inventing a
synonym.

A new term SHOULD be introduced only when:

- existing SCAP/NIST terminology is materially inaccurate for the NG concept;
- retaining the legacy term would preserve obsolete architecture or create
  ambiguity; or
- SCAP-NG introduces a genuinely new semantic concept with no suitable
  predecessor.

When SCAP-NG intentionally renames, replaces, or removes an established SCAP
1.4 concept, the specification crosswalk SHOULD record that decision and its
rationale.

Publisher-specific vocabulary SHALL NOT be promoted into generic SCAP-NG
terminology merely because it is common in one content ecosystem.


## Native feature admission and simplification principle

SCAP-NG SHALL NOT preserve a legacy SCAP/XCCDF/OVAL construct merely because
the construct exists in an earlier specification or because a hypothetical
future use can be imagined.

A construct SHOULD become part of the native SCAP-NG model only when at least
one of the following is true:

- it preserves a demonstrated semantic requirement that cannot be represented
  clearly by an existing native construct;
- it is exercised by real content or realistic implementation/conformance use;
- it is necessary for interoperability, portability, auditability, or
  deterministic evaluation;
- it materially improves authoring or implementation without creating
  competing ways to express the same semantics.

Legacy constructs that exist primarily for XML serialization, inheritance
machinery, packaging indirection, historical compatibility, or speculative
extensibility SHOULD be normalized away during migration when their effective
meaning can be preserved directly.

A converter MAY need to understand a legacy construct completely in order to
migrate it losslessly. That requirement does **not** imply that the construct
must survive as a native SCAP-NG feature.

When deciding the disposition of a legacy feature, the project SHOULD classify
it explicitly as one of:

1. **retain** — the concept remains useful and substantially unchanged;
2. **replace** — preserve the semantics using a simpler or more coherent native
   construct;
3. **normalize away** — resolve the legacy mechanism during migration and emit
   only its effective meaning;
4. **drop** — omit a genuinely obsolete, deprecated, harmful, or unjustified
   feature, with the divergence documented.

New native features SHOULD be justified by concrete content, implementation, or
standards requirements rather than hypothetical use cases alone.



## Vendor adoption and implementability

SCAP-NG SHOULD optimize for broad, correct implementation by independent
vendors.

Specification simplicity is an interoperability and adoption requirement.
A technically expressive feature that substantially increases implementation
complexity, creates multiple equivalent ways to represent the same semantics,
or requires scanner-specific interpretation SHOULD be rejected or simplified
unless its value is demonstrated.

The native standard SHOULD prefer:

- one clear construct for one semantic purpose;
- explicit behavior over hidden defaults;
- deterministic processing over implementation-defined behavior;
- shallow, composable concepts over overlapping feature families;
- compile-time normalization over runtime legacy machinery;
- machine-readable conformance requirements and known-good examples;
- independently testable capabilities and evaluator semantics;
- useful error reporting for unsupported or invalid content;
- minimal mandatory implementation surface consistent with semantic fidelity.

Optionality SHOULD be introduced cautiously. Every optional feature increases
the risk of fragmented implementation profiles and content that works only on a
subset of products.

A new native feature SHOULD therefore demonstrate that its interoperability or
functional benefit outweighs its implementation, testing, documentation, and
long-term compatibility cost.

The project SHOULD routinely ask:

> Would two independent vendors reading only the specification and conformance
> corpus implement this the same way?

If the answer is not clearly yes, the design SHOULD be simplified or made more
explicit before standardization.



## Complexity budget

Implementation complexity SHALL be treated as a standards cost.

When two candidate designs preserve the required semantics and interoperability,
SCAP-NG SHOULD prefer the design that requires:

- fewer distinct concepts;
- fewer runtime branches and special cases;
- fewer context-sensitive interpretation rules;
- fewer cross-file joins to understand one result;
- fewer hidden defaults;
- fewer equivalent authoring forms;
- fewer optional behaviors;
- less scanner-specific policy logic;
- simpler validation and conformance testing.

A feature SHALL NOT be considered "free" merely because it can be expressed in
a schema. Every additional construct creates parser, validator, compiler,
runtime, result, test, documentation, and interoperability obligations.

The specification SHOULD push complexity toward deterministic build-time
normalization when doing so preserves semantics and produces simpler
scanner-facing content.

Runtime behavior SHOULD remain boring and predictable. A scanner SHOULD be able
to execute already-resolved content without re-performing historical XCCDF,
OVAL, packaging, inheritance, fallback, or authoring machinery that could have
been resolved earlier.

A proposed feature that materially increases implementation complexity SHOULD
identify the concrete requirement it satisfies and why an existing simpler
construct cannot satisfy it. Hypothetical flexibility alone is insufficient
justification.

