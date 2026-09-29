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
