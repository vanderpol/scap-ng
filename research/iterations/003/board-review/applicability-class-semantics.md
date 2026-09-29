# OVAL Board Review: Applicability and Assessment Class Semantics

**Status:** open design question  
**Iteration:** 003


## Implementation reality of `applicability_check`

The presence of `applicability_check` in the OVAL schema SHALL NOT by itself
be treated as proof of mature interoperable applicability semantics.

The attribute was added to OVAL 5.10 after a community request to mark criteria,
criterion, or extended definitions as applicability checks. The OVAL language
specification requires the marker to be preserved into OVAL Results.

A review of the OpenSCAP implementation shows that OpenSCAP:

- parses and stores the `applicability_check` flag;
- exposes getters/setters for it;
- propagates it into result criteria nodes;
- but does not consult the flag in the core criteria evaluation path.

The criteria evaluator evaluates child criteria/tests/extended definitions,
combines their normal result values, applies negation, and returns the result
without changing behavior based on `applicability_check`.

This is consistent with the possibility that `applicability_check` was only
partially realized in deployed OVAL tooling. Historical OVAL Board knowledge
also indicates that the feature may never have achieved broad end-to-end
implementation. That historical point should be confirmed with Board members
before it is treated as established fact.

### Consequence for SCAP-NG

SCAP-NG SHOULD NOT adopt a separate applicability semantic axis merely because
OVAL contains `applicability_check`.

The Board should first determine whether the historical feature had any
interoperable operational behavior that must be preserved.

If it did not, the more relevant compatibility precedent may be the long-lived
SCAP convention of using `class="inventory"` Definitions as applicability
predicates.


## Decision options

The OVAL Board should explicitly choose among these directions:

1. **Preserve the historical SCAP convention:** applicability Assessments use
   `class: inventory`, even for environmental predicates that are not literal
   software inventory.
2. **Define a native NG `applicability` class:** make applicability a first-class
   semantic class and document this as an intentional divergence from OVAL 5.x.
3. **Keep semantic class separate from invocation context:** retain classes such
   as compliance/inventory and let the applicability registry/reference establish
   how an Assessment is being used.
4. **Adopt another model based on implementation evidence:** if Board review
   identifies operational semantics not captured above.

Any choice that differs from historical SCAP behavior SHALL be documented in
the SCAP 1.4 compatibility crosswalk and migration guidance.
