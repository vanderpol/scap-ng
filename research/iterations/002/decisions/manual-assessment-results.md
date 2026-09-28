# Manual Assessment Result Contract and STIG Viewer Interoperability

**Status:** working design decision for OVAL Board / DISA review  
**Iteration:** 002  
**Scope:** manual Assessment operator responses and STIG Viewer-compatible result export

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Goal

A SCAP-NG Manual Assessment should be immediately usable by an interactive
review tool without each content author redefining basic pass/fail response
semantics.

The default manual response contract SHALL therefore be defined by SCAP-NG
rather than repeated in every Manual Assessment source file.

## Default completed outcomes

A Manual Assessment SHALL support these normal completed operator outcomes:

- `pass` — the requirement is satisfied;
- `fail` — the requirement is not satisfied;
- `not_applicable` — the requirement does not apply to the assessed target
  under the governing policy/applicability guidance.

These values are semantic result states, not merely display labels.

A content author SHALL NOT redefine `pass` to mean failure, or otherwise
change their normative meaning.

Presentation tools MAY display publisher- or organization-preferred labels
while preserving the canonical result value.

## Incomplete/unreviewed state

A Manual Assessment result model SHALL also represent an assessment that has
not yet been completed.

The working canonical state is:

    not_reviewed

`not_reviewed` is not normally an operator-selected completed answer. It is
the state of a Manual Assessment for which no completed determination has yet
been supplied, or for which required manual review remains outstanding.

The final SCAP-NG cross-mode result vocabulary remains subject to broader
results-model review.

## Finding details and comments

A Manual Assessment result SHOULD provide two distinct free-text fields:

    finding_details
    comments

### finding_details

`finding_details` records the evidence, observation, or factual basis supporting
the outcome.

Examples include:

- the configuration observed by the reviewer;
- filenames, setting values, account names, or other relevant observations;
- why a requirement was determined not applicable;
- concise evidence supporting a pass or fail result.

### comments

`comments` records reviewer/organization annotations that are useful but are
not themselves the observed finding evidence.

Examples include:

- ticket or POA&M references;
- reviewer notes;
- remediation coordination notes;
- local documentation references.

Keeping these fields distinct preserves interoperability with established STIG
checklist workflows and avoids collapsing evidence and commentary into one
unstructured string.

## Minimal Manual Assessment source

Because the default response contract is defined by the specification, content
authors do not need to repeat the outcome vocabulary in every source file.

An external Manual Assessment can remain small:

    assessment:
      id: rhel9.RHEL-09-000000-manual
      mode: manual
      procedure: >
        Review the configuration and determine whether the requirement is met.

The same semantic object may be embedded inline in Rule policy source when the
manual method is rule-specific, as described in
`check-text-manual-assessment.md`.

Authoring syntax MAY later allow an Assessment to add prompts or constraints
for `finding_details` or `comments`, but absence of such customization SHALL
still provide the standard fields.

## Runtime result example

A completed manual result may be represented conceptually as:

    result:
      assessment: rhel9.RHEL-09-000000-manual
      outcome: fail
      finding_details: >
        PermitRootLogin is configured as yes in /etc/ssh/sshd_config.
      comments: >
        Change is scheduled under ticket CHG-12345.

Exact results-document syntax remains subject to results-model design.

## STIG Viewer / checklist mapping

SCAP-NG tooling intended to export DISA checklist results SHOULD support the
following deterministic mapping:

| SCAP-NG result | STIG Viewer / CKL status |
| --- | --- |
| `pass` | `NotAFinding` |
| `fail` | `Open` |
| `not_applicable` | `Not_Applicable` |
| `not_reviewed` | `Not_Reviewed` |

The SCAP-NG `finding_details` field SHOULD map to the checklist finding-details
field.

The SCAP-NG `comments` field SHOULD map to the checklist comments field.

Export tooling MAY support additional DISA checklist fields, such as severity
override or justification, when those are represented by the final SCAP-NG
results model. Those fields are outside this minimal manual-response decision.

## Why the outcome vocabulary is not repeated in content

Repeating this in every manual Assessment:

    allowed_outcomes:
      - pass
      - fail
      - not_applicable

would add no semantic information for the normal case and would invite
unnecessary publisher variation.

The default contract belongs in the specification.

A future extension MAY allow an Assessment to restrict an outcome only when
there is a demonstrated semantic need, but content SHALL NOT invent new
meanings for the canonical states.

## Applicability interaction

Rule applicability and a Manual Assessment's `not_applicable` outcome are
related but not identical mechanisms.

Where applicability can be determined before the Rule assessment, the Rule
SHOULD be excluded through the normal Benchmark/Rule applicability model.

The `not_applicable` manual outcome remains necessary for cases where
applicability can only be established during the prescribed human review or
where existing DISA workflow requires recording that determination at the Rule
result.

Tooling SHOULD preserve the reason in `finding_details`.

## Authoring UI expectations

A conformant interactive Manual Assessment UI SHOULD be able to derive, without
publisher-specific code:

- the manual procedure;
- the standard outcome choices;
- a finding/evidence-details entry area;
- a comments entry area.

This allows SCAP-NG Manual Assessments to be rendered consistently by multiple
tools and exported back into existing STIG review workflows.

## SCAP 1.4 / DISA analog

| SCAP-NG concept | Existing workflow analog |
| --- | --- |
| `pass` | STIG Viewer `NotAFinding` |
| `fail` | STIG Viewer `Open` |
| `not_applicable` | STIG Viewer `Not_Applicable` |
| `not_reviewed` | STIG Viewer `Not_Reviewed` |
| `finding_details` | CKL/CKLB finding-details field |
| `comments` | CKL/CKLB comments field |
| Manual Assessment procedure | XCCDF/STIG Check Text |

## Open questions

- Whether `not_reviewed` becomes a general SCAP-NG result state shared by all
  Assessment modes or remains a workflow state.
- Whether finding details are required for `fail` and `not_applicable`.
- Whether reviewer identity/timestamp belongs directly in each manual result or
  in enclosing result provenance.
- How severity override and justification should map into the broader
  SCAP-NG results model.
