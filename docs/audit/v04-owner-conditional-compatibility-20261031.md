# Ordered supplied-result conditional compatibility (#255/#268)

Implements owner Decisions **8, 24, 25 and 26** from the
[2026-10-31 register](v04-owner-final-decisions-20261031.md). This is compiler,
independent package-reader and supplied-outcome compatibility, not a scanner
implementation or a source-OVAL Boolean-to-conditional rewrite.

## Before and after

The previous canonical result compiler rejected every `if/then/else` as
unapproved, despite the now-approved schema. It also accepted old Boolean
aliases at its native entry point. The current compiler rejects native
`all/any/odd` aliases, preserves canonical `and/or/one/xor` six-state algebra,
and emits static nested blocks for the approved conditional grammar:

```yaml
evaluate:
  if: {test: local-inspection-test}
  then: {test: local-result-test}
  else_if:
    - if: {test: remote-inspection-test}
      then:
        not_evaluated: {reason: Remote ACL inspection is outside available evidence}
  else:
    not_applicable: {reason: No affected configuration is selected}
```

This is a schematic expression; it does not assert these collectors exist.
The compiled `select_first_true` instruction retains ordered guard/then blocks,
final else, original clause paths and all static reference identities. Every
named branch reference must resolve at compilation, including unselected ones.
The independent package reader builds expected blocks without importing the
compiler and compares exact instructions/source fingerprints.

| Guard | Supplied-result behavior |
| --- | --- |
| true | Execute the corresponding then block only |
| false | Try the next ordered guard, or final else |
| error / unknown / not_evaluated / not_applicable | Propagate the same technical outcome; do not run a fallback |

Only selected branches read supplied outcomes. Missing outcomes for unselected
branches are permitted; missing selected outcomes are errors. A selected
noncompliant false or unexpected error stays false/error; it never falls through
to informational follow-up. Explicit terminal reasons are retained in the trace.
An explicit authored not_evaluated that remains the final outcome emits
`manual_follow_up_required`; this is technical metadata for a Rule consumer,
not reinterpretation of Assessment class or a claim that complete Rule Results
roll-up/renderer/scanner integration has been qualified.

`compile_canonical_result_plan` and `evaluate_supplied_results` retain the
supplied-results-only boundary. They collect no Objects, execute no Test or
Variable operation, and claim no host compliance. The old research truth-table
module and all_exist/incomplete reference-oracle discrepancy are unchanged.
No existing source archive, authoring/program proof hash or library was rewritten.

## Observed validation

**44 focused tests PASS** (0.448s): new conditional suite, canonical result-plan
regression, expression schema, graph references and owner-decision schema lock.
Coverage includes all six guard outcomes, first-true order even when the selected
result is false, skipped branches, static missing references, malformed/missing
else and terminal reasons, legacy alias rejection, and class/context separation.
A new copied unit fixture (not an edited historical fixture) validates current
YAML/JSON authoring, compiles a complete package containing an ordered else_if,
then passes the independent package reader with exact external source comparison.
Its unix.file Object/owner_uid comparison is concrete, but no collection was run.

Actual converted Linux/Windows compatibility samples, wider producer/name drift,
and the rest of the editor-default catalog remain tracked in the
[reconciliation packet](v04-owner-reconciliation-20261031.md). These passing
conditional gates alone do not make PR #268 merge-ready or release-qualified.
