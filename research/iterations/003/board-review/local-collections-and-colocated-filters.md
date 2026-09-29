# Board Review: Local Collections and Colocated Filtering

**Status:** proposed SCAP-NG authoring feature for OVAL Board review.

## Proposal

SCAP-NG should support a native authoring pattern where one-use assessment
semantics may be defined locally at the point of use instead of requiring a
separately named/referenced node solely to satisfy language structure.

Two concrete examples are:

1. **Inline local Collections inside Variables**
2. **Filters expressed directly inside Collections**

These are not changes to the underlying OVAL semantics. They are authoring-model
improvements intended to remove unnecessary indirection when a construct has no
independent reuse value.

## Inline local Collection inside a Variable

A Variable MAY obtain values from either:

- a named reusable Collection; or
- an anonymous/local Collection defined inside the Variable expression.

Example:

    variables:
      interactive-uids-variable:
        expression:
          values:
            collection:
              capability: unix.password
              select:
                username:
                  operation: pattern_match
                  value: ".*"
              filters:
                - action: include
                  match:
                    field: user_id
                    operation: greater_than_or_equal
                    value: 1000
            field: user_id

The local Collection is scoped to the containing Variable and is not addressable
elsewhere.

If the same Collection later needs reuse by another Variable, Check, Filter,
Set, or other named node, it should be promoted to a named
`*-collection`.

## Colocated Filters

The same authoring principle applies to filters.

Instead of requiring authors to create a separately named State solely so that a
Collection can reference that State as a filter, NG may allow the filter
predicate to be written directly in the Collection when the predicate has no
independent reuse value.

Example:

    collections:
      interactive-users-collection:
        capability: unix.password
        filters:
          - action: include
            match:
              field: user_id
              operation: greater_than_or_equal
              value: 1000

This preserves the semantic role of the filter while making the Collection
self-contained and easier to read.

A reusable or independently meaningful filter/state may still be promoted to a
named node if NG ultimately supports that form.

## Design principle

> A semantic construct that is used only once and has no independent identity or
> reuse requirement MAY be colocated with its owning construct. A construct that
> is reused or independently addressable SHOULD be promoted to a named node.

This principle could reduce the object/state/variable indirection that makes
some valid OVAL content difficult to author and review, while still preserving
the same dependency semantics.

## Conversion behavior

This proposal applies primarily to **new native SCAP-NG content**.

For lossless SCAP 1.4 conversion:

- existing OVAL Object boundaries should remain named NG Collections;
- existing OVAL Variable boundaries should remain named NG Variables;
- existing State/filter boundaries should remain recognizable when present in
  the source;
- the converter should not collapse source nodes merely because NG allows a more
  compact native representation.

This preserves source-graph fidelity and makes side-by-side validation easier.

## Board questions

1. Should NG support anonymous/local Collections scoped to a single Variable?
2. Should NG permit filter predicates to be colocated directly inside a
   Collection rather than requiring an independently named State?
3. Should the general rule be that one-use constructs may be local while reused
   constructs must be named/addressable?
4. Are there interoperability, diagnostics, or result-traceability reasons that
   would require every Collection or filter predicate to have a stable ID?
5. Should conversion retain original OVAL decomposition even when native NG
   authoring could express the same semantics more compactly?

## Rationale for Board review

This is more than YAML shorthand. It changes the native authoring abstraction
while intentionally retaining OVAL semantics.

The feature appears promising because it:

- reduces artificial one-use Objects/States;
- makes Variables and Collections easier to understand in isolation;
- keeps related collection/filter semantics together;
- lowers authoring burden;
- preserves an upgrade path to named/reusable nodes; and
- does not require loss of SCAP 1.4 conversion fidelity.
