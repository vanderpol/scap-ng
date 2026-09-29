# Benchmark, Rule, and Group Model

**Status:** pre-alpha normative draft

## 1. Purpose of a Benchmark

A Benchmark is the authoritative publisher policy container for a checklist,
security configuration baseline, vulnerability checklist, inventory policy, or
other supported SCAP-NG policy use case.

A Benchmark defines the policy universe against which Profiles and Tailoring
operate. It SHALL NOT be treated merely as a directory manifest.

A Benchmark SHALL have:

- a stable logical identity;
- a human-readable title;
- a publication version or revision;
- publisher identity;
- a target Platform expression;
- one or more Rule members.

A Benchmark SHOULD also provide, when applicable:

- description;
- publication/status metadata;
- references;
- meaningful Groups;
- policy Parameters;
- publisher-defined Profiles;
- an applicability catalog.

Stable Benchmark identity and Benchmark version SHALL be distinct concepts.
Revisions of the same logical Benchmark SHOULD retain the same logical
Benchmark identity and change the version/revision.

## 2. Benchmark as the publisher baseline

Benchmark Rule membership establishes the publisher baseline.

Every Rule that is a member of the Benchmark SHALL be enabled in the
unprofiled Benchmark baseline.

The baseline therefore requires no positive Rule-selection list beyond
Benchmark membership.

A Profile MAY reduce that baseline as defined in
`profiles-and-tailoring.md`.

An external Tailoring artifact MAY subsequently modify the resolved publisher
selection as defined in `profiles-and-tailoring.md`.

If neither a Profile nor Tailoring is selected, the effective Rule selection is
the Benchmark baseline.

## 3. Benchmark source ownership

The Benchmark object SHALL own Benchmark-wide policy structure, including:

- Benchmark identity/version;
- publisher metadata;
- Platform expression and Platform Assessment bindings;
- applicability-catalog reference;
- Rule membership;
- Group definitions;
- Profile catalog/references;
- Benchmark-scoped Parameter definitions or references.

A Rule object SHALL own Rule-specific semantics, including as
applicable:

- stable Rule identity;
- Rule revision;
- title;
- severity;
- discussion/rationale;
- external identifiers and references;
- Rule-specific applicability expression;
- Assessment Method references;
- human-readable remediation.

The Benchmark SHALL NOT duplicate Rule-specific properties merely to create a
centralized snapshot.

Generated indexes, review views, and compiled packages MAY repeat resolved data
when useful, but such derived views SHALL NOT become competing authoring
sources of truth.

## 4. Rule membership and references

A Benchmark SHALL reference each Rule member explicitly.

Authoring source MAY use file paths for those forward references.

A compiler SHALL resolve source paths to stable Rule identities before
producing scanner-facing content.

Filename, path, directory membership, or naming convention SHALL NOT by itself
create Benchmark membership.

A Rule referenced by a Benchmark SHALL resolve exactly once.

Duplicate Rule identities within one Benchmark SHALL be invalid.

A Benchmark SHALL NOT gain new Rule members through a Profile or Tailoring
artifact.

## 5. Platform scope

A Benchmark SHALL define its target Platform scope explicitly.

The Platform expression MAY combine named Platform predicates using explicit
Boolean composition when required.

For example, a Benchmark MAY target any of several equivalent operating-system
products, or MAY require more than one product identity when that is intrinsic
to the Benchmark's intended target.

Role, feature, installation-state, and configuration predicates SHOULD be kept
as applicability conditions rather than encoded into Platform identity when
the concepts are separable.

Platform evaluation semantics are defined in
`platform-and-applicability.md`.

## 6. Applicability catalog

When any Rule references named applicability conditions, the Benchmark SHALL
declare the applicability catalog used to resolve those identifiers.

The catalog relationship SHALL be explicit.

No filename such as `applicability.yaml` has implicit meaning.

A Benchmark SHALL NOT rely on scanner-specific knowledge to resolve an
applicability identifier.

## 7. Profiles

Publisher-defined Profiles belong to the Benchmark policy publication.

A Benchmark MAY contain or explicitly reference zero or more Profiles.

A Profile is optional. Absence of a selected Profile means the unprofiled
Benchmark baseline is used.

A Benchmark/Profile implementation SHALL NOT require a Profile whose only
purpose is to repeat that all Benchmark Rules are selected.

Profile semantics are defined in `profiles-and-tailoring.md`.

## 8. Parameters

A Benchmark MAY define typed policy Parameters.

