# Platform Specification and Applicability

**Status:** pre-alpha normative draft

## 1. Three distinct questions

SCAP-NG SHALL distinguish:

1. **Platform** — is this target one of the products/platforms the Benchmark
   was written for?
2. **Rule applicability** — assuming the target is in Benchmark scope, is this
   particular Rule relevant to this target?
3. **Compliance** — if the Rule is applicable, does the target satisfy the
   Rule requirement?

These questions MAY use the same underlying Assessment language and
capabilities, but they SHALL remain separate semantic roles.

## 2. Platform predicates

A Platform predicate establishes product or operating-system identity.

Examples:

    windows.11
    windows.server-2025
    rhel.9
    oracle-linux.9

A Platform predicate SHALL have a stable logical identifier.

The author SHALL explicitly bind the Platform identifier to the Assessment
Method that establishes it.

A processor SHALL NOT infer Platform truth from:

- the identifier text;
- a filename or directory;
- a CPE name alone;
- an operating-system display string;
- hard-coded scanner knowledge.

CPE and other external platform identifiers MAY be retained as aliases or
references, but executable Platform truth comes from the bound Assessment
Method.

## 3. Benchmark Platform expression

A Benchmark SHALL declare an explicit Platform expression.

Boolean composition MAY include `all_of`, `any_of`, and `not` when
needed.

Example:

    platforms:
      any_of:
        - id: rhel.9
          assessment: ../../shared/assessments/automated/platforms/rhel-9.assessment.yaml
        - id: almalinux.9
          assessment: ../../shared/assessments/automated/platforms/almalinux-9.assessment.yaml
        - id: rocky-linux.9
          assessment: ../../shared/assessments/automated/platforms/rocky-linux-9.assessment.yaml

The exact source serialization remains subject to schema review.

A Benchmark whose Platform expression evaluates false is not applicable to the
target and its Rule compliance Assessments SHALL NOT be executed.

An indeterminate/error Platform evaluation SHALL NOT be treated as a false
Platform result merely for convenience.

## 4. What belongs in Rule applicability

A Rule applicability condition is an additional target condition that is not
part of basic product identity.

Examples include:

- workstation/member-server/domain-controller role;
- optional feature installed;
- package or application present;
- GNOME installed;
- FIPS mode enabled;
- NFS mounted;
- hardware feature present.

When a legacy platform combines product identity with one of these conditions,
SCAP-NG SHOULD separate the predicates when semantic equivalence is exact.

## 5. Applicability catalog

A Benchmark MAY declare one explicit applicability catalog.

If any Rule uses named applicability conditions, the Benchmark SHALL declare
the catalog that resolves those identifiers.

The catalog maps stable condition identifiers to Assessment Methods.

Example:

    applicability:
      windows.camera-installed:
        assessment: assessments/automated/applicability/windows-camera-installed.assessment.yaml

      windows.member-workstation:
        assessment: assessments/automated/applicability/windows-member-workstation.assessment.yaml

A Rule SHALL reference the stable condition identifier, not the Assessment file
path.

A processor SHALL resolve the identifier through the containing Benchmark's
catalog.

An undefined, duplicate, ambiguous, or unresolvable applicability identifier
SHALL be a validation error.

Unused catalog entries SHOULD produce a warning rather than an error.

## 6. Rule `when` expression

A Rule MAY declare a `when` expression composed only of named applicability
conditions.

A single condition MAY use scalar shorthand:

    when: windows.camera-installed

When more than one condition is involved, Boolean composition SHALL be
explicit:

    when:
      all_of:
        - linux.gnome-installed
        - not: linux.containerized

A bare sequence of multiple condition identifiers SHOULD NOT be used because
the Boolean operator would be implicit.

`when` SHALL NOT contain:

- collection definitions;
- commands;
- queries;
- target-state comparisons;
- collector/capability selection;
- executable expressions.

Those semantics belong in the referenced applicability Assessment Methods.

## 7. Effective Rule applicability

For an effectively selected Rule:

    effective applicability =
        Benchmark Platform expression
        AND
        Rule when expression

A Rule with no `when` expression inherits the Benchmark Platform scope.

The compliance Assessment for a Rule SHALL run only when effective
applicability is true.

If the Rule applicability expression is false, the Rule result SHALL be
`not_applicable` or the final standardized equivalent, and the compliance
Assessment SHALL NOT be executed.

If applicability cannot be determined because of an error, unsupported
capability, or missing required input, the processor SHALL NOT coerce that
condition to `not_applicable`, `pass`, or `fail`. It SHALL use the
appropriate indeterminate/not-evaluated/error result state defined by the final
result vocabulary.

## 8. Applicability and Rule selection

Rule selection and Rule applicability are distinct.

A disabled Rule is outside the effective policy selection and need not have
applicability evaluated.

An enabled but inapplicable Rule remains part of the effective policy and is
reported as not applicable.

Tailoring SHALL NOT rewrite the Rule's applicability expression or replace an
applicability Assessment Method.

If an organization does not wish to assess an otherwise applicable publisher
Rule, it SHOULD express that as Tailoring Rule selection rather than altering
the applicability logic.

## 9. Applicability and Parameters

An applicability Assessment MAY consume typed Parameters or Organizational
Input when the condition genuinely depends on organization-defined expected
state.

Such values remain subject to the normal policy-data isolation rules.

Missing required input SHALL make applicability indeterminate; it SHALL NOT be
silently interpreted as false.

## 10. Reuse and evaluation

Applicability conditions SHOULD be reusable across Rules and, when semantics
are truly equivalent, across Benchmarks.

A processor MAY cache the result of a reusable applicability Assessment during
one run when doing so cannot change semantics.

Caching SHALL NOT change result truth or hide an evaluation error.

## 11. Result provenance

Results SHOULD preserve enough information to explain applicability decisions,
including:

- effective Benchmark Platform result;
- Rule applicability condition identifiers;
- final Rule applicability outcome;
- structured reason/evidence when needed for diagnosis.

A consumer SHOULD NOT need to reconstruct legacy CPE/OVAL component graphs to
understand why a Rule was not applicable.

## 12. Manual not-applicable outcome

Pre-evaluated Rule applicability and the Manual Assessment
`not_applicable` outcome are related but distinct.

Applicability SHOULD be determined before the Manual Assessment when it can be
expressed reliably.

The Manual Assessment `not_applicable` outcome remains available for cases
where applicability can only be established by the prescribed human review.

## 13. Legacy CPE/XCCDF migration

SCAP 1.4 CPE/XCCDF applicability SHALL be interpreted semantically during
migration.

When product identity and additional applicability can be separated exactly,
the converter SHOULD emit:

    Benchmark Platform
    AND
    Rule applicability

When decomposition cannot be proven equivalent, the converter SHALL preserve a
lossless condition for review rather than silently inventing a split.

Legacy CPE names MAY remain as identifiers/provenance, but SCAP-NG execution
SHALL NOT depend on a scanner possessing hard-coded knowledge of those names.
