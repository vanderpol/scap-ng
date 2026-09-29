# Iteration 002 Four-Anchor Source Review Plan

**Status:** active  
**Scope:** complete benchmark/policy conversion plus lossless assessment-migration proof

Iteration 002 keeps four real STIG anchors:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

The anchors are used to design and review native SCAP-NG source. The complete
XCCDF benchmark/policy layer for each anchor is in scope, and the current
checkpoint also exercises Assessment Method migration far enough to prove that
source semantics are either represented faithfully or rejected explicitly.
Final packaging and signing remain out of scope for this checkpoint.

## Why keep all four

The anchors provide two natural reuse pairs:

    RHEL 9 <-> Oracle Linux 9
    Windows 11 <-> Windows Server 2025

They also exercise different mature OVAL families and applicability patterns.

This lets us review:

- complete Benchmark and Rule inventories;
- Profile normalization and selection semantics;
- meaningful versus mechanically inherited Group structure;
- benchmark-level platform targeting;
- rule-level applicability;
- shared applicability concepts across related benchmarks;
- Rule identity and revision normalization;
- Parameter/Value migration where present;
- future shared assessments across related benchmarks;
- Unix/Linux and Windows assessment families once that layer is addressed.

## Benchmark-layer conversion rule

Each anchor SHALL be converted completely at the XCCDF policy layer.

The benchmark conversion SHOULD include, as applicable:

1. Benchmark identity, publisher, version/revision, and external identifiers;
2. every source Rule represented by stable native Rule identity;
3. Rule title, severity, revision, external identifiers, and required
   applicability references needed to review the Benchmark model;
4. every publisher Profile, normalized to canonical SCAP-NG semantics;
5. source Values mapped to Parameters where present;
6. meaningful Groups when the source contains them or when conservative
   grouping can be justified;
7. source platform/applicability distinctions necessary to avoid changing
   effective policy.

Executable compliance Assessment Methods SHALL be migrated for the reference
cases exercised by this checkpoint when the current NG model can represent them
losslessly.

A source construct that cannot yet be represented losslessly SHALL stop that
conversion path with an explicit blocker. It SHALL NOT be silently guessed,
weakened, strengthened, dropped, or converted from automated to manual merely
because the converter lacks support.


## Current acceptance gates

The four-anchor exercise is also the regression corpus for design decisions
made during iteration 002. Before this checkpoint is considered complete:

1. Benchmark and policy semantics SHALL survive conversion.
2. XCCDF selectable-check semantics SHALL survive as
   `Benchmark Rule -> Policy -> selected check -> Assessment`.
3. XCCDF `refine-rule/@selector` semantics SHALL be represented in native
   Profile/Tailoring selector data.
4. A source Rule exposing multiple selectable checks SHALL NOT be collapsed to
   one Assessment. Until every alternative is lowered, conversion SHALL fail
   explicitly.
5. OVAL object/state/test/variable semantics, including existence and
   non-existence conditions, SHALL be preserved or explicitly blocked.
6. Manual Check Text and remediation context needed by content authors SHALL
   remain available through the rule-centric authoring view.
7. Result examples SHALL include deterministic human-readable outcome messages,
   structured failure reasons, and bounded concrete evidence where applicable.
8. Every newly discovered unsupported source construct SHOULD become a
   permanent migration/conformance regression test.

Generated output that merely validates syntactically does not satisfy these
gates if it reflects an older design assumption.

## Profile rule-selection rule

Benchmark membership enables a Rule by default.

Profiles SHALL describe Rule-selection differences only. Native Profile
Rule-selection is subtractive:

- a Profile MAY disable Benchmark Rules;
- a Profile SHALL NOT explicitly enable a Rule;
- a Profile SHALL NOT introduce a Rule not already in the Benchmark;
- a Profile with no Rule-selection difference contains no Rule-selection state;
- source XCCDF positive selections that merely restate Benchmark defaults are
  removed during up-conversion.

See
[`decisions/profile-rule-selection.md`](decisions/profile-rule-selection.md)
for the complete normative rule, inheritance constraints, migration behavior,
and RHEL 9 evidence.

## Working layout

    research/iterations/002/
      examples/
        shared/
          platforms/
          applicability/
          assessments/
        rhel9/
          benchmark.yaml
          policy/
        oracle-linux9/
          benchmark.yaml
          policy/
        windows11/
          benchmark.yaml
          policy/
        windows-server-2025/
          benchmark.yaml
          policy/
      provenance/
      decisions/

Shared platform identity assessments, applicability conditions, and technical
compliance assessments should each live once under `examples/shared/` when
the review establishes reuse.

Do not combine platform identity with reusable rule conditions. For example,
`windows.11` is a platform, while `windows.member-workstation` is an
applicability condition reusable across Windows versions. Likewise,
`windows.server-2025` is a platform and `windows.domain-controller` is a
separate reusable applicability condition.

When legacy source logic combines platform identity with another condition and
the assessment semantics have not yet been reviewed, preserve the distinction
as requiring classification rather than inventing a decomposition.

## Native-source rules

- Keep executable source free of XCCDF/OVAL/OCIL runtime references.
- Keep machine migration provenance outside executable source.
- Use stable native Rule identities with source identifiers preserved as
  identifiers/provenance rather than overloaded runtime IDs.
- Prefer concise defaults over repeating obvious mechanics.
- Benchmark membership implies Rule enablement.
- Profiles serialize only actual disable deltas.
- Do not recreate one-Rule XCCDF wrapper Groups merely for structural fidelity.
- Preserve required platform and applicability meaning even when executable
  implementations are deferred.
- Use OVAL-aligned capability families when Assessment Methods are added.
- Preserve complex semantics only where the underlying assessment actually
  requires them.

## Explicitly out of scope for now

Until the source model is approved:

- final distribution packages;
- signing;
- package manifests;
- complete OVAL-to-NG compliance Assessment Method conversion;
- reference scanner implementation;
- broad-corpus generation beyond the four anchor benchmarks.

## Design authority during iteration 002

The source format is intentionally open to redesign.

The working approach is:

1. start from the real semantic requirement;
2. preserve OVAL/XCCDF lessons that still matter;
3. remove legacy structure and expansion that do not improve clarity or
   correctness;
4. choose the smallest readable native syntax that remains deterministic;
5. validate decisions against the complete four-anchor benchmark layer;
6. compare simple and complex cases side by side;
7. change the syntax freely while 002 is still a design iteration.

Questions should be escalated when a choice materially changes semantics,
authoring power, compatibility expectations, or the eventual specification.
Routine syntax and organization decisions should be made within the iteration
and demonstrated with concrete examples.
