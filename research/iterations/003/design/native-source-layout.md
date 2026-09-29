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


## Hierarchical Group taxonomy

Groups SHALL support child Groups recursively.

For the iteration-003 migration experiment, the preferred generated hierarchy
is assessment-oriented at the top level and functional beneath it.

Illustrative form:

    groups:
      - id: automated
        title: Automated
        groups:
          - id: automated.ssh
            title: SSH
            rules:
              - RHEL-09-...
          - id: automated.password-policy
            title: Password Policy
            rules:
              - RHEL-09-...

      - id: manual-or-managerial
        title: Manual or Managerial
        groups:
          - id: manual-or-managerial.account-management
            title: Account Management
            rules:
              - RHEL-09-...
          - id: manual-or-managerial.documentation
            title: Documentation / Managerial Review
            rules:
              - RHEL-09-...

The top-level classification SHOULD follow the Rule's effective/default
Assessment Method, not merely the existence of an alternate manual check.

A Rule whose default check is automated but that also provides a manual
alternative belongs under `automated` unless human/managerial judgment is
material to the effective policy decision.

Functional subgrouping MAY be inferred from title, discussion, remediation,
manual procedure, Assessment capability, and affected configuration artifact.

Generated Group classification is migration metadata and navigation structure.
It SHALL NOT alter Rule applicability, Rule selection, Assessment behavior,
Parameter binding, or result semantics.

When the converter cannot infer a useful functional subgroup with sufficient
confidence, it SHOULD place the Rule under a `needs-grouping` child of the
appropriate assessment-mode parent rather than fabricate a topic.


## Relationship to XCCDF design

SCAP-NG is replacing the XCCDF serialization and legacy SCAP coupling model,
not discarding useful policy-language design merely because it originated in
XCCDF.

Iteration 003 SHOULD retain or adapt XCCDF concepts when they remain useful,
clear, and interoperable in a native NG model.

Examples include:

- Benchmark as the authoritative policy container;
- hierarchical Groups;
- Profiles as publisher-defined Benchmark variations;
- Rule-level policy metadata such as severity, role, weight, rationale,
  warnings, identifiers, references, dependencies, and remediation;
- explicit check selection;
- typed policy Parameters;
- platform and Rule applicability composition.

These concepts SHOULD be simplified where historical XCCDF behavior was
needlessly complex, but their useful semantics SHOULD NOT be removed simply to
make NG look different.

The design test is:

1. Does the concept have demonstrated authoring, interoperability, or execution
   value?
2. Can it be represented more clearly without legacy XML/SCAP coupling?
3. Can it remain self-describing without hidden defaults or schema tribal
   knowledge?

If yes, SCAP-NG SHOULD preserve the concept in native form.

Legacy XML namespaces, opaque identifiers, component hrefs, wrapper structures,
and cross-language stovepipes remain out of native NG source.
