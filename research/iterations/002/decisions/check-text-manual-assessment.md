# Check Text as Manual Assessment Method

**Status:** working design decision  
**Iteration:** 002  
**Scope:** XCCDF-to-SCAP-NG policy/assessment split

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Decision

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

A Rule therefore references Assessment Methods by source/object reference only;
processors and authoring tools determine each referenced method's modality by
resolving that Assessment object.

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

Separating Check Text from policy allows the verification procedure to evolve
without necessarily changing the logical Rule requirement.

Keeping modality in the Assessment Method also prevents duplicated metadata
such as:

    rule:
      automated: true
      assessment: ../assessments/example.yaml

where the referenced Assessment could later become manual or hybrid while the
Rule's duplicated flag becomes stale.

## Authoring consequence

The separation is intended to improve policy quality.

Content authors SHOULD place normative requirement language in the Rule and
procedural verification language in Assessment Methods.

A Rule may therefore remain simple:

    rule:
      id: RHEL-09-000000
      assessment: ../assessments/RHEL-09-000000.yaml

and the referenced Assessment owns its execution classification, for example:

    assessment:
      id: rhel9.RHEL-09-000000
      mode: automated

or:

    assessment:
      id: rhel9.RHEL-09-000000-manual
      mode: manual

The exact field name and permitted modality vocabulary remain subject to later
Assessment Method design review.

A Manual Assessment Method SHALL NOT silently strengthen, weaken, or redefine
the Rule to which it is bound.

If a requirement can only be understood by reading the Check Text, that is a
content-quality problem to be surfaced rather than a pattern SCAP-NG should
institutionalize.

Presentation tools MAY render a Rule and its bound Manual Assessment Method
together so existing STIG authoring and review workflows remain familiar.

Presentation and repository tools MAY derive convenient labels such as
"automated" or "manual" for a Rule by resolving its referenced Assessment
Methods. Such labels are derived views, not authoritative Rule properties.

## Migration from XCCDF

An XCCDF-to-SCAP-NG converter SHALL preserve source Check Text completely and
SHALL associate it with the originating Rule as a Manual Assessment Method.

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
properties of the converted Assessment Methods rather than duplicated Rule
metadata.

## SCAP 1.4 analog

| SCAP-NG concept | SCAP 1.4 analog | Relationship |
| --- | --- | --- |
| Rule requirement | XCCDF Rule policy text | retained as policy |
| Manual Assessment Method | XCCDF Check Text/manual check procedure | moved to assessment layer |
| Automated Assessment Method | XCCDF check + OVAL/other checking-system content | moved to assessment layer |
| Assessment modality | implied by XCCDF checking system / manual check form | normalized into Assessment Method metadata |
| Rule-to-assessment binding | XCCDF Rule check association | retained with cleaner separation |
