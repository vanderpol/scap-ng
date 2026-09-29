# Iteration 003 Conversion Contract

## Purpose

This document defines the conversion behavior that the clean-room SCAP 1.4
up-converter must satisfy before generated SCAP-NG source is accepted.

## Source authority

The converter SHALL consume pinned original SCAP 1.4 artifacts/components.
Generated iteration-001 and iteration-002 YAML SHALL NOT be authoritative input.

The converter SHALL record a cryptographic digest of every authoritative input
artifact used for conversion.

## Semantic preservation

For every supported source construct that can affect platform truth, Rule
applicability, Rule selection, Profile/Tailoring resolution, check selection,
Assessment behavior, parameter/input flow, result truth/result state, or
decisive evidence, the converter SHALL either represent the construct exactly
and prove a native lowering, or stop the affected path with an explicit
diagnostic.

The converter SHALL NOT silently approximate, drop, repair, weaken, strengthen,
or reinterpret source semantics.

## Serialization is not semantics

Raw XML trees, namespaces, component filenames, hrefs, legacy wrapper
structures, and other serialization details are provenance rather than native
SCAP-NG content unless they are proven to affect behavior.

## Versioned semantic IR

The converter SHALL use a versioned semantic IR independent of both SCAP 1.4
XML and final SCAP-NG source syntax.

The IR SHALL contain semantic concepts rather than XML mirrors, use typed fields,
preserve behaviorally relevant defaults, preserve unresolved references
explicitly, contain no raw XML source tree, and support deterministic
serialization for regression testing.

## Separate provenance ledger

Source lineage SHALL be emitted separately from native source.

The provenance ledger MAY contain original XCCDF/OVAL/OCIL/CPE IDs, source
paths/hrefs, namespace information, source hashes, and mappings from source
entities to semantic IR and NG entities.

## Explicit accounting

Every behaviorally relevant source construct SHALL be classified as:

- represented_exactly
- represented_normalized
- deferred_design
- requires_review
- unsupported

A successful full conversion SHALL contain no behaviorally relevant
requires_review or unsupported items.

## Native legacy-residue prohibition

Native SCAP-NG output SHALL NOT contain XCCDF, OVAL, OCIL, or CPE
Applicability Language namespaces, identifiers, hrefs, XML element structures,
or legacy execution IDs.

Such data MAY appear in separate conversion evidence only.

If preserving a legacy reference appears necessary for native semantics, that
conversion path SHALL stop for design review and SHALL NOT emit the reference
without explicit project-owner approval.

## Public-tool constraint

Reusable ingestion, IR, validation, diagnostics, provenance, and lowering code
SHOULD remain benchmark/vendor neutral.

NIWC/DISA-specific corpus orchestration belongs in research/evidence tooling,
not reusable converter logic.
