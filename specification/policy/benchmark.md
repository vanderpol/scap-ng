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

A Rule policy object SHALL own Rule-specific policy semantics, including as
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
