<!-- scap-ng-discussion-id: EXTEND-DEFINITION-NATIVE-MODEL -->

# Native representation of OVAL extend_definition

**Status:** open Board design discussion; not a ratified 0.2.0 decision.

## Why this discussion exists

OVAL `extend_definition` allows one Definition to incorporate the technical result of another Definition into its criteria. DISA content uses this pattern frequently.

SCAP-NG currently has two relevant mechanisms under discussion:

1. **Assessment-result dependency** — a consuming Assessment references another Assessment's technical result in its evaluation expression.
2. **Collected Item reuse/import** — a consuming Assessment reuses previously collected Items so those observations do not need to be gathered again.

These solve different problems and SHOULD NOT be conflated:

- Assessment-result dependency reuses the **answer/truth**.
- Item reuse reuses the **observations/evidence**.

## Current converter behavior

The current SCAP 1.4 → SCAP-NG converter already preserves `extend_definition` semantics.

Today it resolves the referenced OVAL Definition, recursively lowers that Definition's criteria, and incorporates the resulting expression into the consuming native Assessment. It detects cycles and missing referenced Definitions.

Therefore current DISA conversion does **not** depend on a native Assessment-result dependency feature. Supported content remains convertible even if the Board later chooses a different native representation for `extend_definition`.

This gives us a safe working baseline:

> OVAL `extend_definition` semantics are preserved today through semantic inlining.

## Candidate native representations

The Board should decide whether SCAP-NG should preserve the structural relationship expressed by `extend_definition`, or whether semantic inlining should remain the canonical native form.

### Option A — semantic inlining

The converter continues to lower the referenced Definition's criteria into the consuming Assessment.

Advantages:

- self-contained Assessment;
- no runtime dependency orchestration;
- simpler package/runtime graph;
- conversion already works this way.

Tradeoffs:

- loses the explicit reuse relationship present in source OVAL;
- can duplicate equivalent logic across Assessments;
- changes to a shared logical component are not structurally shared after conversion.

### Option B — Assessment-result reference

A consuming Assessment evaluates a local alias that resolves to another Assessment's technical result.

Conceptually:

```yaml
evaluate:
  all:
    - test: local-test
    - assessment: shared-prerequisite
```

Advantages:

- directly reflects the conceptual role of OVAL `extend_definition`;
- preserves logical reuse;
- can also support conditional evaluation based on another Assessment result;
- may reduce duplicated native logic.

Tradeoffs:

- requires a clear dependency/binding model;
- raises packaging, cycle, invocation, caching, provenance, and execution-order questions;
- requires deciding where the alias-to-Assessment binding belongs.

## Binding-level question

Even if Assessment-result references are retained, the current syntax should not be treated as settled.

Possible binding levels include:

- inside the consuming Assessment;
- at the Rule/check-selection layer;
- in the compiled package/manifest;
- in an Assessment Request/runtime binding;
- through an explicit exported-result contract.

A useful design constraint may be:

> The Assessment expression consumes a **local named result alias**, while the binding of that alias to a concrete Assessment identity is resolved outside the expression itself.

That would keep executable logic readable while separating authoring semantics from packaging/runtime resolution.

## Relationship to conditional evaluation

Conditional evaluation and `extend_definition`-style result reuse are complementary.

A condition may be based on:

- a local Test result; or
- another Assessment's technical result.

This does not imply that the conditional mechanism must own the dependency binding model.

## Relationship to collected Item reuse

Collected Item reuse is a separate optimization/semantic capability.

An Assessment may need the result of another Assessment without any of its Items. Conversely, two Assessments may reuse the same collected Items while reaching independent technical results.

A future implementation could use both:

1. reuse prior Items to avoid recollection; and
2. reuse another Assessment's technical result where the evaluation logic requires it.

Neither mechanism should silently imply the other.

## Questions for the OVAL Board

1. Should native SCAP-NG preserve an explicit analog of OVAL `extend_definition`, or should conversion inline referenced criteria?
2. If a native Assessment-result reference exists, should it be a core Assessment-language construct or orchestration/binding metadata one layer above?
3. Should the consuming Assessment reference:
   - another Assessment as a whole;
   - a named exported result/output;
   - or only a local alias whose concrete binding is supplied externally?
4. How should cycles be detected and reported?
5. When the same dependency is referenced multiple times under the same target/binding context, is one invocation result reused?
6. How should provenance show that a result came from another Assessment?
7. Should conversion preserve the source `extend_definition` relationship when possible, even if semantic inlining remains valid?
8. Should a converter be permitted to choose either representation when they are provably equivalent, or should canonical NG require one form?

## Current recommendation for review

Do **not** treat the current `assessment-result-dependency.assessment.yaml` sample as a ratified new feature.

Treat it as:

> an illustrative candidate native representation of the existing OVAL `extend_definition` semantic.

Until the Board decides otherwise, the current converter's semantic inlining remains the established migration behavior.