A Parameter definition SHALL be distinct from its effective value.

Effective values may come from the Benchmark, a Profile, Tailoring, or
Organizational Input according to the Parameter model.

Parameter values SHALL NOT modify Assessment execution semantics.

## 9. Groups

Groups SHALL represent meaningful logical collections of Rules and, when
useful, Parameters.

A Group SHALL have a stable identifier and human-readable title.

A Group MAY contain child Groups and multiple Rules.

Group membership SHALL NOT change:

- Rule applicability;
- Assessment Method behavior;
- Parameter binding;
- Rule truth.

SCAP-NG SHOULD NOT create one-Rule Groups solely to reproduce historical XCCDF
wrapper structure.

Profile or Tailoring operations that use Groups are policy-authoring
conveniences. Such operations SHALL be resolved against the exact Benchmark
version and normalized to effective per-Rule state before execution.

## 10. Benchmark metadata and publication lifecycle

A Benchmark SHOULD provide enough publication metadata for a consumer to
distinguish:

- logical Benchmark identity;
- exact publication version;
- publisher;
- publication/release state;
- release or effective date when supplied by the publisher.

A compiled package SHALL identify the exact Benchmark version it contains.

Tailoring authored for one Benchmark version SHALL NOT silently bind to another
version.

Migration/rebase tooling MAY assist with moving Tailoring to a newer Benchmark,
but that operation SHALL be explicit.

## 11. Self-contained execution package

Human authoring source MAY reference shared Rules, Assessments, Platform
Assessments, applicability Assessments, and other reusable objects.

The compiled scanner-facing package for a Benchmark SHALL contain the complete
resolved content needed to execute that Benchmark.

A scanner SHALL NOT depend on mutable external source libraries whose content
could change independently after the package was created.

## 12. Stable identity and publisher identifiers

Stable SCAP-NG logical identity SHALL be distinct from publisher revision
identifiers.

Publisher-specific IDs such as STIG IDs, vulnerability IDs, legacy XCCDF Rule
IDs, CCI identifiers, and CPE names SHOULD be preserved using typed identifier
or reference structures where appropriate.

Legacy metadata SHALL NOT force SCAP-NG to overload fields with unrelated
semantics.

## 13. Publisher extensions

SCAP-NG SHALL provide a constrained extension mechanism for publisher-specific
data that has no standard semantic field.

An extension SHALL NOT:

- redefine standard SCAP-NG fields;
- modify Assessment Method implementation;
- bypass Parameter restrictions;
- override Platform/applicability processing;
- silently change Rule selection.

## 14. SCAP 1.4 relationship

The SCAP-NG Benchmark is the direct policy descendant of the XCCDF Benchmark,
but intentionally removes the requirement that policy, checking-system
indirection, applicability machinery, and variable exchange remain coupled in
one XML component architecture.

SCAP-NG preserves the high-level requirements that a Benchmark have stable
identity/version, target scope, policy Rules, and deterministic processing,
while moving implementation details into explicit referenced objects.


## 15. Benchmark processing model

A processor SHALL treat Benchmark processing as a deterministic sequence.

For a requested Benchmark execution, the processor SHALL conceptually:

1. identify the exact Benchmark identity and version;
2. resolve all Rule members;
3. resolve the Benchmark Platform expression and Platform Assessment bindings;
4. resolve the applicability catalog, when present;
5. resolve the selected publisher Profile, when present;
6. resolve Tailoring, when present;
7. resolve effective Parameter values and required Organizational Input;
8. freeze the effective Rule-selection state;
9. evaluate the Benchmark Platform expression;
10. evaluate Rule applicability only for effectively selected Rules;
11. execute the selected Assessment Methods for applicable Rules, preserving each Assessment's declared class and purpose; and
12. produce results that identify the exact effective policy used.

A build/compiler MAY perform source resolution and normalization before run
time, but the observable semantics SHALL be equivalent to this processing
model.

## 16. Benchmark validation requirements

A Benchmark SHALL fail validation when:

- its logical identity is missing or ambiguous;
- its publication version is missing when version binding is required;
- a Rule reference cannot be resolved;
- two Rule references resolve to the same logical Rule identity;
- a Platform Assessment reference cannot be resolved;
- a referenced applicability catalog cannot be resolved;
- a Profile references a Rule not contained in the Benchmark;
- a Group references an unknown Rule or child Group;
- a Parameter reference cannot be resolved;
- source references resolve ambiguously.

