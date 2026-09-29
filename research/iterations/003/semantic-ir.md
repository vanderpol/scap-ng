# Iteration 003 Semantic IR

## Status

Initial contract for the clean-room converter. This IR is internal to migration
tooling and is deliberately not a proposal for final SCAP-NG authoring syntax.

## Design goal

The IR exists to answer:

> What behavior did the SCAP 1.4 source specify?

It must answer that without preserving the XML document shape.

## Layering

### Benchmark/policy layer

Captures:

- Benchmark identity, title, version, and status;
- default Rule membership/selection behavior;
- logical Group membership;
- Rule identity, title, severity, weight, and role;
- requires/conflicts;
- Benchmark and Rule platform/applicability references;
- Profile inheritance and effective deltas;
- Value/parameter declarations and Profile refinements;
- selectable checks and their selectors/default relationship.

### Assessment-reference layer

Captures check alternatives without embedding XCCDF XML:

- selector;
- check-system semantic kind;
- negate/multi-check behavior;
- referenced automated-content target;
- inline/manual procedure;
- exported parameter bindings.

Source hrefs and opaque IDs used only for resolving the original package live in
provenance. The IR uses stable resolver keys where cross-component resolution is
still pending.

### Assessment semantic layer

Later OVAL/OCIL lowering will capture normalized collection, derivation, and
evaluation semantics.

This layer is intentionally not implemented by the first 003 checkpoint.

### Diagnostics/accounting layer

Every source construct encountered during extraction is classified as
represented, deferred, review-required, or unsupported.

A clean extraction has no unaccounted behaviorally relevant construct.

## Explicit vs effective values

Where SCAP/XCCDF defaulting affects behavior, the IR records the effective value.

Where it matters for auditability, provenance records whether the effective
value was explicit in source or obtained from the specification default.

This avoids contaminating the semantic model with serialization trivia while
still permitting exact review.

## Internal IDs

IR IDs are deterministic converter-local identifiers.

They are not required to reuse XCCDF/OVAL IDs and are not intended to become
native SCAP-NG execution identifiers.

The provenance ledger maps source identities to IR identities.

## Prohibited shortcuts

The following are not accepted as semantic modeling:

- storing an XML subtree because a construct has not been understood;
- copying arbitrary XML attributes into a catch-all map and declaring success;
- preserving an OVAL definition as raw XML and calling it converted;
- treating a source href as assessment semantics;
- using source-local OVAL IDs as proof that two assessments are different;
- using schema validation as semantic accounting.

If a construct is not modeled, it receives a diagnostic.

## First checkpoint

The first 003 implementation covers the XCCDF Benchmark/policy layer only.

It produces:

- a semantic IR JSON file;
- a separate provenance JSON file;
- a diagnostics JSON file containing unsupported/unmodeled construct accounting.

No SCAP-NG YAML renderer is enabled during this checkpoint.
