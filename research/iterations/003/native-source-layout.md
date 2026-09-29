# Iteration 003 Native Source Layout

**Status:** active design direction

Iteration 003 SHALL NOT preserve standalone files merely because iteration 001/002
generators emitted them.

The Benchmark is the authoritative policy container. Separate files are justified
only for independently reusable or independently maintained objects.

## Benchmark-owned content

The following belong semantically to the Benchmark and SHOULD be serialized in
`benchmark.yaml` unless later evidence demonstrates a strong authoring reason to
split them:

- Benchmark identity, title, version, publisher metadata, and status;
- target Platform identity/reference;
- Rule membership;
- meaningful Group hierarchy;
- publisher-defined Profiles;
- Benchmark/policy Parameters and publisher defaults;
- Benchmark-level applicability composition where needed.

Accordingly, iteration 003 SHALL NOT generate:

- `profiles.yaml`;
- `groups.yaml`;
- `values.yaml` / a standalone parameter catalog merely to mirror XCCDF Value;
- `platforms.yaml` as a dump of legacy CPE/XCCDF platform structures.

## Platform

A Benchmark SHALL identify its logical target Platform directly.

Example:

    benchmark:
      id: rhel9-stig
      platform: rhel.9

The executable logic that proves `rhel.9` MAY be a reusable Assessment Method
stored outside the Benchmark when reuse across Benchmarks warrants it.

Platform identity metadata may include external identifiers such as CPE, but
legacy CPE dictionary/application-language structure is migration provenance,
not native Benchmark content.

A separate platform source object/file is therefore optional, not assumed.

## Applicability

Applicability is policy composition evaluated using the ordinary Assessment
language.

The Benchmark or Rule SHOULD reference named applicability conditions directly.
The executable implementation of a reusable applicability condition SHOULD be
an ordinary Assessment Method.

Iteration 003 SHALL NOT generate a monolithic `applicability.yaml` containing
legacy source IR.

A small applicability registry is retained to provide stable semantic
applicability identifiers and bind those identifiers to Assessment Methods.
Rules and Benchmarks reference applicability IDs rather than assessment paths.
See `applicability-registry.md`.

## Parameters

Parameters are policy, so their declarations and publisher values/defaults
belong in the Benchmark.

Profiles may bind/refine the effective publisher policy value only as permitted
by the accepted parameter/profile model.

Assessment Methods consume explicitly typed Parameter bindings but do not own
publisher policy values.

A standalone `values.yaml` SHALL NOT be emitted merely to preserve XCCDF Value
serialization.

## Processing

`processing.yaml` has no native authoring role identified by the current design.

Resolution plans, source-accounting data, effective-state expansions, conversion
bookkeeping, and compiler/runtime instructions are generated evidence or
implementation internals.

They SHALL NOT appear as native source merely because the migration tool needed
them internally.

If a future normative runtime object is demonstrated to be necessary, it must be
specified independently rather than inheriting the old `processing.yaml`
structure.

## Provisional source tree

A benchmark-specific source tree should therefore begin approximately as:

    rhel9/
      benchmark.yaml
      policy/
        RHEL-09-....policy.yaml
      applicability.yaml
      assessments/
        automated/
          ...
        manual/
          ...
        applicability/
          ...

Reusable platform/applicability/compliance Assessments may live in shared
assessment libraries when reuse is proven.

This is an authoring organization convention. Object identity and semantics come
from content, not paths.

## Governing principle

A separate native file/object must justify its existence through semantic
independence, reuse, ownership, or maintainability.

SCAP 1.4 decomposition is not, by itself, sufficient justification.
