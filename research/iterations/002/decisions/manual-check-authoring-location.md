# Manual Check Authoring Location: Policy vs Assessment

**Status:** working design decision for OVAL Board / DISA review  
**Iteration:** 002  
**Scope:** human-readable check procedures and manual assessment authoring

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Problem

Historical STIG/XCCDF content places human-readable Check Text near the Rule.
SCAP-NG separates policy from assessment semantics, which suggests representing
that Check Text as a Manual Assessment Method.

DISA and other publishers may nevertheless prefer authoring the manual check
procedure directly in the Rule policy file because that resembles existing
STIG authoring workflows.

SCAP-NG should distinguish:

1. **canonical semantics** — what object the content represents; and
2. **authoring placement** — where a human author is allowed to write it.

Those do not need to be identical.

## Canonical semantic model

Human-readable verification procedures are Assessment content.

A manual check determines **how compliance is evaluated**, not **what the
requirement is**.

The canonical SCAP-NG object model SHOULD therefore represent manual Check Text
as a Manual Assessment Method.

Example canonical form:

    rule:
      id: RHEL-09-000000
      assessment: ../assessments/RHEL-09-000000-manual.yaml

    assessment:
      id: rhel9.RHEL-09-000000-manual
      mode: manual
      procedure: >
        Review the system configuration and verify ...

This preserves a clean policy/assessment boundary and allows manual and
automated Assessment Methods to use a common result model.

## Optional inline authoring shorthand

SCAP-NG MAY permit an authoring shorthand that places a manual check procedure
inside the Rule policy source.

Example:

    rule:
      id: RHEL-09-000000

      manual_assessment:
        procedure: >
          Review the system configuration and verify ...

The build process SHALL normalize this shorthand into the same canonical Manual
Assessment Method object that would have been produced by a separate Assessment
file.

The inline form SHALL NOT create a second semantic model.

A processor SHALL NOT treat inline manual Check Text as normative Rule policy
merely because it appears in the policy source file.

## Prohibition on duplication

A Rule SHALL NOT define the same Manual Assessment both inline and by external
Assessment reference.

If both forms are present for the same logical Manual Assessment, validation
SHALL fail rather than guess which source is authoritative.

This preserves the one-authoritative-location principle.

## Advantages of separate Assessment files

Representing the manual check in a separate Assessment file provides:

- a clean distinction between **what must be true** and **how it is checked**;
- consistent treatment of manual and automated Assessment Methods;
- easier replacement or evolution of the checking procedure without changing
  Rule policy source;
- straightforward support for multiple Assessment Methods for one Rule;
- reuse when the same manual procedure legitimately applies to multiple Rules;
- a natural place for manual-result vocabulary, comments, evidence fields, and
  future workflow metadata;
- cleaner conversion to canonical compiled objects.

The primary cost is authoring indirection: reviewers may need to open a second
file to see the traditional STIG Check Text.

## Advantages of inline policy authoring

Allowing Manual Assessment shorthand inside the Rule source provides:

- familiarity for DISA/STIG authors accustomed to Rule + Check Text proximity;
- easier single-file review of a traditional requirement and its manual
  verification procedure;
- fewer tiny files for content that is unique to one Rule;
- simpler migration of prose-only XCCDF Check Text.

The primary risks are:

- authors may mistake procedural text for normative policy;
- policy files become larger and mix two semantic responsibilities;
- later addition of automated methods can make the inline form less natural;
- reuse and independent versioning of Manual Assessment Methods become harder.

## Recommended working direction

For iteration 002:

1. Manual Check Text SHALL remain **Assessment semantics**.
2. Separate Manual Assessment files SHOULD be the canonical explicit form.
3. An inline Rule-policy shorthand MAY be supported for authoring convenience.
4. The compiler SHALL normalize both forms into the same canonical Assessment
   object model.
5. Native compiled output SHALL not preserve a semantic distinction between
   "inline manual check" and "external manual assessment."
6. Duplicate definitions SHALL be invalid.

This gives publishers flexibility without fragmenting the specification.

## Result contract

Regardless of authoring form, a Manual Assessment Method SHOULD declare or
inherit a standard manual-result contract supporting at least:

- pass;
- fail;
- not_applicable;
- not_checked / not_evaluated, according to the final result vocabulary;
- reviewer/operator comments;
- optional evidence/notes appropriate for export back to STIG-oriented tools.

The exact final result vocabulary and STIG Viewer mapping remain a separate
results-model decision.

## Open manual-assessment questions

The major architectural decision is settled, but several result/workflow
details remain for later review:

- the exact normative result vocabulary and deterministic mapping to STIG
  Viewer/CKL-style statuses;
- whether comments are optional for every result or required for selected
  outcomes such as fail, not_applicable, or not_checked;
- whether evidence attachments/references are part of the core result model or
  an extension;
- operator/reviewer identity, timestamp, and attestation/provenance
  requirements;
- how partially completed manual assessments are represented;
- whether one Rule may legitimately bind multiple manual Assessment Methods and
  how those results combine;
- whether manual procedures need independent revision metadata when their
  procedure changes without changing Rule policy;
- privacy/redaction requirements for comments and evidence.

These are important, but they do not currently require changing the
policy/assessment separation.

## Deferred mixed manual-input / automated-evaluation case

Iteration 002 SHALL retain an explicit deferred requirement for cases where
human- or organization-supplied input is consumed by otherwise automated
evaluation.

The SQL Server 2016/2022 SCC experiment is a motivating example: OCIL collected
a tightly constrained expected-state value, which was then supplied to fixed
OVAL logic as an external value while the collection/query behavior remained
hard-coded.

This case SHALL be revisited when typed Assessment inputs and automated
Assessment Methods are designed.

The future design SHOULD distinguish at least:

- Organizational Input: human/organization supplies expected policy state;
- Manual Evidence: human supplies observed target/environment data;
- Manual Assessment: human determines the compliance outcome.

A new "hybrid" Assessment mode SHOULD NOT be added merely because legacy SCAP
required multiple technologies to express one logically automated assessment.

If mixed human-input/automation is supported, content SHALL define a typed
input contract sufficient for tools to generate safe input forms/templates,
including type, cardinality, validation constraints, and human-readable
instructions.

## Migration from XCCDF

An XCCDF converter MAY choose either source-authoring form according to project
policy:

- emit a separate Manual Assessment file; or
- emit the inline Rule shorthand.

Both outputs SHALL normalize to the same canonical SCAP-NG object graph.

A converter SHOULD offer a deterministic option so repositories can choose one
style consistently.

Example:

    --manual-checks=external
    --manual-checks=inline

The default remains an implementation/project decision until OVAL Board and
publisher review.

## Board / publisher questions

The OVAL Board and DISA should explicitly consider:

- whether the cleaner semantic separation is worth the extra source file;
- whether inline authoring materially improves STIG development/review;
- whether allowing both source styles creates acceptable tooling complexity;
- whether repository conventions should require one style per project;
- whether manual Check Text is ever legitimately reusable across multiple
  Rules in production content.

## SCAP 1.4 analog

| SCAP-NG concept | XCCDF 1.2 analog | Relationship |
| --- | --- | --- |
| Manual Assessment Method | Rule Check Text / manual check | canonical semantic successor |
| inline manual-assessment shorthand | Check Text colocated with Rule | optional authoring convenience |
| manual result contract | OCIL/manual workflow + XCCDF result | normalized into common results model |
