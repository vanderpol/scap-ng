# Check Text as Manual Assessment Method

**Status:** working design decision  
**Iteration:** 002  
**Scope:** XCCDF-to-SCAP-NG policy/assessment split and manual-assessment authoring layout

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Semantic decision

SCAP-NG SHALL treat human-readable Check Text as **assessment content**, not as
normative policy content.

A Rule SHALL express the security or configuration requirement independently
of any procedure used to verify that requirement.

Human-readable verification procedures SHALL be represented as **Manual
Assessment Methods**.

A Rule MAY bind to one or more Assessment Methods, including manual and
automated methods.

The Rule policy SHALL NOT duplicate the Assessment Method's modality. Whether
an Assessment Method is automated, manual, or another defined execution mode
SHALL be declared by the Assessment Method itself.

This semantic separation does **not** require every Manual Assessment Method to
live in a separate physical source file.

## Two valid authoring layouts

SCAP-NG SHOULD permit both of the following source layouts when they normalize
to the same Assessment object model.

### External Manual Assessment file

A Rule may reference a separate Assessment source file:

    rule:
      id: RHEL-09-000000
      assessments:
        - ../assessments/manual/RHEL-09-000000.manual.assessment.yaml
        - ../assessments/automated/RHEL-09-000000.automated.assessment.yaml

When only the Manual Assessment is being illustrated, its referenced file
contains:

    assessment:
      id: rhel9.RHEL-09-000000-manual
      mode: manual
      procedure: >
        Inspect the configuration and determine whether the requirement is met.

This layout is preferred when the Assessment is reused, independently
maintained, unusually complex, or one of several methods bound to the Rule.

External Manual Assessment Methods SHOULD reside under an
`assessments/manual/` tree. Automated Assessment Methods SHOULD reside under
`assessments/automated/`. Reusable shared methods SHOULD follow the same
modality separation beneath `shared/assessments/`.

The directory is an authoring convention, not semantic identity; the
Assessment's declared `mode` remains authoritative.

### Inline Manual Assessment

A Rule may embed a rule-specific Manual Assessment in the policy source:

    rule:
      id: RHEL-09-000000

      manual_assessment:
        id: rhel9.RHEL-09-000000-manual
        procedure: >
          Inspect the configuration and determine whether the requirement is met.

The exact property name remains subject to schema review. The embedded object
is still semantically an Assessment Method, not normative Rule text.

At build time, inline and external forms SHALL normalize to the same internal
Assessment object model and result semantics.

A Manual Assessment SHALL NOT be represented in both forms simultaneously
merely to duplicate the same procedure.

## Tradeoffs

### External-file advantages

- preserves a visually strict policy/assessment file boundary;
- makes reuse across Rules and Benchmarks obvious;
- permits independent Assessment revision and testing;
- scales naturally when a Rule has multiple Assessment Methods;
- keeps large or structured procedures out of policy source;
- aligns manual and automated Assessment organization.

### External-file disadvantages

- creates many small files for one-off prose checks;
- increases navigation burden for human reviewers;
- may be less familiar to DISA/STIG authors accustomed to Rule plus Check Text
  being reviewed together;
- may add indirection where no reuse or independent lifecycle exists.

### Inline advantages

- keeps a one-off prose verification procedure next to the Rule it evaluates;
- maps naturally from traditional DISA STIG authoring practice;
- reduces file count and repository navigation;
- may improve human review when requirement and manual procedure are routinely
  considered together.

### Inline disadvantages

- can visually blur policy and assessment unless the schema remains explicit;
- makes reuse less obvious;
- can make Rule files substantially larger;
- complicates independent Assessment revision;
- can become awkward if automated and manual methods coexist or if a manual
  method becomes shared later.

## Working recommendation

SCAP-NG SHOULD preserve one semantic Assessment model while permitting both
source placements.

A publisher MAY embed a Manual Assessment when it is tightly scoped to one
Rule and consists primarily of prose procedure.

A publisher SHOULD use a separate Assessment file when the method:

- is reused or expected to be reused;
- has structured inputs or evidence contracts;
- has multiple consumers;
- is independently versioned/tested;
- contains significant logic or complexity;
- is one of multiple Assessment Methods for the Rule.

Tooling SHOULD be able to promote an inline Manual Assessment to a separate
file without changing its stable logical identity or result semantics.

## Rationale

Policy and assessment answer different questions:

- policy: **what must be true**;
- assessment: **how compliance is determined**.

For example:

    Policy:
      The audit log directory must be owned by root.

    Manual Assessment Method:
      Inspect the ownership of /var/log/audit and verify that the owner is root.

    Automated Assessment Method:
      Collect the owner of /var/log/audit and assert uid == 0.

The manual and automated procedures are peer implementations of the same
verification problem and SHOULD share the same Parameter, provenance, and
result model.

Separating the concepts allows verification procedures to evolve without
necessarily changing the logical Rule requirement. Allowing inline
serialization prevents that semantic separation from forcing unnecessary
one-paragraph files.

## Assessment modality

Keeping modality in the Assessment Method prevents duplicated metadata such as:

    rule:
      automated: true
      assessment: ../assessments/example.yaml

where the referenced Assessment could later change while the Rule's duplicated
flag becomes stale.

Presentation and repository tools MAY derive convenient labels such as
"automated" or "manual" for a Rule by resolving or normalizing its Assessment
Methods. Such labels are derived views, not authoritative Rule properties.

## Manual result contract

Manual Assessments SHALL use the SCAP-NG manual result contract defined for the
assessment/result model.

The normal operator-selectable outcomes SHOULD include at least:

- `pass`;
- `fail`;
- `not_applicable`.

The result model SHOULD also represent a not-yet-reviewed/not-evaluated state
without requiring the operator to choose it as a completed assessment outcome.

Manual results SHOULD support distinct fields for:

- finding/evidence details;
- reviewer comments.

The result vocabulary and interoperability mapping are documented separately so
that authoring layout does not change result semantics.

## Migration from XCCDF

An XCCDF-to-SCAP-NG converter SHALL preserve source Check Text completely and
SHALL associate it with the originating Rule as a Manual Assessment Method.

The converter MAY emit that Manual Assessment inline or as a separate source
file according to publisher/tooling policy, provided both forms normalize to
the same object model.

The converter SHALL preserve source provenance for that Manual Assessment
Method.

The converter SHALL NOT assume that all historical Check Text is purely
procedural. If Check Text contains normative policy that is absent from the
Rule requirement, the converter SHOULD identify that condition for review
rather than silently discarding or inventing policy semantics.

Where policy semantics can be identified deterministically and without
interpretive repair, the converter MAY normalize them into the policy model
while preserving the original Check Text as provenance.

When source content provides both automated and manual checking methods, the
converted Rule MAY reference both. Their execution classifications SHALL remain
properties of the Assessment Methods rather than duplicated Rule metadata.

## SCAP 1.4 analog

| SCAP-NG concept | SCAP 1.4 analog | Relationship |
| --- | --- | --- |
| Rule requirement | XCCDF Rule policy text | retained as policy |
| Manual Assessment Method | XCCDF Check Text/manual check procedure | assessment semantics retained; source may be inline or external |
| Automated Assessment Method | XCCDF check + OVAL/other checking-system content | moved to assessment layer |
| Assessment modality | implied by XCCDF checking system / manual check form | normalized into Assessment Method metadata |
| Rule-to-assessment binding | XCCDF Rule check association | retained with cleaner separation |
