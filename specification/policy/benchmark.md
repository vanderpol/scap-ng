# Benchmark, Rule, and Group Model

**Status:** pre-alpha normative draft

## 1. Benchmark

A Benchmark is the authoritative policy container for a published checklist or
security policy.

A Benchmark SHALL provide or reference, as applicable:

- stable Benchmark identity;
- Benchmark version/revision;
- publisher metadata;
- target Platform specification;
- Rule membership;
- meaningful Groups;
- policy Parameters;
- publisher-defined Profiles;
- an applicability catalog when Rule-specific applicability conditions are
  used.

Assessment implementation SHALL remain separate from Benchmark policy
structure.

## 2. Rule membership

A Rule contained by a Benchmark is enabled by default.

Benchmark membership therefore establishes the publisher's complete baseline
Rule set.

A Benchmark SHALL NOT require a Profile to restate that every baseline Rule is
enabled.

## 3. Rule policy

Rule policy source SHALL own Rule-specific policy semantics, including as
applicable:

- stable Rule identity;
- Rule revision;
- title;
- severity;
- discussion/rationale;
- external identifiers and references;
- Rule-specific applicability references;
- Assessment Method references;
- human-readable remediation.

The Benchmark SHALL NOT duplicate those Rule properties merely to create a
centralized index.

Generated indexes and Rule-centric views MAY repeat them as derived data.

## 4. Groups

Groups SHALL represent meaningful logical collections of Rules and, when
useful, Parameters.

A Group SHALL have a stable identity and human-readable title.

A Group MAY contain child Groups and multiple Rules.

Group membership SHALL NOT alter Rule applicability, Assessment execution,
Parameter binding, or result truth.

SCAP-NG SHOULD NOT create one-Rule Groups merely to preserve mechanical XCCDF
wrappers that provide no useful organization.

## 5. Stable identity

Stable logical identity SHALL be distinct from revision/version.

A revision to the same logical Rule SHALL NOT require a new SCAP-NG Rule
identity merely because a publisher's legacy identifier embeds a revision.

Legacy publisher identifiers SHOULD be preserved using typed identifier
structures rather than by overloading normative identity or version fields.

## 6. Publisher extensions

SCAP-NG SHALL provide a constrained extension mechanism for publisher-specific
data that has no standard semantic field.

An extension SHALL NOT redefine standard SCAP-NG semantics or modify Assessment
execution behavior.
