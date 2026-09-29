# Board Review: Dependency Ordering and Cycle Semantics

**Status:** proposed SCAP-NG clarification for OVAL Board review.

## Schema-derived observations

OVAL 5.12.3 defines references among Tests, Objects, States, Variables, Sets, and
Filters and requires those references to resolve to valid IDs.

For VariableComponentType, the schema documentation explicitly warns that a
variable reference must not point to the parent Variable that contains that
component, because doing so would create a race condition.

The current XSD/Schematron corpus does not appear to contain a general rule that
rejects every possible indirect dependency cycle spanning multiple Variables,
Objects, Sets, States, and Filters.

## Ordering

SCAP-NG SHOULD NOT assign semantic meaning to source-file declaration order.

A processor should resolve references and evaluate a dependency only after the
nodes required to compute that dependency are available.

For example:

    collection-a
      -> variable-a
      -> variable-b
      -> collection-b
      -> filter/state
      -> variable-c
      -> check

may be serialized in any source order. The dependency graph, not textual order,
determines evaluation prerequisites.

This aligns with the reference-based nature of OVAL rather than introducing a
new ordering model.

## Direct self-reference

A Variable SHALL NOT directly reference itself.

This retains the explicit OVAL VariableComponentType constraint.

## Indirect cycles

Proposed NG clarification:

> A dependency cycle that prevents finite deterministic evaluation SHALL be a
> content validation error.

Examples:

    variable-a -> variable-b -> variable-a

or:

    variable-a
      -> collection-a selector
      -> object values
      -> variable-a

or a longer cross-node cycle involving Collections, Filters, States, Sets, and
Variables.

A processor SHOULD detect such cycles before target collection begins when the
cycle is statically discoverable.

## Why this needs Board review

Rejecting all dependency cycles is a stronger and more explicit rule than the
current OVAL schema language, which explicitly discusses direct parent-variable
self-reference but does not appear to normatively enumerate all indirect cycle
forms.

The intent seems consistent with OVAL's evaluability model, but SCAP-NG should
not silently strengthen the language without review.

## Board questions

1. Should SCAP-NG normatively require the full Assessment dependency graph to be
   acyclic?
2. Is every indirect cycle invalid, or are there any legitimate fixed-point or
   recursively evaluable semantics that must be preserved?
3. Should cycle detection be a static content-validation requirement?
4. Should converted SCAP 1.4 content containing an indirect cycle fail
   conversion rather than attempt to reproduce implementation-specific behavior?
5. Should this clarification also be proposed back to the OVAL 5 language as a
   Schematron/validation improvement?

## Initial recommendation

Use reference-driven ordering with no semantic dependence on file order.

Retain OVAL's prohibition on direct Variable self-reference.

For NG, reject any dependency cycle that prevents finite deterministic
evaluation, but present this as an OVAL Board decision because it makes implicit
evaluator requirements explicit and may be stricter than the legacy schema.
