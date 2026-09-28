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

XCCDF 1.2 `refine-value` is a Profile action. It can select an alternate
publisher-authored Value selector/constraint and can refine the Value operator.
In the absence of an applied Profile or Tailoring action, the normal/default
Value selection is used.

SCAP-NG SHALL NOT initially define a direct native `refine-value` equivalent.

The preferred native model is deliberately smaller:
- a Profile supplies the effective publisher policy value;
- Tailoring overrides an already-resolved policy value;
- Organizational Input supplies an intentionally unresolved value;
- validation constraints remain explicit and typed.

## Migration behavior if refine-value is dropped

If the OVAL Board decides that native SCAP-NG does not support
`refine-value`, the up-converter SHALL NOT recreate the historical
`refine-value` mechanism merely for compatibility.

Dormant or otherwise non-effective `refine-value` data does not require a
native runtime representation.

One compatibility case remains important: when converting an XCCDF Profile
whose effective behavior actually depends on `refine-value`, silently
ignoring that action would change the Profile's policy semantics.

For such an applied/effective source Profile, the converter MAY normalize the
resolved result into an ordinary SCAP-NG Profile Parameter binding when that is
lossless. For example, a selected XCCDF Value variant may become an explicit
Parameter value in the converted Profile.

If the Board prefers that even this normalization not be supported, the
converter SHOULD report that source Profile as requiring review or unsupported
rather than silently changing its effective policy.

The converter does not need to preserve selectors, `refine-value` syntax, or
other obsolete mechanism after the effective policy value has been normalized.

## Reconsideration

A direct native equivalent to `refine-value` MAY be added later only if
production migration evidence or native authoring requirements demonstrate a
case that cannot be expressed clearly with the smaller Parameter/Profile model.

Because this changes a long-standing XCCDF policy-language feature and affects
the contract between policy and assessment, retention or removal of the feature
SHOULD be an explicit OVAL Board design decision.
