# Parameter Model and XCCDF refine-value

**Status:** working design decision for OVAL Board review  
**Iteration:** 002

SCAP-NG Parameters are intended to preserve the useful policy role of XCCDF
Values without recreating the XCCDF-to-OVAL variable stovepipe.

## Minimal native model

A Parameter SHALL define:
- a stable semantic identifier;
- a data type;
- a human-readable description/title;
- whether the value is publisher-defined or organization-defined;
- an effective publisher value/default when one exists;
- validation constraints necessary to determine whether a supplied value is
  valid policy data.

A Profile MAY bind a Parameter value.

Tailoring MAY override a Parameter that already has an effective publisher
value when the Benchmark permits that override.

Organizational Input MAY satisfy a Parameter intentionally left unresolved by
the publisher.

Assessment Methods MAY consume Parameters only through explicitly typed
expected-state input bindings.

## XCCDF refine-value

XCCDF 1.2 `refine-value` allowed a Profile to select among alternate
publisher-authored Value selectors/constraints and to refine the Value
operator. That was a useful attempt to support policy variants without simply
replacing the Value.

SCAP-NG SHALL NOT initially define a direct native `refine-value` equivalent.

The preferred native model is deliberately smaller:
- a Profile selects or supplies the effective publisher policy value;
- Tailoring overrides an already-resolved policy value;
- Organizational Input supplies an intentionally unresolved value;
- validation constraints remain explicit and typed.

## Migration requirement

An SCAP 1.4 up-converter SHALL preserve the semantics of source
`refine-value` usage.

Where the selected XCCDF Value variant can be represented losslessly as an
explicit SCAP-NG Profile Parameter binding plus constraints, the converter
SHOULD normalize it to that simpler form.

Where lossless normalization is not possible, the converter SHALL preserve the
source semantics in migration IR/provenance and SHALL mark the construct for
review rather than silently dropping or approximating it.

## Reconsideration

A direct native equivalent to `refine-value` MAY be added later only if
production migration evidence or native authoring requirements demonstrate a
case that cannot be expressed clearly with the smaller Parameter/Profile model.

Because this changes a long-standing XCCDF policy-language feature and affects
the contract between policy and assessment, promotion of such a construct into
the native SCAP-NG specification SHOULD be an explicit OVAL Board design
decision.
