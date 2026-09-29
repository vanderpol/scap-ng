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

## 3. Inventory identity versus applicability identity

SCAP-NG target results MAY report standardized product identifiers, including
CPE identifiers, for the observed operating system and applications.

This inventory-reporting use case is independent of whether CPE participates in
Benchmark Platform or Rule applicability evaluation.

A product identifier reported in target inventory SHALL NOT automatically make
content applicable, and a content Platform identifier SHALL NOT automatically
be emitted as observed target inventory without supporting collection evidence.

The normal SCAP-NG production path is:

    Platform Assessment collects product evidence
        -> Platform Boolean result
        -> optional descriptive product-inventory facts
        -> target.inventory in the result package

Inventory facts emitted by a Platform Assessment are side outputs. They SHALL
NOT feed back into that Platform decision, Rule selection, Rule applicability,
or compliance truth.

Operating-system Platform Assessments SHOULD emit an operating-system product
inventory fact when the product identity can be established reliably.

Application Platform Assessments SHOULD emit an application product inventory
fact when the product identity can be established reliably.

## 4. External platform identifiers

A Platform MAY declare one or more external product/platform identifiers in
addition to its stable SCAP-NG logical identifier.

External identifiers MAY include CPE identifiers.

Illustrative syntax:

    platform:
      id: windows.11
      identifiers:
        - scheme: cpe
          version: "2.3"
          value: "cpe:2.3:o:microsoft:windows_11:*:*:*:*:*:*:*:*"

The external identifier does not replace the SCAP-NG Platform identifier.

By default, a declared CPE identifier is identity/provenance data. It SHALL NOT
be treated as executable proof of Platform truth merely because a processor
recognizes the string.

A future conformance profile or standardized capability MAY define executable
CPE name matching. Such a mechanism SHALL identify the supported CPE version
and matching semantics explicitly.

SCAP-NG's generic external-identifier model SHOULD remain version-neutral so a
future CPE revision can be represented without changing Platform logical
identity.

## 5. Benchmark Platform expression

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

## 6. What belongs in Rule applicability

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

## 7. Applicability catalog

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

In human-authored source, an applicability catalog entry SHALL explicitly
reference the Assessment source object it binds. The preferred authoring form
is an explicit relative source path, for example:

    applicability:
      - id: linux.gnome-installed
        assessment: assessments/applicability/linux.gnome-installed.assessment.yaml

A compiler SHALL resolve that authoring reference, verify that the referenced
Assessment's declared logical identity matches the resolved object, and replace
the source-path relationship with the stable Assessment logical identity in
compiled scanner-facing content.

Processors SHALL NOT discover an applicability Assessment merely by scanning
directories for a matching `assessment.id`. Physical co-location or filename
similarity is not a semantic binding.

Thus the two identities serve different purposes:

- applicability `id` is the stable condition identifier referenced by Rules;
- source `assessment` is the explicit authoring reference used to locate the
  bound Assessment before compilation;
- compiled content uses the resolved Assessment logical identity rather than a
  source filesystem path.

A processor SHALL resolve the identifier through the containing Benchmark's
catalog.

An undefined, duplicate, ambiguous, or unresolvable applicability identifier
SHALL be a validation error.

Unused catalog entries SHOULD produce a warning rather than an error.

## 8. Rule `when` expression

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

## 9. Effective Rule applicability

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

## 10. Applicability and Rule selection

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

## 11. Applicability and Parameters

An applicability Assessment MAY consume typed Parameters or Organizational
Input when the condition genuinely depends on organization-defined expected
state.

Such values remain subject to the normal policy-data isolation rules.

Missing required input SHALL make applicability indeterminate; it SHALL NOT be
silently interpreted as false.

## 12. Reuse and evaluation

Applicability conditions SHOULD be reusable across Rules and, when semantics
are truly equivalent, across Benchmarks.

A processor MAY cache the result of a reusable applicability Assessment during
one run when doing so cannot change semantics.

Caching SHALL NOT change result truth or hide an evaluation error.

## 13. Result provenance

Results SHOULD preserve enough information to explain applicability decisions,
including:

- effective Benchmark Platform result;
- Rule applicability condition identifiers;
- final Rule applicability outcome;
- structured reason/evidence when needed for diagnosis.

A consumer SHOULD NOT need to reconstruct legacy CPE/OVAL component graphs to
understand why a Rule was not applicable.

## 14. Manual not-applicable outcome

Pre-evaluated Rule applicability and the Manual Assessment
`not_applicable` outcome are related but distinct.

Applicability SHOULD be determined before the Manual Assessment when it can be
expressed reliably.

The Manual Assessment `not_applicable` outcome remains available for cases
where applicability can only be established by the prescribed human review.

## 15. Legacy CPE/XCCDF migration

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

