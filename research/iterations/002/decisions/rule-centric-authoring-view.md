# Rule-Centric Authoring View

**Status:** working design decision  
**Iteration:** 002  
**Scope:** authoring workflow for split policy / assessment source

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Problem

SCAP-NG intentionally separates policy, manual assessment content, automated
assessment logic, applicability, parameters, and remediation ownership.

That normalized source organization SHALL NOT require content authors to
manually open and correlate many files merely to understand one Rule while
developing or reviewing an automated Assessment.

## Requirement

SCAP-NG authoring tooling SHOULD provide a **Rule-centric authoring view** that
resolves and presents, together, the authoritative content relevant to one Rule.

At minimum, the view SHOULD be able to show:

- Rule identifier, title, severity, revision, and external identifiers;
- discussion/rationale;
- human-readable remediation;
- manual Check Text / Manual Assessment procedure;
- Benchmark platform and Rule-specific applicability;
- effective Parameters and Assessment input bindings;
- existing automated Assessment reference and source;
- source XCCDF/OVAL lineage where available.

The authoring view is a projection. It SHALL NOT become an additional
authoritative copy of those fields.

## Example conceptual view

    Rule: RHEL-09-232190
    Title: RHEL 9 system commands must be owned by root.
    Severity: medium

    Discussion:
      ...

    Manual check:
      ...

    Remediation:
      ...

    Applicability:
      Platform: rhel.9
      When: none

    Parameters:
      none

    Automated assessment:
      assessments/RHEL-09-232190.yaml

    Source lineage:
      XCCDF Rule: ...
      OVAL Definition: ...

## Tooling forms

A conformant authoring tool MAY provide this view through:

- a CLI command;
- an IDE/editor panel;
- a web UI;
- a generated Markdown/HTML review artifact;
- another equivalent interactive or generated projection.

Illustrative CLI forms:

    scap-ng show RHEL-09-232190 --authoring

or:

    scap-ng edit-assessment RHEL-09-232190

The exact command names are not normative.

## Generated review artifacts

Repositories MAY generate non-authoritative Rule-centric review artifacts, for
example:

    generated/
      authoring/
        RHEL-09-232190.md

Generated authoring artifacts SHALL be clearly marked as derived and SHALL NOT
be edited as source of truth.

## Conversion workflow

During OVAL-to-NG migration, the Rule-centric authoring view SHOULD be able to
place side-by-side:

- original XCCDF Check Text;
- original XCCDF Fix Text;
- current NG Rule policy;
- current Manual Assessment;
- current automated Assessment;
- source OVAL Definition/Test/Object/State/Variable lineage.

This is especially important when validating whether a lossless OVAL
conversion actually implements the Rule author's intended policy.

## Design principle

SCAP-NG SHALL distinguish **source normalization** from **author experience**.

A normalized source tree MAY contain multiple authoritative objects, while
authoring tooling SHOULD make the content feel like one coherent Rule-centric
workspace.

The split architecture exists to improve semantics and reuse, not to impose
navigation overhead on content authors.
