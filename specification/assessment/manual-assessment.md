# Manual Assessment

**Status:** pre-alpha normative draft

## 1. Purpose

A Manual Assessment represents a human-executed method for determining whether
a Rule is satisfied.

SCAP-NG is designed to support publisher content in which the only
authoritative manual-assessment material is human-readable Check Text. A
publisher SHALL NOT be required to author questionnaire structures, explicit
choice lists, typed observations, branching workflows, or other interaction
metadata merely to create a portable Manual Assessment.

Procedure-only Manual Assessments are therefore a first-class and expected
SCAP-NG authoring form.

## 2. Minimum Manual Assessment

The minimum Manual Assessment SHALL contain:

- a stable Assessment identity;
- `mode: manual`;
- a human-readable `procedure`.

Example:

    assessment:
      id: rhel9.RHEL-09-654025.manual
      mode: manual

      procedure: |-
        Verify the target configuration using the following procedure...

The `procedure` MAY contain commands, expected output, explanatory text, and
publisher-defined conditions for determining whether the Rule is satisfied.

A processor SHALL NOT require any additional publisher-authored interaction
metadata in order to execute this Assessment.

## 3. Default manual interaction

When a Manual Assessment contains a `procedure` and does not define a richer
manual interaction contract, a conforming interactive processor SHALL:

1. present the procedure to the operator;
2. allow the operator to record a completed compliance outcome of:
   - `pass`;
   - `fail`; or
   - `not_applicable`;
3. associate the selected outcome with the Rule and Manual Assessment being
   evaluated; and
4. preserve the result using the normal SCAP-NG result model.

This behavior is the **default Manual Assessment interaction**. It exists so
that procedure-only publisher content remains fully usable without an OCIL-like
questionnaire definition.

A processor MAY use publisher-specific or user-interface-specific labels for
these choices, provided the labels map deterministically to the normalized
SCAP-NG outcomes.

For example, a DISA-oriented interface MAY present terminology familiar to
STIG users while still storing the normalized SCAP-NG outcome.

## 4. Not-yet-evaluated state

The result model SHOULD support a lifecycle state representing a Manual
Assessment that has not yet been completed, such as `not_evaluated` or the
final standardized equivalent.

That lifecycle state SHALL NOT be treated as a completed compliance decision.

A processor SHOULD NOT require an operator to select the not-yet-evaluated
state as though it were equivalent to `pass`, `fail`, or
`not_applicable`.

## 5. Operator responsibility

For a procedure-only Manual Assessment, the human operator is the evaluator.

The processor SHALL NOT infer a compliance outcome from unstructured procedure
text.

The processor SHALL NOT reinterpret phrases such as "this is a finding" into
automated logic unless the content has been deliberately transformed into a
structured Assessment and that transformation is authoritative for the
content being executed.

The operator SHALL determine the outcome by following the publisher procedure
and selecting the corresponding normalized result.

## 6. Comments and evidence

A processor SHOULD permit a manual result to include reviewer comments.

A processor MAY permit evidence or evidence references to be associated with a
manual result.

Comments and evidence SHALL NOT silently alter the selected compliance outcome.

Publisher content MAY impose additional evidence or comment requirements when
such requirements are explicitly authored.

## Manual result provenance

A completed Manual Assessment Result SHALL record sufficient provenance to
identify who supplied the normalized manual outcome and when that outcome was
recorded.

At minimum, a completed manual result SHALL include:

- an evaluator/respondent identity;
- a completion timestamp;
- the Manual Assessment identity/version;
- the Assessment execution identity or Assessment Request context;
- the selected normalized outcome.

The evaluator identity SHALL use one or more stable typed identifiers available
to the implementation, such as an authenticated account identifier, directory
identity, certificate subject, organization-managed user identifier, or other
portable identity value. A display name MAY accompany the stable identity but
SHALL NOT be the only identity when a stronger identifier is available.

