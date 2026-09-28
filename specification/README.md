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