A validator SHOULD warn about:

- unused applicability catalog entries;
- empty Groups;
- metadata-only Profiles that are semantically identical and appear accidental;
- Rule membership that is not represented in any meaningful Group when the
  publisher normally uses grouping.

Warnings SHALL NOT silently change policy.

## 17. Benchmark source example

Illustrative source:

    benchmark:
      id: disa.windows11.stig
      title: Microsoft Windows 11 Security Technical Implementation Guide
      version: V2R10

      publisher:
        name: Defense Information Systems Agency
        short_name: DISA

      platforms:
        any_of:
          - id: windows.11
            assessment: assessments/automated/platforms/windows-11.assessment.yaml

      applicability: applicability.yaml

      rules:
        - rules/WN11-00-000020.rule.yaml
        - rules/WN11-00-000050.rule.yaml
        - rules/WN11-CC-000005.rule.yaml

      profiles:
        - profiles/cat-i-only.profile.yaml

The example is illustrative. Exact serialization remains subject to schema
stabilization.

## 18. Source-tree organization

A Benchmark source tree SHOULD make policy ownership obvious.

A typical source tree is:

    benchmark.yaml
    applicability.yaml
    rules/
      <rule>.rule.yaml
    profiles/
      <profile>.profile.yaml
    assessments/
      manual/
      automated/

Shared reusable content MAY live outside the Benchmark tree.

Repository layout is an authoring convention. A processor SHALL NOT infer
object type, identity, or semantics solely from the directory structure.

## 19. Benchmark execution identity

Results SHALL identify the exact Benchmark publication that was executed.

A Benchmark result reference SHOULD include:

- stable Benchmark logical identity;
- publication version/revision;
- immutable compiled-package identity when available;
- selected Profile identity, if any;
- Tailoring identity/version, if any.

This information SHALL be sufficient to distinguish two executions that used
different policy publications even when the Benchmark logical identity is the
same.

## 20. Benchmark replacement and supersession

A new Benchmark publication MAY supersede an older publication while retaining
the same logical Benchmark identity.

Supersession SHALL NOT mutate historical result meaning.

Profiles and Tailoring bound to an older publication SHALL NOT silently
retarget to the newer publication.

Rebase/migration tooling MAY produce a new Profile or Tailoring artifact for
the newer Benchmark after validating every referenced Rule, Group, and
Parameter decision.


## 21. Worked source examples

The current five-Rule design-review source trees demonstrate this Benchmark
model:

    research/iterations/002/examples/source/rhel9/
    research/iterations/002/examples/source/windows11/

They include Benchmark Platform bindings, Rule membership, policy files,
Manual Assessments, Automated Assessments, and, for Windows 11, a
Benchmark-scoped applicability catalog.

These examples are non-normative syntax demonstrations. Where example syntax
and normative requirements diverge during pre-alpha development, the
specification requirement controls.


## 22. Assessment class neutrality

A Benchmark MAY contain Rules whose selected Assessment Methods use different
standardized Assessment classes.

The Benchmark processing model SHALL NOT assume that every Rule is a
`compliance` Assessment merely because compliance is a primary SCAP-NG use
case.

Rule outcome interpretation SHALL use the selected Assessment Method's declared
class as defined in `../assessment/assessment-method.md`.

Publisher-specific Rule metadata that is not part of the standardized SCAP-NG
Policy vocabulary SHALL use the constrained extension mechanism rather than
being promoted implicitly into core Rule fields.


## 23. Benchmark use case

A Benchmark SHALL declare a high-level `use_case` describing the primary
SCAP-NG use case of that Benchmark.

The initial inherited use-case model is derived from the SCAP 1.4 source
data-stream use-case distinction. The current candidate native vocabulary is:

- `compliance`;
- `vulnerability`;
- `inventory`;
- `other`.

The final naming of `compliance` versus the SCAP 1.4 term
`CONFIGURATION` remains subject to standards review.

Benchmark `use_case` SHALL remain distinct from Assessment `class`.
A compliance Benchmark MAY contain inventory-class Assessments used for
Platform or Rule applicability, and MAY contain patch-class Assessments where
appropriate.

Iteration 003 uses `use_case: compliance` for the RHEL 9 STIG conversion
because the Benchmark's primary purpose is security-configuration compliance
evaluation.

Whether a future SCAP-NG Benchmark publication may contain more than one
Benchmark remains an open governance question. The current v1 design direction
is one executable Benchmark per SCAP-NG Benchmark publication.
