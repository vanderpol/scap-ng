# SCAP-NG 0.3.0 schema

**Status:** active pre-alpha development tree.

This directory is a complete, independent SCAP-NG **0.3.0** schema snapshot.
It was opened from the frozen 0.2.0 baseline and is now versioned entirely as
0.3.0. Files in this directory SHALL resolve to other 0.3.0 files, not back to
the frozen 0.2.0 tree.

The 0.2.0 tree remains unchanged as historical reference. The stable 0.3
owner-review candidate is the active review target; Board publication follows
owner acceptance. Object-level `for_each`, including correlated nested
collection lineage, is integrated into this active pre-alpha tree. Automatic
SCAP 1.4 modernization is enabled only for transformation classes with an exact
equivalence proof; the current direct ObjectComponent → Variable → selector
class is proven and exercised by the review candidate.

## Change discipline

- Do not modify `schema/v0.2.0/` for 0.3.0 features.
- Every 0.3.0 schema and mapping file carries its own 0.3.0 identity/version.
- Relative schema references remain within this directory.
- Semantic changes require focused conformance evidence and human review.
- A schema-valid document is not automatically migration-equivalent,
  collector-conformant, live-target-tested, or Board-approved.

## Start here

1. [Assessment schema](assessment.schema.json)
2. [Shared capability primitives](capability-common.schema.json)
3. [Supported capability mappings](capability-mappings/supported/)
4. [Assessment result schema](assessment-result.schema.json)
5. [Package manifest schema](package-manifest.schema.json)

For accepted 0.3 collection-iteration semantics, see
[Collection `for_each`](../../specification/assessment/foreach.md). Historical
automatic-modernization proof remains under
[foreach-07](../../research/assessment-simplification/foreach-07/README.md).

## Embedded predicates and Filters

0.3 native Tests and Object/Set Filters use **local typed comparison
expressions**, not named or separately reusable States. A Filter still narrows
the observed Item population after acquisition, and before Set/Test evaluation.
Only the consumer specifies the effective capability. Source OVAL State
identifiers, titles and comments remain in non-executable migration evidence.

See [selection and filtering](../../specification/assessment/selection-and-filters.md)
and implementation/proof [#208](https://github.com/vanderpol/scap-ng/issues/208).
The frozen 0.2.0 schemas are unaffected.

## Collection `for_each`

0.3 supports typed collection expansion from a named `shared_objects` source,
including correlated chained/nested collection lineage. The semantic validator
checks source existence, acyclic dependency, lexical alias scope, datatype
compatibility, and consumption. Independent Cartesian expansion is not implicit.

Automatic SCAP 1.4 modernization remains fail-closed to transformation classes
with an exact equivalence proof; native language support is broader than the
currently proven automatic rewrite class.

See [Collection `for_each`](../../specification/assessment/foreach.md).
