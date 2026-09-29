# Board Review: Decisive / Short-Circuit Evaluation

**Status:** proposed SCAP-NG execution behavior for OVAL Board review.

## Schema-derived foundation

OVAL 5.12.3 defines aggregation truth tables for CheckEnumeration and
OperatorEnumeration, including True, False, Error, Unknown, Not Evaluated, and
Not Applicable child results.

The authoritative tables permit an aggregate result to become decisive before
all children are evaluated in several cases. Examples include:

- ALL / AND: one False is sufficient to determine False;
- AT LEAST ONE / OR: one True is sufficient to determine True;
- ONLY ONE: a second True is sufficient to determine False;
- NONE SATISFY: one True is sufficient to determine False.

Other cases require additional evaluation to distinguish among possible final
results.

The schema defines the correct aggregate result. It does not appear to require a
specific child evaluation order or require exhaustive evaluation once the final
result is already determined.

## Proposed NG rule

SCAP-NG implementations MAY use decisive (short-circuit) evaluation when the
applicable schema-derived aggregation semantics prove that remaining children
cannot change the aggregate result.

A skipped child SHALL be represented as Not Evaluated (or the NG-native
equivalent) rather than silently omitted when result detail includes the child.

Short-circuit evaluation SHALL NOT alter:

- the aggregate result;
- the semantics of any child that was actually evaluated;
- dependency resolution required by an evaluated child; or
- source/content semantics.

## Exhaustive versus decisive execution

NG should consider defining two execution strategies:

- **exhaustive** — evaluate all reachable child checks needed by the selected
  assessment path, even after the aggregate result becomes decisive, to maximize
  evidence and failure discovery;
- **decisive** — stop evaluating siblings once the aggregate result is provably
  fixed by the normative aggregation table.

Both strategies must produce the same aggregate result for the same content and
target state.

The choice SHOULD be an implementation/execution policy rather than content
authoring semantics unless a concrete use case proves that content must mandate
one strategy.

## Example: ALL

Given:

    evaluate:
      all:
        - check: check-a
        - check: check-b
        - check: check-c

If check-a is False, the ALL result is False regardless of later Error,
Unknown, Not Evaluated, or Not Applicable results permitted by the normative
table.

A decisive implementation may therefore return:

    check-a: false
    check-b: not_evaluated
    check-c: not_evaluated
    overall: false

An exhaustive implementation may evaluate all three and still return:

    overall: false

The difference is evidence completeness, not truth semantics.

## Board questions

1. Should SCAP-NG explicitly permit decisive/short-circuit evaluation when the
   normative result is already fixed?
2. Should exhaustive evaluation remain the default for compliance/evidence-rich
   scans, with decisive evaluation as an implementation option?
3. Must skipped children be surfaced as Not Evaluated in results?
4. Should execution strategy be scanner/runtime policy rather than authored
   content?
5. Are there cases where evidence collection, diagnostics, or result
   reproducibility require exhaustive evaluation despite a decisive result?

## Initial recommendation

Permit both exhaustive and decisive execution, with identical aggregate truth
semantics.

For compliance-oriented scanning, exhaustive evaluation is likely the better
default because it reports all failures in one run.

For performance-sensitive or applicability-style evaluation, decisive execution
can avoid unnecessary work.

The result format should record the execution strategy and identify skipped
nodes as Not Evaluated so evidence differences are explicit.
