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

A Profile SHALL expose `disabled_rules`, including an empty list when it
disables no additional Rules. An empty list explicitly records no additional
deselections; it SHALL NOT re-enable Rules disabled by an ancestor Profile.
This preserves the visible supported-data-elements convention. `enabled_rules`
is not a supported publisher Profile property and SHALL NOT appear there.

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

### Named Assessment selection

Tailoring MAY choose among the named Assessment selections already exposed by
a Rule, for example `automated` or `manual`. Selection SHALL preserve the Rule's
declared bindings and SHALL NOT create a new selection or replace an Assessment
path, capability, or implementation. An unknown selection SHALL be rejected.

Choosing an existing named selection is distinct from modifying the Assessment
references or implementations prohibited below. Organizational Input SHALL NOT
select Assessments or alter which Tests run.

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

A Tailoring artifact SHALL expose a human-readable `purpose` explaining why
the Tailoring exists. Purpose and a clearly labeled `provenance` section SHOULD
appear near the top, before policy changes, so reviewers can readily find them.

The provenance section SHALL expose distinct fields for `created_by`,
`created_at`, `modified_by`, `modified_at`, `authorized_by`, `authorized_at`,
`authorization_reference`, and `authorization_status`. Creator, modifier and
authorizer SHALL remain distinct roles even when the same person fills them.
Person records SHOULD include name, organizational role and contact information
when available. Organizational ownership SHOULD also be recorded.

Unset or not-yet-authorized fields MAY be null and SHALL remain visible in
draft examples. A null authorizer SHALL NOT be represented as approval by the
creator. These metadata record purpose and authorization provenance; they SHALL
NOT themselves alter Rule selection, Parameter values or Assessment execution.

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


## 15. Minimal Tailoring example

A Tailoring artifact SHOULD express only local differences from the referenced
publisher policy.

Illustrative source:

    tailoring:
      id: org.example.windows11.production
      version: 1

      benchmark:
        id: disa.windows11.stig
        version: V2R10

      profile: disa.mac-2_classified

      disabled_rules:
        - WN11-EXAMPLE-001

      parameters:
        password_minimum_length: 16

A Tailoring artifact SHOULD NOT serialize a full copy of the Benchmark or
Profile.

## 16. Tailoring resolution algorithm

A processor SHALL resolve effective policy in this order:

1. load the exact Benchmark publication;
2. enable every Benchmark Rule;
3. apply the selected publisher Profile and its ancestors;
4. resolve publisher Parameter values;
5. apply Tailoring parent layers, if any;
6. apply the requested Tailoring layer;
7. resolve resulting effective Rule selection;
8. resolve resulting effective tailorable Parameter values;
9. validate required Organizational Input separately;
10. freeze the effective policy for the Assessment Request.

After policy is frozen, subsequent evaluation SHALL NOT mutate that effective
policy.

## 17. Tailoring validation

A Tailoring artifact SHALL fail validation when:

- the referenced Benchmark identity cannot be resolved;
- the referenced Benchmark version does not match;
- the referenced Profile does not exist;
- a referenced Rule is not a Benchmark member;
- a Rule is both enabled and disabled in the same layer;
- a Parameter does not exist;
- a Parameter is not tailorable;
- Tailoring attempts to change an Assessment Method or applicability mapping;
- Tailoring inheritance is cyclic;
- Group operations are ambiguous;
- a parent Tailoring targets a different Benchmark publication.

## 18. Tailoring rebase to a new Benchmark

Tailoring SHALL be version-bound.

When a new Benchmark publication is released, existing Tailoring SHALL NOT be
silently reused against it.

A rebase tool MAY create a candidate Tailoring for the new Benchmark.

A rebase operation SHOULD classify each previous local decision as:

- unchanged and still valid;
- automatically mapped to a stable Rule/Parameter identity;
- affected by publisher policy change;
- removed because the referenced object no longer exists;
- requiring human review.

The rebased Tailoring SHALL receive its own identity/version or revision and
SHALL record the new Benchmark publication binding.

## 19. Tailoring and Rule applicability

Tailoring Rule selection and Rule applicability solve different problems.

Tailoring answers:

    Should this Rule be part of the organization's effective policy?

Applicability answers:

    Given that the Rule is selected, does it apply to this target?

A Tailoring artifact SHALL NOT change a Rule's `when` expression merely to
exclude a target.

A selected but inapplicable Rule is reported as not applicable.

A Tailoring-disabled Rule is outside the effective assessment selection and
SHOULD be reported distinctly from an inapplicable Rule when the result format
records excluded policy.

## 20. Tailoring result requirements

Results SHALL make the effective local policy reconstructable without requiring
the Tailoring source artifact to remain externally available forever.

At minimum, a complete run result SHOULD identify:

- Benchmark identity/version;
- publisher Profile identity;
- Tailoring identity/version;
- effective selected/disabled Rule state;
- effective tailored Parameter values or their protected references;
- which values came from Organizational Input rather than Tailoring.

Sensitive Parameter values MAY require redaction according to the future
results-security profile.

## 21. Tailoring authorization metadata

Tailoring content MAY carry organization-specific approval metadata such as:

- approval authority;
- ticket/change identifier;
- exception identifier;
- effective date;
- expiration/review date;
- justification.

These values describe local policy governance.

They SHALL NOT change evaluation semantics unless a future specification
explicitly defines such behavior.


## 22. Worked-source expectation

Before Profile/Tailoring serialization is considered stable, the project
SHOULD add worked source examples covering at least:

- Tailoring a Benchmark baseline with no Profile;
- Tailoring a publisher Profile;
- disabling a publisher-selected Rule;
- re-enabling a Benchmark Rule disabled by a publisher Profile;
- overriding a tailorable publisher Parameter;
- supplying Organizational Input without creating Tailoring;
- rebasing Tailoring to a newer Benchmark version;
- result provenance showing publisher policy versus local modifications.

Current worked examples are in
[`research/iterations/003/examples/tailoring-all-options/`](../../research/iterations/003/examples/tailoring-all-options/README.md),
including a comprehensive demonstration and a Tailoring bound to the current
full RHEL9 review. Example source grammar proposals SHALL NOT be mistaken for
finalized serialization or assessor runtime conformance.


## 23. Check selection

A Rule MAY expose multiple named Assessment alternatives. A Tailoring
artifact MAY select among those published alternatives by **check selector**.

Illustrative source:

    tailoring:
      benchmark:
        id: disa.example.stig
        version: V1R1

      check_selectors:
        EXAMPLE-01-000001: manual

The selector identifies a choice already exposed by the Rule.
Tailoring SHALL NOT use check selection to introduce, replace, or
modify an Assessment implementation.

Selector names are extensible and SHALL NOT be restricted to `automated` and
`manual`.

An explicitly selected check selector that cannot be resolved SHALL make policy
resolution fail. A processor SHALL NOT silently fall back to a default check.

This capability is the native SCAP-NG successor to XCCDF check-selection
semantics, including tailoring that deliberately selects a manual alternative
instead of an automated check.

The effective policy recorded for a run SHALL include any non-default check
selection needed to reconstruct which Assessment Method was executed.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Platform and Applicability](platform-and-applicability.md) · [Contents](../README.md) · [Next: Policy Resolution →](policy-resolution.md)

<!-- spec-nav:end -->
