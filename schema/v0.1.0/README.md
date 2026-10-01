# SCAP-NG JSON Schema v0.1.0 draft

Status: **pre-alpha corpus-validated draft**

This directory contains the first versioned JSON Schema release candidate for
the current SCAP-NG native architecture. It is intentionally a schema for the
language we have actually designed and exercised, not a reservation mechanism
for every feature we may add later.

## Current architecture

- Benchmark -> Rule -> selected Assessment is authoritative.
- There is no separate Policy document.
- Assessment source currently uses `collections`, `variables`, `tests`, and
  `evaluate` as the core automated structure.
- Test, collection/object, State/predicate, and Variable semantics remain
  independently meaningful and require semantic compatibility validation.
- Applicability Assessments are ordinary Assessments invoked for applicability.
- Migration, conversion, quarantine, parity, and normalizer evidence are
  excluded from native content schemas.

## What v0.1.0 validates

The current executable schemas cover:

1. Benchmark
2. Rule
3. Assessment
4. Applicability catalog

JSON Schema validates document shape, required fields, basic types, selected
enumerated vocabularies, and manual-versus-automated structural requirements.

It does **not** prove:

- reference resolution;
- Test/Object/State capability compatibility;
- OVAL-derived quantifier/existence/result truth semantics;
- variable/filter/set dependency closure;
- cycle freedom;
- valid capability-specific fields or behavior combinations;
- package/signature integrity;
- runtime execution equivalence.

Those remain semantic-validator and conformance-test responsibilities.

## Corpus evidence

GitHub Actions run #44
(`Gate full native corpus on v0.1.0 JSON schemas`) validated the freshly
generated pinned NIWC Current corpus at revision
`8c8e5dff860af6b1290ee9273a282db24278f8d5`.

Before repository normalization:

- 65 Benchmarks
- 8,892 Rules
- 16,126 Assessments
- 65 applicability catalogs
- 25,148 total documents
- 25,148 valid
- 0 invalid

After repository normalization:

- 19,759 total native documents checked
- 19,759 valid
- 0 invalid

This demonstrates structural compatibility with the current generated corpus.
It does not establish that every accepted document is semantically valid.

## Deferred features

Important likely features are documented outside the executable schema until
their semantics are settled. In particular:

- conditional evaluation, including branching on a local Test result or a
  statically declared dependent Assessment/applicability result;
- Assessment composition and shared runtime collection execution;
- import/materialization of reused collected Items into self-contained
  Assessment results.

These features SHALL NOT be added to v0.1.0 merely to reserve speculative
syntax. See
[`specification/assessment/draft-future-assessment-features.md`](../../specification/assessment/draft-future-assessment-features.md).

## OVAL terminology review

The project is reconsidering whether the authored term `Collection` should
return to the established OVAL term `Object` while reserving
`collection execution` for runtime acquisition. Because this terminology
decision is not yet ratified, v0.1.0 preserves the current `collections`
serialization. A later schema revision may rename it deliberately with an
explicit migration rule.

The working terminology principle is: when SCAP-NG retains an OVAL construct
with substantially the same semantics, retain the established OVAL term unless
there is a clear benefit that outweighs the compatibility cost.

## Planned next schemas

Tailoring, organizational input, package manifest, and results schemas will be
added after the core authoring graph and result model stabilize.

The full pinned NIWC Current native corpus census remains the primary evidence
used to classify fields as required, optional, conditional, extensible, or
migration-only before schemas become normative.
