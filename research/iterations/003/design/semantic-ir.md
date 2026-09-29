# Iteration 003 Semantic IR

**Status:** internal converter contract, not native SCAP-NG source syntax

The IR exists to answer:

> What behavior did the SCAP 1.4 source specify?

It must answer that without preserving the XML document shape.

## Layers

### Benchmark/policy semantics

Captures Benchmark identity, Rule membership, meaningful Group structure,
Profiles, Parameters, platform/applicability references, Rule policy
attributes, and selectable check alternatives.

### Assessment references

Captures selector, modality, negate/multi-check behavior, parameter bindings,
and resolved links to Assessment semantics without embedding legacy XML.

### Assessment semantics

Captures normalized collection, derivation, and evaluation behavior.

### Diagnostics/accounting

Records unsupported, deferred, or review-required constructs.

## Boundary rule

The semantic IR is not SCAP-NG authoring syntax.

It SHALL NOT dictate the native file layout merely because a parser happens to
represent data a particular way.

Raw XML trees, namespace URIs, source IDs, and source component hrefs are
provenance and do not belong in the semantic IR unless their behavior is itself
the subject of conversion.
