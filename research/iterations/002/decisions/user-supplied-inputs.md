# OVAL Board Decision: User-Supplied Inputs / Organizational Values

**Status:** open design decision for OVAL Board review  
**Iteration:** 002  
**Scope:** split policy / assessment source model

## Why this needs a Board decision

SCAP-NG should preserve and improve the useful intent behind XCCDF Values and
interactive/tailoring inputs: content authors need a way to automate checks
whose expected value is defined by an organization rather than by the benchmark
author.

This becomes especially important when an otherwise manual requirement can be
automated if the scanner is given organization-defined data.

The old SCAP/XCCDF-to-OVAL model did not provide a clean general-purpose bridge
for rich typed data. SCAP-NG has an opportunity to make this a first-class,
shared language feature rather than a special policy-to-assessment stovepipe.

## Working direction for discussion

An NG assessment should be able to declare typed external inputs, conceptually:

    inputs:
      approved_admins:
        type: list<string>
        required: true
        on_missing: not_checked

The same declared input could be supplied by:

- a benchmark profile;
- a tailoring or override file;
- an interactive scanner UI;
- a scanner-supported external data file;
- an API or other integration.

The assessment should consume the same typed value regardless of the delivery
mechanism.

## Important design goal

Do not limit user-supplied values to single text strings.

Potential input types should include, at minimum, discussion of:

- string
- boolean
- integer / decimal
- version
- path
- list<T>
- set<T>
- map<K,V>
- structured record/object

Inputs may also need validation constraints such as allowed values, regex,
numeric ranges, uniqueness, and field-level requirements.

This allows organizational data to match the complexity actually needed by the
assessment language.

## Open Board question: what happens when required input is missing?

This behavior must be normative and content-controlled rather than left to
individual scanner implementations.

Two important patterns need to be supported or deliberately ruled on.

### Option A — not checked / not evaluated

The assessment cannot make a meaningful determination without the
organizational value.

Conceptually:

    inputs:
      approved_admins:
        type: list<string>
        required: true
        on_missing: not_checked

If the user provides no value, the scanner reports that the rule was not
checked/evaluated because required input was missing.

### Option B — compare against an explicit empty/default value

For some requirements, absence of supplied data may intentionally resolve to an
empty or declared default value:

    inputs:
      approved_exceptions:
        type: list<string>
        default: []

Normal assessment logic then executes.

If collected system data does not satisfy the requirement when compared with
that empty/default value, the assessment can fail normally.

This is different from silently treating all missing required values as empty.

## Questions for the OVAL Board

1. Should user-supplied inputs be a first-class part of the NG assessment
   language?

2. Which primitive and structured input types must the first NG specification
   support?

3. Should the assessment declaration own the type, validation constraints,
   required/optional status, default, and missing-value semantics?

4. Which missing-input result behaviors should be normative?
   Candidates include:
   - not_checked / not_evaluated;
   - error;
   - use declared default;
   - explicit empty value followed by normal comparison.

5. Should profiles bind values directly to assessment inputs, or should a
   separate tailoring/binding object mediate that relationship?

6. Should interactive entry, file-based input, profiles, and APIs all resolve
   into the same typed input model?

7. What standard serialization should external input files use? YAML and/or
   JSON are obvious candidates because they support structured data.

8. How should scanners report the source of a resolved value: profile,
   tailoring file, interactive entry, API, or default?

9. What redaction/privacy requirements are needed when organizational inputs
   may contain sensitive names, accounts, paths, or other local information?

10. Should input definitions be reusable independently of a single assessment,
    allowing multiple assessments to consume the same organizational value?

## Board demonstration requirement

Iteration 002 should eventually demonstrate at least two examples for Board
review:

### Required organizational value

- assessment declares a typed organizational input;
- no value supplied -> proposed `not_checked` behavior;
- value supplied -> assessment evaluates normally.

### Optional/defaulted structured value

- assessment declares a list/set/record input;
- no value supplied -> declared empty/default value;
- normal comparison executes and may pass or fail.

At least one example should use structured data rather than a scalar string.

## Relationship to profiles

Profiles belong to the benchmark/policy layer, but the **input contract belongs
to the assessment**.

A profile may provide a value, but it should not redefine the assessment's
datatype or semantic expectations.

Conceptually:

    profile:
      id: enterprise-default
      values:
        approved_admins:
          - DOMAIN\\SecAdmins
          - DOMAIN\\OpsAdmins

The same assessment could receive that value from another profile, a tailoring
file, interactive input, or an API without changing its source.

## Design principle to preserve

The scanner provides input mechanisms.

The content defines:

- what input is needed;
- its type;
- its validation;
- its default, if any;
- what missing input means.

The OVAL Board should decide the normative syntax and result semantics before
this becomes a locked SCAP-NG feature.
