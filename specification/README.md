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
