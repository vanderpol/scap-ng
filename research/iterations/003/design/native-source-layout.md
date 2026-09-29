# Iteration 003 Native Source Layout

## Governing principle

A separate native file/object must justify its existence through semantic
independence, reuse, ownership, or maintainability.

SCAP 1.4 decomposition is not sufficient justification.

## Benchmark-owned policy

benchmark.yaml owns:

- Benchmark identity and metadata;
- target Platform identity/reference;
- Rule membership;
- meaningful Group hierarchy;
- publisher-defined Profiles;
- Benchmark/policy Parameters and publisher defaults;
- Benchmark-level policy composition.

Iteration 003 SHALL NOT generate standalone:

- profiles.yaml
- groups.yaml
- values.yaml
- platforms.yaml
- processing.yaml

## Applicability registry

A small applicability.yaml remains in the split-policy-assessment design as an
indirection layer:

    applicability ID -> Assessment Method

Rules reference applicability IDs rather than Assessment file paths.

The registry SHALL contain only native SCAP-NG identity/binding information and
SHALL NOT contain migrated XCCDF/OVAL/CPE structures.

## Source organization

    source/
      split-policy-assessment/
        <benchmark>/
          benchmark.yaml
          applicability.yaml
          policy/
          assessments/
            automated/
            manual/
            applicability/

Reusable/shared Assessments may later move into a clearly named shared subtree
once exact reuse is demonstrated.

Source and sample results SHALL remain in different top-level directories.


## Explicit native field visibility

Iteration 003 SHALL favor self-describing source over implicit defaults or
tribal knowledge.

For native objects intended for human authoring/review, every field supported
by that object type SHOULD be serialized even when it has no value.

Use:

- `null` for an optional scalar/object that is supported but unset;
- `[]` for a supported collection with no members;
- `{}` for a supported mapping with no entries.

A field SHALL be omitted only when it is not part of that native object model
or when omission has a deliberately defined semantic meaning.

This rule applies especially to Rule Policy source. The supported Rule Policy
surface for iteration 003 is:

    policy:
      id:
      title:
      severity:
      role:
      weight:
      discussion:
      rationale:
      documentable:
      warnings:
      identifiers:
      references:
      requires:
      conflicts:
      applicability:
      parameters:
      remediation:
      checks:
      default_check:

The exact vocabulary may evolve during iteration 003, but once a field is part
of the supported Policy model it SHALL remain visible in generated review
source even when unset.

This is intentionally different from opaque legacy content models where authors
and reviewers needed external schema knowledge to discover available
properties.

This explicit-field rule does not override Profile canonicalization decisions
where omission itself is semantically meaningful (for example, omission of
`disabled_rules` means the Profile does not alter Benchmark Rule selection).
