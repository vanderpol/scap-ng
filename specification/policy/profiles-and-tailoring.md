# Profiles and Tailoring

**Status:** pre-alpha normative draft

## 1. Distinct roles

A Profile is publisher policy contained within a Benchmark.

Tailoring is an external policy modification applied to a published Benchmark
or Profile.

SCAP-NG SHALL keep those concepts distinct.

## 2. Profile Rule selection

Benchmark membership establishes the default Rule-selection state: every Rule
in the Benchmark is enabled.

A Profile's Rule-selection behavior SHALL be subtractive only.

A Profile MAY disable Rules contained in the Benchmark.

A Profile SHALL NOT explicitly enable a Rule merely to restate Benchmark
membership.

A Profile SHALL NOT introduce a Rule that is not contained in the Benchmark.

A Profile that makes no Rule-selection changes SHALL contain no Rule-selection
state.

Illustrative form:

    profile:
      id: disa.cat-i-only
      disabled_rules:
        - RHEL-09-211015
        - RHEL-09-211020

## 3. Profile inheritance

A Profile MAY extend at most one other Profile in the same Benchmark.

Rule selection through inheritance SHALL remain monotonic and subtractive.

A child Profile MAY disable additional Rules.

A child Profile SHALL NOT re-enable a Rule disabled by an ancestor.

Profile inheritance cycles SHALL be invalid.

## 4. Profile Parameters

A Profile MAY bind publisher-resolved policy Parameter values.

A Profile SHALL NOT:

- replace Assessment Methods;
- choose collectors;
- provide commands, queries, scripts, or shell fragments;
- change comparison operators;
- change execution privileges;
- otherwise alter scanner execution semantics.

## 5. Tailoring

A Tailoring artifact SHALL be external to the Benchmark.

A Tailoring artifact SHALL identify the Benchmark, and where applicable the
Profile, against which it was authored.

Tailoring SHALL modify only policy surfaces explicitly permitted by the
Benchmark/specification.

Tailoring SHALL NOT redefine Benchmark Rule membership, Group hierarchy,
Assessment Method implementations, Platform Assessment implementations, or
other executable scanner behavior.

Tailoring MAY override an already-resolved publisher Parameter when that
Parameter is declared tailorable.

Supplying a value for a publisher Parameter intentionally left unresolved is
Organizational Input, not Tailoring.

## 6. Tailoring provenance

A Tailoring artifact SHOULD identify, where available:

- author;
- organization;
- approval or authorization reference;
- creation/modification time;
- source Benchmark identity/version;
- source Profile identity/version.

Results SHALL make clear when effective policy for a Rule or Parameter differs
from publisher policy because of Tailoring.

Tailoring provenance and Organizational Input provenance SHALL remain
distinguishable.

## 7. Group operations

If Tailoring or Profile processing refers to a Group, the operation SHALL be
resolved against the exact Benchmark version used for the assessment.

Results SHALL retain effective per-Rule selection state so later Group changes
cannot alter interpretation of historical results.

## 8. Open Tailoring issue

The exact native rule-selection operations permitted to an external Tailoring
artifact, including whether Tailoring may reverse a publisher Profile
deselection, remain under design.

Until that is resolved, this section SHALL NOT be interpreted as authorizing a
Tailoring artifact to re-enable Rules.
