# Benchmark, Profile, and Group Structure

**Status:** working design decision  
**Iteration:** 002  
**Scope:** native SCAP-NG policy source

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Benchmark

A Benchmark is the authoritative policy container. It SHALL provide the
identity and version of the policy publication, publisher metadata, platform
scope, Groups, Rules, policy Parameters, and publisher-defined Profiles.

Assessment implementation is separate. Rules bind to Assessment Methods rather
than embedding executable implementation into policy structure.

## Profiles

A Profile is a publisher-defined policy selection within a Benchmark.

A Profile MAY:
- select or deselect Rules;
- select or deselect Groups as authoring shorthand;
- bind publisher-resolved policy Parameters;
- refine policy attributes explicitly declared tailorable by the Benchmark.

A Profile SHALL NOT:
- replace Assessment Methods;
- select executable implementations;
- alter collectors, queries, operations, privileges, or other scanner behavior.

Profiles are part of the Benchmark because they represent publisher policy.

## Groups

Groups SHALL represent meaningful logical collections of related Rules and,
when useful, Parameters.

A Group:
- SHALL have a stable identifier;
- SHALL have a human-readable title;
- MAY contain child Groups;
- MAY contain multiple Rules;
- SHOULD describe a coherent policy topic, subsystem, control family, or
  configuration area.

Groups MAY be nested recursively. Implementations SHALL NOT assume a fixed
maximum nesting depth defined by the format, although content authors SHOULD
prefer the shallowest hierarchy that communicates the policy clearly.

A one-Rule Group SHOULD NOT be created solely to imitate historical STIG XCCDF
wrapping.

### Automatic grouping during migration

An up-converter MAY infer useful Groups from source content when grouping does
not alter Rule semantics.

Automatic grouping SHOULD use multiple signals, such as:
- policy title and discussion;
- check/fix text;
- affected configuration artifact or subsystem;
- Assessment Method capability and collected object type;
- existing meaningful source Group ancestry;
- control/reference metadata.

Automatic grouping SHALL be conservative. Rules for which a meaningful group
cannot be determined with sufficient confidence SHALL remain valid and SHOULD
be placed in a clearly identified review Group such as:

    needs-grouping

The absence of a confident Group SHALL NOT block conversion of an otherwise
valid Rule.

A migration report SHOULD identify the percentage of Rules automatically
grouped and the Rules requiring manual review. For mature benchmark families,
the project SHOULD target automatic useful grouping of at least 90 percent of
Rules, but a converter SHALL NOT fabricate a grouping merely to reach that
target.

### Grouping is not assessment semantics

Group membership SHALL NOT alter:
- Rule applicability;
- Assessment Method behavior;
- Parameter binding;
- result computation.

If a Profile or Tailoring artifact operates on a Group, the processor SHALL
resolve that operation against the exact referenced Benchmark version. Results
SHALL retain effective per-Rule selections so a later change in Group
membership cannot obscure what was actually assessed.

## Historical guidance

XCCDF 1.2 Groups were capable of containing multiple Rules, Values, and nested
Groups. Older NIST/USGCB content used that capability to create meaningful
sections such as security-options and system-services groupings.

SCAP-NG intentionally preserves that useful structural concept while avoiding
the common STIG pattern of mechanically wrapping each Rule in its own Group.

## SCAP 1.4 analog

| SCAP-NG concept | SCAP 1.4 analog | Relationship |
| --- | --- | --- |
| Benchmark | XCCDF Benchmark | direct descendant, with assessment implementation separated |
| Profile | XCCDF Profile | direct descendant with tighter policy/execution boundary |
| Group | XCCDF Group | direct descendant, restored to meaningful multi-Rule organization |
| needs-grouping | none | NG migration/review convention |
