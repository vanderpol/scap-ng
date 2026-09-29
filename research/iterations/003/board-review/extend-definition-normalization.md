# Board Review: OVAL `extend_definition` normalization

**Status:** intentional SCAP-NG structural normalization; semantic preservation required.

## OVAL semantics

OVAL 5.12.3 defines `extend_definition` as evaluating a referenced Definition
and using that result within the logical context of the extending Definition.

The reference edge may itself carry:

- `negate`; and
- `applicability_check`.

The referenced Definition may contain arbitrary nested criteria and additional
`extend_definition` references.

## Proposed SCAP-NG treatment

SCAP-NG does not need a first-class executable construct corresponding directly
to OVAL `extend_definition`.

During OVAL -> NG conversion, the converter SHOULD recursively dereference the
referenced Definition's criteria/result subtree into the location where the
`extend_definition` occurred.

The following source structure:

    Definition A
      AND
        criterion Test-1
        extend_definition B

    Definition B
      OR
        criterion Test-2
        criterion Test-3

may normalize to:

    AND
      Test-1
      OR
        Test-2
        Test-3

A Definition that only wraps one unmodified `extend_definition` MAY therefore
disappear entirely from executable NG.

## Required semantic preservation

Dereferencing SHALL preserve:

- the containing criteria operator;
- all sibling criteria;
- nested criteria operators;
- `negate` on the `extend_definition` edge;
- `applicability_check` on the `extend_definition` edge;
- nested negation/applicability semantics in the referenced Definition; and
- the referenced Definition's final result behavior.

Definition metadata and identity SHALL NOT be interpreted as extra Boolean
semantics merely because the source represented the subtree in a separate
Definition.

## Provenance

The converter SHOULD retain in conversion provenance:

- the original extending Definition ID;
- the referenced Definition ID;
- the original `extend_definition` edge;
- source metadata needed for audit/reconstruction; and
- the mapping from source Definition subtrees to the normalized NG assessment
  subtree.

This provenance does not require preserving the wrapper as a native executable
object.

## Round-trip consequence

OVAL -> NG -> OVAL is not expected to reproduce the original
`extend_definition` wrapper graph byte-for-byte or structurally.

A regenerated OVAL document MAY express the same logic as an equivalent nested
criteria tree rather than recreating the original Definition boundaries.

Round-trip conformance therefore compares recursively dereferenced Definition
result semantics.

Raw/canonical XML diffs SHOULD continue to show the structural change so the
normalization remains visible and auditable.

## RHEL 9 corpus evidence

The pinned RHEL 9 benchmark round-trip inventory produced 382 initial semantic
mismatches. In all 382 cases:

- Tests matched;
- Objects/Collections matched;
- States matched; and
- Variables matched.

381 were trivial single-wrapper `extend_definition` patterns. The remaining
case contained two extended Definitions under the same AND criteria and
regenerated as the two equivalent inlined Test subtrees.

The RHEL 9 corpus did not expose an `extend_definition` edge carrying explicit
`negate` or `applicability_check`, so dedicated schema-derived stress cases
remain necessary for those edge semantics.

## Board questions

1. Does the Board agree that Definition identity is composition/provenance rather
   than a required first-class NG execution node when the Definition is only
   consumed through `extend_definition`?
2. Should recursive dereferencing be the normative NG conversion behavior?
3. Are there any OVAL implementation semantics beyond the XSD/Schematron result
   model that require retaining Definition boundaries?
4. Should an equivalent clarification be considered for future OVAL guidance?
