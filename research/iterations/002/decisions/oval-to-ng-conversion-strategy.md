# OVAL to SCAP-NG Conversion Strategy

**Status:** working design decision  
**Iteration:** 002  
**Scope:** OVAL-to-NG conversion fidelity and later native refactoring

Normative terms in this research note are provisional but intentionally use
SHALL, SHALL NOT, SHOULD, SHOULD NOT, and MAY in the sense expected for a
future standards specification.

## Core principle

The first responsibility of an OVAL-to-SCAP-NG converter is semantic fidelity,
not source elegance.

For supported OVAL content, the initial NG conversion SHALL preserve the
effective evaluation semantics of the source OVAL.

A converter SHALL NOT silently:

- reinterpret ambiguous source logic;
- repair likely authoring mistakes;
- merge distinct source conditions because they appear redundant;
- replace repeated logic with a stronger or broader native abstraction;
- infer missing cases in a repeated pattern;
- change defaulted OVAL semantics while making them explicit in NG.

If lossless conversion is not possible, the converter SHALL report a blocker
rather than approximate behavior without disclosure.

## Two-stage model

OVAL migration SHOULD be treated as two conceptually separate stages.

### Stage 1 — lossless conversion

    OVAL
      ->
    semantically equivalent NG

The Stage 1 output SHOULD:

- make OVAL defaults explicit;
- replace opaque cross-object identifiers with readable local names where doing
  so does not alter semantics;
- preserve OVAL result behavior and error states;
- preserve source anomalies and redundancies when required for equivalence;
- retain authoring-time provenance sufficient to trace native constructs back
  to source OVAL without making historical lineage part of scanner semantics.

The Stage 1 artifact establishes a regression-testable semantic baseline.

### Stage 2 — native semantic refactoring

    lossless NG
      ->
    cleaner native NG

Stage 2 MAY:

- replace repeated low-level patterns with higher-level capabilities;
- introduce clearer structured collectors;
- simplify variable/transform chains;
- consolidate provably equivalent repeated logic;
- promote reusable Assessments;
- improve result/evidence declarations;
- reorganize logic into clearer collect/derive/assert structures.

Any Stage 2 transformation that can change observable behavior SHALL require
explicit review and provenance.

Semantics-preserving optimizations MAY be automated only when equivalence can
be demonstrated.

## Why keep the stages separate

OVAL content often contains:

- hidden/default semantics;
- repeated but subtly different logic;
- complex variable chains;
- implementation-shaped expression trees;
- historical inconsistencies and authoring defects.

Aggressive cleanup during conversion makes it difficult to distinguish:

1. a faithful migration;
2. a semantics-preserving optimization; and
3. an accidental behavioral change.

A lossless baseline lets tools compare OVAL and NG results before content is
modernized.

## Native evolution

SCAP-NG SHOULD provide authors with richer, clearer primitives than OVAL where
those primitives reduce complexity without sacrificing portability or
determinism.

The existence of a lossless conversion path SHALL NOT require future native
content to preserve OVAL's Definition/Test/Object/State/Variable structure.

As richer native constructs become available, authors MAY deliberately refactor
lossless converted Assessments into simpler native forms.

Over time, content complexity should decrease because authors can express
intent directly instead of recreating historical OVAL implementation patterns.

## Validation strategy

A migration toolchain SHOULD support regression testing between source OVAL and
Stage 1 NG using representative system-state fixtures.

Where practical, the same collected-state fixture SHOULD be evaluated by both
engines and compared for:

- final result;
- intermediate truth/error outcomes where relevant;
- object existence behavior;
- cardinality behavior;
- variable/transformation results;
- unknown/error/not-evaluated propagation.

Stage 2 refactoring SHOULD be regression-tested against the Stage 1 baseline.

## Source defects and suspected intent

When the source OVAL appears internally inconsistent or likely incorrect, the
converter SHALL preserve the source behavior and record the anomaly.

For authoring source, a concise anomaly note SHOULD normally be preserved as a
comment adjacent to the affected content.

Tooling SHOULD also be able to emit a separate conversion/review report with
full machine-readable lineage and anomaly detail.

A source anomaly SHALL NOT be silently corrected during lossless conversion.

## Historical provenance

Historical conversion lineage is useful for authors, reviewers, regression
testing, and migration tooling, but it is not normally scanner semantics.

SCAP-NG authoring source SHOULD preserve concise historical provenance as
comments where it materially helps review, for example:

    # Source OVAL test: oval:...:tst:25303503
    # Source OVAL object: oval:...:obj:25303503
    # Source anomaly preserved: nominal b64 case resolves to b32.

A converter SHOULD be able to emit a separate machine-readable conversion
report containing complete lineage such as source Definitions, Tests, Objects,
States, Variables, defaulted OVAL behavior, anomalies, and transformation
history.

Historical OVAL/XCCDF lineage SHALL NOT be required in the compiled
scanner-facing Assessment object merely because the content was converted from
legacy SCAP.

The compiler SHOULD discard authoring comments from canonical scanner packages.

Runtime/result provenance is a separate concern. Compiled packages and results
MAY carry provenance needed to identify what actually executed, such as stable
Assessment identity/version, Benchmark identity/version, scanner identity,
effective inputs, execution timestamps, and result producer.

## Relationship to current design samples

The five RHEL 9 design-review samples intentionally include both conservative
and aggressive-native ideas.

In particular, the structured audit-rule matrix example is a candidate for
Stage 2 native refactoring, not proof that the Stage 1 converter should rewrite
the source OVAL into that form automatically.

This distinction is intentional and should remain visible during Assessment
language design.