A manual result SHOULD also support, when available:

- organization/role of the evaluator;
- authentication/identity source;
- start time and completion time;
- reviewer comments distinct from factual observations;
- evidence/evidence references supplied by the evaluator;
- whether the response was entered directly, imported from another authorized
  system, or supplied by an authorized delegate;
- provenance for the source system or import when the result was not entered
  directly.

If a second person verifies, approves, or adjudicates the manual result, that
review action SHALL be represented separately from the original evaluator. The
original evaluator identity and completion time SHALL NOT be overwritten by a
later reviewer or approver.

Illustrative result metadata:

    manual_response:
      outcome: fail
      completed_at: 2026-10-01T14:32:18-04:00
      evaluator:
        id:
          scheme: directory
          value: jdoe@example.mil
        display_name: Jane Doe
        role: System Administrator
      response_source: direct

      review:
        reviewed_at: 2026-10-01T15:10:04-04:00
        reviewer:
          id:
            scheme: directory
            value: reviewer@example.mil
          display_name: Alex Reviewer

Exact identity schemes and the final result serialization remain subject to the
result schema, but the provenance requirements above are normative.

Manual result provenance describes who made or reviewed the observation. It is
distinct from Tailoring authorization and Organizational Input provenance.

## 7. Optional richer interaction

SCAP-NG MAY support richer Manual Assessment interaction metadata in addition
to the default procedure-only behavior.

Candidate interaction forms include:

- constrained choices with explicit outcome mappings;
- text observations;
- integer or numeric observations;
- Boolean observations;
- other typed human-supplied observations that can be evaluated by explicit
  SCAP-NG assertions.

These richer forms are optional enhancements. Their existence SHALL NOT make
them mandatory for procedure-only Manual Assessments.

A converter SHALL NOT invent structured choices, typed observations, or
pass/fail assertions from unstructured Check Text without an explicit,
reviewed transformation.

## 8. Relationship to organizational input

Manual operator observations and Organizational Inputs are distinct concepts.

Organizational Input supplies expected policy state or organization-defined
values to an Assessment.

Manual observation supplies target-specific observed information during an
assessment.

A future typed-interaction model SHALL preserve this distinction.

## 9. Legacy Check Text migration

An XCCDF-to-SCAP-NG converter that encounters human-readable Check Text SHALL
be able to produce a valid Manual Assessment by preserving that Check Text as
the `procedure`.

Lossless migration SHALL NOT depend on OCIL being present.

If legacy OCIL is present only as an interaction wrapper around Check Text, a
converter MAY omit the OCIL object structure and rely on the SCAP-NG default
Manual Assessment interaction, provided no additional authoritative semantics
are lost.

Historical XCCDF/OCIL identifiers and conversion lineage SHOULD be retained as
authoring comments or external conversion reports when useful for review. They
SHALL NOT be required scanner-facing Manual Assessment semantics.

## 10. Rationale

The expected dominant publisher workflow for manual STIG-style content is
human-readable Check Text rather than a separately authored questionnaire
model.

SCAP-NG therefore defines useful interoperable scanner behavior for that
minimal input instead of requiring publishers to adopt a more complex
interaction language before their existing manual content can be used.

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Assessment Method](assessment-method.md) · [Contents](../README.md) · [Next: Source, Compilation, Packaging, and Integrity →](../package/package-and-integrity.md)

<!-- spec-nav:end -->


## Manual Assessment versioning

A native Manual Assessment SHOULD carry an explicit version/revision.

When a Manual Assessment is created natively and has no inherited executable
definition version, its initial version SHOULD be `1` unless the publisher
uses another documented versioning policy.

The Manual Assessment version SHALL remain independent of the governing Rule
version. A Rule revision does not automatically imply a Manual Assessment
revision, and a Manual Assessment revision does not automatically imply a Rule
revision.

Migration tooling SHALL preserve any authoritative source version when one
exists rather than replacing it with the native initial value.
