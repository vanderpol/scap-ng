# Profiles and Tailoring

**Status:** pre-alpha normative draft

## 1. Distinct policy layers

SCAP-NG SHALL distinguish three policy layers:

1. **Benchmark baseline** — publisher Rule membership and Benchmark values;
2. **Profile** — a publisher-defined variation contained in the Benchmark;
3. **Tailoring** — an external organization/user modification to the resolved
   publisher policy.

Organizational Input is not a fourth tailoring layer. It supplies expected-state
data intentionally left unresolved by the publisher and is defined separately.

## 2. Profile Rule selection

Benchmark membership enables every Rule by default.

A Profile's Rule-selection behavior SHALL be subtractive only.

A Profile MAY disable Rules contained in its Benchmark.

A Profile SHALL NOT:

- explicitly enable a Rule merely to restate Benchmark membership;
- introduce a Rule not contained in the Benchmark;
- re-enable a Rule disabled by an ancestor Profile.

A Profile that does not change Rule selection SHALL contain no Rule-selection
state.

Illustrative source:

    profile:
      id: disa.cat-i-only
      disabled_rules:
        - RHEL-09-211015
        - RHEL-09-211020

Profiles describe differences from inherited publisher policy, not complete
selection snapshots.

## 3. Profile inheritance

A Profile MAY extend at most one other Profile in the same Benchmark.

Profile inheritance SHALL be acyclic.

For Rule selection, inheritance SHALL remain monotonic and subtractive.

A child Profile MAY disable additional Rules.

A child Profile SHALL NOT re-enable a Rule disabled by its parent or another
ancestor.

The effective publisher Profile selection is calculated before Tailoring is
applied.

## 4. Profile Parameter values

A Profile MAY bind publisher-resolved Parameter values.

A Profile SHALL NOT:

- replace Assessment Methods;
- select executable implementations;
- modify Platform/applicability Assessment implementations;
- provide commands, scripts, SQL, XPath, shell fragments, or other executable
  content;
- choose collectors, comparison operations, or privileges;
- otherwise alter scanner execution semantics.

## 5. Tailoring identity and binding

A Tailoring artifact SHALL be external to the Benchmark publication.

A Tailoring artifact SHALL identify:

- the exact Benchmark logical identity;
- the exact Benchmark version against which it was authored;
- the base Profile, if one is being tailored.

A Tailoring artifact that names a base Profile SHALL apply only after that
Profile has been resolved.

A Tailoring artifact SHALL NOT create a shadow Profile with the same identity
as a publisher Profile.

A Tailoring artifact SHALL NOT silently apply to a different Benchmark version.

## 6. Tailoring Rule selection

Unlike a publisher Profile, Tailoring exists specifically to record a local
departure from publisher policy.

Tailoring MAY therefore explicitly enable or disable Rules that are already
members of the referenced Benchmark.

This permits an organization to reverse a publisher Profile deselection when
that is the organization's deliberate tailored policy.

Tailoring SHALL NOT add a Rule that is not a member of the Benchmark.

Illustrative source:

    tailoring:
      benchmark:
        id: disa.rhel9.stig
        version: V2R9
      profile: disa.cat-i-only

      enabled_rules:
        - RHEL-09-211015

      disabled_rules:
        - RHEL-09-255040

A Rule SHALL NOT appear in both `enabled_rules` and `disabled_rules` in the
same effective Tailoring layer.

Every Tailoring selection change SHOULD support a human-readable justification
or external authorization reference.

## 7. Tailoring Group operations

Tailoring MAY provide authoring convenience operations that select or deselect
a Group.

A Group operation SHALL be resolved against the exact referenced Benchmark
version.

Before execution, Group operations SHALL be expanded into deterministic
per-Rule selection state.

If Group-level and Rule-level operations would produce contradictory state for
the same Rule, the Tailoring SHALL be rejected unless the final specification
defines an explicit deterministic precedence rule.

The current pre-alpha model prefers rejecting ambiguity over relying on source
order.

## 8. Tailoring Parameters

Tailoring MAY override a publisher-resolved Parameter only when that Parameter
is declared tailorable.

Supplying a value for a Parameter intentionally left unresolved for the
organization is Organizational Input, not Tailoring.

Tailoring and Organizational Input SHALL remain distinguishable in source and
results.

## 9. Tailoring boundary

Tailoring SHALL NOT modify:

- Benchmark Rule membership;
- Group hierarchy;
- Rule identity;
- Rule title/discussion/remediation;
- Rule applicability expression;
- Platform definitions;
- applicability-catalog mappings;
- Assessment Method references;
- Assessment Method implementations;
- collector/capability selection;
- commands, queries, operations, privileges, or other execution semantics.

A future specification revision MAY standardize additional policy surfaces such
as severity override, but an implementation SHALL NOT invent such mutation
semantics implicitly.

## 10. Tailoring layering

A Tailoring artifact MAY extend at most one other Tailoring artifact when both
target the same Benchmark identity/version and compatible base Profile.

Tailoring inheritance SHALL be acyclic.

Layers SHALL be applied from parent to child.

A child Tailoring MAY override the parent's Rule-selection or tailorable
Parameter decisions because both layers are explicitly local policy, but the
final effective state SHALL be deterministic.

Tooling SHOULD flatten Tailoring inheritance before scanner execution.

## 11. Effective selection algorithm

The effective Rule selection SHALL be resolved in this order:

1. start with every Benchmark Rule enabled;
2. apply the selected publisher Profile and its ancestors, disabling Rules;
3. apply Tailoring layers, explicitly enabling or disabling existing Benchmark
   Rules;
4. freeze the effective per-Rule selection state for the Assessment Request.

A Rule disabled by the effective selection SHALL NOT require applicability or
compliance evaluation.

## 12. Tailoring provenance

A Tailoring artifact SHOULD identify, where available:

- Tailoring identity/version;
- author;
- organization;
- creation/modification time;
- approval/authorization reference;
- source Benchmark identity/version;
- base Profile identity;
- parent Tailoring identity, when used.

Results SHALL identify the Tailoring that contributed to effective policy.

Results SHALL distinguish:

- publisher baseline/Profile state;
- Tailoring changes;
- Organizational Input values.

## 13. Result auditability

Compact Tailoring source SHALL NOT reduce historical auditability.

Results SHALL retain sufficient effective Rule-selection and Parameter
provenance to determine what policy was actually assessed even if the
Benchmark, Profile, Group membership, or Tailoring changes later.

## 14. SCAP 1.4 relationship

SCAP-NG Tailoring is the policy descendant of XCCDF Tailoring, but it uses a
smaller mutation surface.

Legacy XCCDF Tailoring constructs SHOULD be normalized to the effective
SCAP-NG Rule-selection and Parameter changes when this can be done losslessly.

A legacy Tailoring construct that changes policy in a way the native SCAP-NG
model does not support SHALL be reported for review rather than silently
discarded or converted into Assessment execution logic.