When a legacy CPE name or CPE Applicability Language expression materially
affects applicability, Stage-1 migration SHALL preserve that semantic effect.
The converter SHOULD decompose the source into native Platform identity and Rule
applicability when equivalence can be proven. Otherwise it SHALL preserve the
legacy matching/applicability semantics through an explicit compatibility
Assessment/capability or report a conversion blocker.

A processor SHALL NOT substitute simple string equality for CPE name-matching
or CPE Applicability Language semantics.

If CPE matching depends on an external dictionary, the effective dictionary
identity/version SHOULD be visible in execution provenance when that dependency
can affect applicability truth.


## 16. Applicability processing algorithm

For each effectively selected Rule, a processor SHALL evaluate applicability
in the following order:

1. evaluate the Benchmark Platform expression;
2. if the Benchmark Platform expression is false, do not execute Rule
   compliance Assessments;
3. if the Benchmark Platform expression is indeterminate or errors, propagate
   an appropriate non-compliance result state rather than treating the
   Benchmark as simply not applicable;
4. if the Platform expression is true and the Rule has no `when` expression,
   the Rule is applicable;
5. if the Rule has a `when` expression, resolve every named condition through
   the Benchmark applicability catalog;
6. evaluate the Boolean `when` expression;
7. execute the Rule compliance Assessment only when the effective Rule
   applicability is true.

Rule selection SHALL be resolved before this algorithm. A disabled Rule does
not require applicability evaluation.

## 17. Applicability truth semantics

Applicability truth SHALL be distinct from compliance truth.

For an enabled Rule:

| Platform | Rule `when` | Effective applicability | Compliance Assessment |
| --- | --- | --- | --- |
| true | absent | applicable | execute |
| true | true | applicable | execute |
| true | false | not applicable | do not execute |
| false | any | Benchmark out of scope | do not execute |
| error/indeterminate | any | indeterminate | do not coerce to N/A |
| true | error/indeterminate | indeterminate | do not coerce to N/A |

The final result-state names for Benchmark-out-of-scope and indeterminate
applicability remain subject to the common results vocabulary.

## 18. Applicability Assessment contract

An applicability catalog entry SHALL resolve to an Assessment Method whose
result can be interpreted as Boolean applicability truth or an explicit
indeterminate/error state.

An applicability Assessment:

- MAY use any normal SCAP-NG collection capability;
- MAY use derived values and Boolean assertions;
- MAY consume typed expected-state Parameters when genuinely necessary;
- SHALL NOT determine compliance for the consuming Rule;
- SHALL NOT change Rule selection;
- SHALL NOT mutate Benchmark or Tailoring policy.

The same applicability Assessment MAY be reused by multiple Rules.

## 19. Applicability catalog example

Illustrative catalog:

    applicability:
      windows.member-workstation:
        assessment: assessments/automated/applicability/windows-member-workstation.assessment.yaml

      windows.camera-installed:
        assessment: assessments/automated/applicability/windows-camera-installed.assessment.yaml

Illustrative Rule:

    rule:
      id: WN11-EXAMPLE
      when:
        all_of:
          - windows.member-workstation
          - windows.camera-installed

The Rule does not repeat either Assessment path.

## 20. Shared condition evaluation

When multiple Rules reference the same applicability condition during one run,
a processor SHOULD evaluate the condition once and reuse the result when:

- the Assessment is deterministic for the run;
- its effective inputs are identical;
- its target scope is identical; and
- reuse cannot alter error or evidence semantics.

A processor that reuses the result SHALL preserve enough result information to
show which Rules depended on the condition.

## 21. Applicability evidence

When a Rule is reported as not applicable, the result SHOULD identify the
condition or Boolean branch that made it inapplicable.

Example:

    applicability:
      outcome: false
      decisive_condition: windows.camera-installed
      message: Camera feature is not installed.

For complex Boolean expressions, the result SHOULD preserve the decisive
applicability explanation without duplicating the complete static Assessment
definition.

## 22. Applicability versus exceptions

Applicability SHALL describe whether a requirement logically applies to the
target.

Applicability SHALL NOT be used as a generic waiver or exception mechanism.

An organization wishing to omit an otherwise applicable Rule from its local
policy SHALL use Tailoring Rule selection or another explicitly standardized
policy-exception mechanism rather than falsifying target applicability.


## 23. Worked source example

The Windows 11 source example demonstrates a Benchmark-scoped applicability
catalog and reusable Rule applicability Assessments:

    research/iterations/002/examples/source/windows11/applicability.yaml
    research/iterations/002/examples/source/windows11/assessments/automated/applicability/

The RHEL 9 source example demonstrates a Benchmark with multiple alternative
Platform identities sharing the same Rule policy set:

    research/iterations/002/examples/source/rhel9/benchmark.yaml
    research/iterations/002/examples/source/rhel9/assessments/automated/platforms/

These examples are design-review source and do not freeze final serialization.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Benchmark, Rule, and Group Model](benchmark.md) · [Contents](../README.md) · [Next: Profiles and Tailoring →](profiles-and-tailoring.md)

<!-- spec-nav:end -->
