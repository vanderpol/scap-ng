# Iteration 003 Conversion Contract

## Purpose

This document defines the conversion behavior that the clean-room SCAP 1.4
up-converter must satisfy before generated SCAP-NG source is accepted.

## 1. Source authority

The converter SHALL consume pinned original SCAP 1.4 artifacts/components.

Generated iteration-001 and iteration-002 YAML SHALL NOT be used as authoritative
input to iteration 003.

The converter SHALL record a cryptographic digest of every authoritative input
artifact used for a conversion.

## 2. Semantic preservation

For every supported source construct that can affect platform truth, Rule
applicability, Rule selection, Profile/Tailoring resolution, check selection,
Assessment behavior, parameter/input flow, result truth/result state, or decisive
evidence, the converter SHALL either represent the construct exactly in the
semantic IR and prove a native SCAP-NG lowering, or stop the affected conversion
path with an explicit diagnostic.

The converter SHALL NOT silently approximate, drop, repair, weaken, strengthen,
or reinterpret source semantics.

## 3. Serialization is not semantics

The converter is not required to preserve source serialization when that
serialization has no behavioral meaning.

Raw XML trees, namespaces, component filenames, hrefs, source element ordering
that has no defined semantic effect, and legacy wrapper structures are provenance
rather than native content.

## 4. Versioned semantic IR

The converter SHALL use a versioned semantic IR independent of both SCAP 1.4 XML
and final SCAP-NG YAML.

The IR SHALL:

- contain semantic concepts rather than XML element mirrors;
- use typed fields for known behavior;
- distinguish explicit source values from effective/defaulted behavior when that
  distinction matters;
- carry stable internal IDs suitable for provenance linkage;
- preserve unresolved references explicitly;
- carry no raw XML source tree;
- support deterministic serialization for regression testing.

## 5. Separate provenance ledger

Source lineage SHALL be emitted separately from the semantic IR/native source.

The provenance ledger MAY contain original XCCDF/OVAL/OCIL/CPE IDs, source
component paths/hrefs, XML namespace information, source locations, normalization
decisions, source hashes, and mappings from source entities to IR/emitted NG
entities.

Native NG files MAY contain a compact provenance reference if required, but SHALL
NOT embed the full ledger.

## 6. Explicit accounting

Every behaviorally relevant source construct SHALL end in one of these states:

- **represented_exactly** — directly represented with equivalent semantics;
- **represented_normalized** — different syntax/shape with proven equivalent semantics;
- **deferred_design** — intentionally withheld pending an explicit SCAP-NG design decision;
- **requires_review** — extraction succeeded but equivalence is not yet proven;
- **unsupported** — conversion cannot continue without semantic loss.

A successful full conversion SHALL contain no behaviorally relevant
requires_review or unsupported items.

deferred_design is not success for a source path that actually requires the
deferred feature.

## 7. Native-source cleanliness gate

A native renderer SHALL reject attempts to emit known legacy serialization
residue as executable/source content.

At minimum, regression tests SHALL prevent native output fields equivalent to
source_tree, raw XML namespace fields, raw XCCDF check-content-ref structures,
raw OCIL questionnaire structure, CPE dictionary XML trees, and OVAL
definition/test/object/state source IDs used as native execution IDs.

A provenance report is exempt from this gate.

## 8. Profile behavior

Profiles SHALL be represented as effective deltas rather than fully expanded
snapshots.

Benchmark membership/default selection is the baseline. Profile output SHALL
serialize only changes required to reproduce effective Profile behavior,
including check-selector and parameter/value refinements.

Inherited/extended Profile behavior SHALL be resolved and verified without
copying the entire Benchmark into each Profile.

## 9. Check selection

The split architecture remains:

    Benchmark Rule -> Policy -> selected check -> Assessment

The semantic IR SHALL preserve all selectable XCCDF check alternatives and the
effective default.

An explicit selector request that cannot be resolved SHALL be a conversion or
resolution error; it SHALL NOT silently fall back.

## 10. Policy role and runtime result research

XCCDF/Policy role semantics SHALL be preserved during conversion.

The separate design questions of assessment-derived informational,
indeterminate, and runtime notapplicable remain deferred until lossless source
conversion is fully understood. Iteration 003 SHALL expose the source semantics
needed to revisit those decisions without prematurely redesigning them.

## 11. OVAL handling

OVAL conversion SHALL preserve dependency closure and result-affecting semantics,
including criteria/criterion/extend_definition composition; tests, objects,
states, variables; object sets and filters; existence/cardinality behavior;
check/check_existence/state operators; variable and component transforms;
datatypes and operations; and result/error propagation where applicable.

Effectively deprecated tests remain explicit conversion blockers unless current
project governance records a reinstatement.

## 12. Verification

Schema-valid YAML or JSON is never proof of conversion correctness.

Acceptance requires, as appropriate, structural accounting tests, semantic
fingerprint tests, focused OVAL Self-Assertion conformance, production
four-anchor regression cases, profile/check-selector equivalence checks, and
differential execution when the reference scanner becomes available.

## 13. Public-tool constraint

Reusable ingestion, IR, validation, diagnostics, provenance, and lowering code
SHOULD remain benchmark/vendor neutral.

NIWC/DISA-specific corpus orchestration belongs in research tooling or manifests,
not in reusable converter logic.


## 14. Native legacy-residue prohibition

Native SCAP-NG output SHALL NOT contain XCCDF, OVAL, OCIL, or CPE Applicability
Language namespaces, identifiers, hrefs, XML element names, or other
serialization residue.

This includes, but is not limited to:

- identifiers beginning with legacy XCCDF/OVAL/OCIL naming conventions;
- XML namespace URIs;
- check-content-ref/check-content XML structures;
- OVAL definition/test/object/state IDs;
- OCIL questionnaire IDs;
- source component filenames/hrefs used as runtime bindings;
- raw CPE Applicability Language structures.

Such data MAY appear in separate conversion provenance/evidence only.

If the converter encounters a source case where preserving one of these legacy
references appears necessary to preserve semantics in native NG, it SHALL stop
that conversion path and report a design-review blocker. It SHALL NOT emit the
legacy reference into native NG without explicit project-owner approval.
