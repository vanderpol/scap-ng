# Draft future Assessment features

**Status:** non-normative design draft; deferred; not part of JSON Schema v0.1.0

This document makes likely future Assessment-language directions visible to
reviewers without turning unsettled examples into executable schema contracts.
The authoritative decision history remains in GitHub Issues #25 and #44.

Nothing in this document changes current SCAP 1.4 conversion output.

## 1. Conditional evaluation

Owner-directed 2026-10-03 experiment:
[conditional known-result content](../../tests/conditional-0.2.0/README.md).
It demonstrates six-state guard handling, nested/dependent conditions, skipped
paths, intrinsic applicability and a proposed explicit `not_applicable` outcome
with a reason. Its controlled Test-result model and fixture grammar are
experimental; passing them does not promote the proposal into v0.1.0 or claim
that a released v0.2.0 implementation exists. Conditional normalizer upgrading
is deferred until implemented/tested/merged 0.2.0, tracked in
[issue #126](https://github.com/vanderpol/scap-ng/issues/126).

SCAP-NG is considering a constrained declarative conditional-evaluation
construct.

Two use cases are explicitly required if the feature is adopted:

1. branch on a local Test result;
2. branch on the result of a statically declared dependent Assessment,
   including an existing applicability Assessment.

Illustrative semantics only:

```yaml
evaluate:
  if:
    test: fips-enabled
  then:
    test: fips-policy-correct
  else:
    test: normal-policy-correct
```

and:

```yaml
evaluate:
  if:
    assessment_result: server-role
    equals: true
  then:
    test: dc-setting-correct
  else:
    test: member-setting-correct
```

The second form SHALL NOT require duplication of the referenced applicability
Assessment's Tests, Objects/Collections, Variables, or criteria.

If adopted, all possible branches and dependencies must remain statically
declared in signed content. Conditional evaluation must not become a general
scripting mechanism and must not dynamically construct shell commands, SQL,
paths, capability names, or unsigned content.

Open decisions include:

- final syntax, including whether a declarative `case/when` surface is clearer
  than programming-language-like `if/elseif/else`;
- propagation of `error`, `unknown`, and `not_applicable`;
- short-circuit behavior versus semantic evaluation;
- dependency-cycle handling;
- whether typed Variables/inputs may be conditional operands;
- whether ordinary Assessments may produce runtime `not_applicable`;
- result fields explaining which branch was selected and why.

### Conversion boundary

The SCAP 1.4 -> SCAP-NG converter should normally ignore this feature entirely.
It SHALL NOT invent conditionals merely because converted content could be made
shorter or more elegant.

Only a concrete legacy construct that cannot otherwise be represented
losslessly may justify converter emission of the future conditional construct.
Such a case must be backed by source evidence and regression tests.

## 2. Shared collection execution

**Partial promotion note:** first-class Assessment-result dependencies are no
longer deferred; they are part of the current Assessment Method and executable
schema. This section now tracks only the still-deferred problem of sharing
runtime collection execution and materializing reused Items.

The design must distinguish:

- Assessment-result dependency;
- authored Object/Collection definition reuse;
- runtime collection-execution reuse;
- Item/result materialization.

The current working principle is:

> Share collection work at runtime; materialize the observations needed to make
> a standalone consuming Assessment result coherent.

For example, if a shared collection execution produces 500 Items and a
consuming Assessment reuses those observations, the consuming Assessment may
serialize local/imported Item representations before Items produced by its own
additional Objects/Collections. Its Tests then reference Items available within
that same Assessment result.

This duplicates result bytes but avoids repeating the expensive collection
operation and keeps a standalone Assessment result independently understandable.

Imported Items should preserve provenance back to the shared collection
execution even though their result-local identifiers belong to the consuming
Assessment.

Open decisions include:

- whether all available imported Items or only actually consumed Items are
  materialized;
- local sequential IDs versus stable content-derived IDs;
- provenance fields connecting local Items to the shared execution;
- interaction with evidence caps and incomplete collection;
- normalized whole-scan result representations that can deduplicate observations
  without making standalone Assessment singles dependent on other result files;
- execution-DAG and cache-key rules;
- redaction/sensitivity behavior.

## 3. Terminology note

This decision has been promoted into the current design: native authoring uses
**Object**, **Test**, **State**, **Variable**, and **Item** where those concepts
retain the corresponding OVAL semantics. **Collection execution** describes the
runtime act of evaluating an Object; `Collection` is not the authored node
name.

The current v0.1.0 Assessment schema therefore validates `objects`,
`states`, `tests`, and `variables`. Older iteration artifacts that use
authored `collections` are historical baselines, not current schema examples.

## 4. Promotion rule

A deferred feature should move into normative specification text and executable
JSON Schema only after:

1. semantics are agreed independently of syntax;
2. result/error behavior is defined;
3. security implications are reviewed;
4. examples cover important real-world cases;
5. conversion impact is understood;
6. conformance tests can distinguish valid from invalid behavior.

Until then, these sections are design guidance only.
