# Profile Rule-Selection Semantics

**Status:** working design decision  
**Iteration:** 002  
**Scope:** native SCAP-NG Benchmark/Profile rule-selection semantics and SCAP 1.4 migration

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Design principle

SCAP-NG Profiles describe **policy differences**, not expanded snapshots of a
Benchmark.

The amount of serialized Profile content SHOULD correspond to the amount of
semantic policy difference being expressed.

A Profile that does not change Rule selection SHALL contain no Rule-selection
state.

## Benchmark membership establishes default Rule selection

Every Rule contained in a Benchmark SHALL be enabled by default.

A native SCAP-NG Rule SHALL NOT require an `enabled: true`, `selected: true`,
or equivalent property merely to participate in its Benchmark.

Benchmark membership is the default enablement state.

This avoids moving redundant selection state from Profiles into Rules.

## Profile Rule selection is subtractive only

The Rule-selection function of a Profile SHALL be subtractive.

A Profile MAY disable zero or more Rules contained in its Benchmark.

A Profile SHALL NOT explicitly enable a Rule.

A Profile SHALL NOT introduce a Rule that is not already contained in its
Benchmark.

The native syntax SHOULD expose only the operation that is semantically valid,
for example:

    profile:
      id: disa.cat-i-only
      title: CAT I Only
      disabled_rules:
        - RHEL-09-211015
        - RHEL-09-211020

Native syntax SHALL NOT provide a generic Boolean Rule-selection map whose
values can redundantly restate inherited enablement, for example:

    # Invalid native SCAP-NG
    selections:
      RHEL-09-211010: true
      RHEL-09-211015: true

A conformant validator SHALL reject native Profile content that attempts to
explicitly re-enable a Rule or otherwise serialize Rule-selection state
identical to the inherited effective state.

## Profiles with no Rule-selection difference

A publisher MAY define multiple Profiles with distinct identities, titles,
references, or other metadata even when they produce the same effective Rule
selection.

When such a Profile does not disable any Rules, it SHALL contain no
Rule-selection data.

Example:

    profile:
      id: disa.mac-1-classified
      title: I - Mission Critical Classified

The absence of `disabled_rules` means the Profile uses the Benchmark Rule set
without modification.

This preserves distinct publisher-facing Profile identities without repeating
the Benchmark's Rule membership.

## Profile inheritance

A Profile MAY extend one other Profile in the same Benchmark.

Multiple inheritance SHOULD NOT be supported.

For Rule selection, inheritance is monotonic and subtractive:

1. all Benchmark Rules begin enabled;
2. the parent Profile disables zero or more Rules;
3. the child Profile may disable additional Rules;
4. the child Profile SHALL NOT re-enable a Rule disabled by an ancestor.

Cycles are invalid.

A publisher needing a different Rule combination SHOULD define another Profile
from the Benchmark or an appropriate common parent rather than create
re-enablement semantics.

Profile inheritance MAY also carry other permitted policy state such as
Parameter bindings, subject to the rules governing those properties.

## Parameters and other Profile policy

The subtractive-only restriction applies specifically to Rule selection.

Profiles MAY still perform other policy functions explicitly permitted by the
SCAP-NG specification, including binding publisher-resolved Parameters or
refining policy properties declared tailorable.

Profiles SHALL NOT use those mechanisms to alter Assessment Method execution
semantics.

## Canonical serialization

Canonical SCAP-NG serialization SHALL omit inherited or default Rule-selection
state.

Authoring tools MAY present a fully expanded user interface showing every
effective Rule as checked/unchecked, but serialization SHALL emit only the
Profile's disable delta.

A serializer SHALL NOT emit an empty `disabled_rules` collection when
omitting the property communicates the same state.

This makes semantic changes obvious in source review and version-control diffs.

## XCCDF up-conversion

An SCAP 1.4/XCCDF up-converter SHALL resolve the effective Rule-selection state
of each source Profile against the source Benchmark before emitting native
SCAP-NG.

For every converted Profile, the converter SHALL:

1. preserve the distinct source Profile identity, title, and relevant
   provenance;
2. determine the effective selected Rule set according to XCCDF semantics;
3. emit only Rules that are disabled relative to the converted Benchmark;
4. omit explicit source selections that merely restate Benchmark-default
   enablement;
5. report any source construct that cannot be represented losslessly by the
   subtractive native model instead of silently changing policy.

The conversion is canonicalization of an equivalent policy representation; it
does not change publisher policy.

### DISA RHEL 9 migration evidence

The NIWC-enhanced DISA RHEL 9 V2R9 benchmark used during iteration 002 contains
445 Rules. None has an explicit XCCDF Rule `selected` attribute, so XCCDF
default behavior selects all 445 Rules.

Its nine standard MAC Profiles each explicitly select all 445 Rules. Those
4,005 explicit positive selections produce no effective Rule-selection
difference from the Benchmark and therefore convert to nine distinct
metadata-only SCAP-NG Profiles.

The same source contains:

- `CAT I Only`: 417 explicit deselections, which convert to 417
  `disabled_rules` entries;
- `Disable Slow Rules`: 7 explicit deselections, which convert to 7
  `disabled_rules` entries.

This example demonstrates why Profile source SHOULD expose semantic difference
rather than serialization expansion.

## Result/audit semantics

Compact Profile source SHALL NOT reduce auditability.

Assessment results SHALL identify the selected Profile and SHALL retain the
fully resolved effective per-Rule selection state used for the assessment.

Historical results therefore remain interpretable even if the Benchmark,
Profile inheritance hierarchy, or Group membership changes later.

## Validation guardrails

A conformant native validator SHALL reject:

- explicit Rule enablement in a Profile;
- references to Rules not contained in the Benchmark;
- attempts by a child Profile to re-enable a Rule disabled by an ancestor;
- Profile inheritance cycles;
- duplicate Rule identifiers in `disabled_rules`;
- redundant serialization of inherited/default Rule-selection state.

An up-conversion tool MAY accept broader legacy constructs as input, but its
native SCAP-NG output SHALL satisfy these canonical constraints.

## SCAP 1.4 analog

| SCAP-NG concept | XCCDF 1.2 analog | Relationship |
| --- | --- | --- |
| Benchmark membership implies enabled | Rule default `selected=true` behavior | simplified and made canonical |
| `disabled_rules` | Profile `select selected="false"` | retained as explicit delta |
| explicit Profile enablement | Profile `select selected="true"` | not representable natively when it merely restates/increases inherited selection |
| metadata-only Profile | Profile whose effective selection equals Benchmark defaults | normalized representation |
| single Profile inheritance | Profile `@extends` | retained with monotonic Rule-disable semantics |
| resolved Rule state in results | XCCDF TestResult rule-result population | preserved as audit evidence |
