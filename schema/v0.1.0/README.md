# SCAP-NG JSON Schema v0.1.0 draft

Status: **pre-alpha corpus-validated draft**

This directory contains the first versioned JSON Schema release candidate for
the current SCAP-NG native architecture. It is intentionally a schema for the
language we have actually designed and exercised, not a reservation mechanism
for every feature we may add later.

## Current architecture

- Benchmark -> Rule -> selected Assessment is authoritative.
- There is no separate Policy document.
- Assessment source uses `objects`, `variables`, `states`, `tests`, and
  `evaluate` as the core automated structure.
- Test, Object, State, and Variable semantics remain independently meaningful
  and require semantic compatibility validation.
- `Collection` is reserved for the runtime act of evaluating an Object and
  producing Items; it is not the authored Object node name.
- Applicability Assessments are ordinary Assessments invoked for applicability.
- Migration, conversion, quarantine, parity, and normalizer evidence are
  excluded from native content schemas.

## What v0.1.0 validates

The current executable schemas cover:

1. Benchmark
2. Rule
3. Assessment
4. Applicability catalog
5. Tailoring (strawman)
6. Benchmark Result (strawman with canonical Rule-result instances)
7. Assessment Result (first-draft strawman)
8. Organizational Input

JSON Schema validates document shape, required fields, basic types, selected
enumerated vocabularies, and manual-versus-automated structural requirements.

### Benchmark Result instance model

Each effectively selected Rule has one policy-facing Rule Result. Every Rule
Result contains a non-empty `instances` array, including the ordinary
single-invocation case.

The Rule Result's top-level `outcome` is the deterministic aggregate policy
outcome. Invocation/check/target-specific outcomes and detailed
`assessment_result_ref` values live in the instances. There is intentionally
no alternate canonical direct-reference shape for the common case.

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

## OVAL terminology alignment

The current working decision is to use the established OVAL terms **Test**,
**Object**, **State**, **Variable**, and **Item** when SCAP-NG retains the same
substantive concept. The authored `Collection` term has therefore been retired
in favor of `Object`; collection describes runtime execution of an Object.

Intentional native terminology improvements remain:

- OVAL Definition -> Assessment;
- OVAL criteria/criterion -> `evaluate`;
- OVAL generic comments -> typed `assessment_title`, `test_title`,
  `object_title`, `state_title`, and `variable_title`.

Tests retain OVAL `check_existence`, `check`, and `state_operator` when
those semantics are preserved. Deep capability schemas SHALL be generated
against this aligned vocabulary rather than the earlier
Collection/assertion/item-quantifier prototype.

## Planned next schemas

Package-manifest and deeper reusable result-component schemas remain to be
added. Tailoring, Organizational Input, Benchmark Result, and Assessment Result
schemas now exist and will continue to evolve with the result-model work.

The full pinned NIWC Current native corpus census remains the primary evidence
used to classify fields as required, optional, conditional, extensible, or
migration-only before schemas become normative.


## Manual Assessment high-level drafts

The following disposable schemas exercise the simplified Manual Assessment model
without importing OCIL's questionnaire/workflow object graph:

- `manual-assessment.schema.json`
- `manual-assessment-result.schema.json`

The model intentionally keeps the common manual path small:

1. authoritative human-readable procedure/check text;
2. a declared response vocabulary and explicit response-to-outcome mapping;
3. optional comments/evidence;
4. evaluator identity and completion time;
5. import/delegation provenance when applicable.

These files are design probes and MAY change as Manual Assessment semantics are
reviewed. They SHALL NOT be treated as evidence that arbitrary OCIL-style
branching or workflow has been adopted.

