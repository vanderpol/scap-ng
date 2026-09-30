# SCAP-NG v003 OVAL Round-Trip Research Harness

This directory now contains the lossless-semantic round-trip harness used to
exercise SCAP 1.4 OVAL against the native SCAP-NG v003 assessment model.

The primary pipeline is:

1. source OVAL;
2. native SCAP-NG v003 assessment lowering;
3. regenerated OVAL 5.12.3;
4. ID-independent semantic comparison;
5. XSD validation;
6. embedded Schematron comparison against the source baseline.

The harness is intentionally fail-closed. Unsupported constructs are reported
explicitly rather than silently dropped. Schema-deprecated OVAL tests are
conversion blockers unless an explicit support override marks a schema
deprecation as reinstated.

## Current regression tiers

The current gates include:

- the complete SCAP 1.4 OVAL Self-Assertion corpus;
- synthetic stress fixtures for variable/function/set behavior;
- RHEL 10 per-rule OVAL singles;
- complete RHEL 10 aggregate OVAL;
- published RHEL 9 and Oracle Linux 9 per-rule OVAL closures;
- Windows 11 and Windows Server 2025 platform-expansion gates.

The aggregate harness deliberately separates two questions:

- can independently lowered split assessments be merged into one valid OVAL
  document without semantic loss?
- can semantically identical dependency nodes then be safely deduplicated?

These are separate gates so local native identifiers cannot accidentally cause
cross-assessment collisions.

## Semantic comparison rules

The comparator is independent of regenerated IDs. It normalizes Tests, Objects,
States, Variables, Sets, Filters, Variable Components, criteria logic, and the
supported OVAL function surface into an ID-independent graph before comparison.

### `extend_definition`

SCAP-NG v003 intentionally does **not** preserve `extend_definition` as a native
assessment construct.

During conversion the referenced Definition is recursively dereferenced and its
criteria expression is substituted into the referring expression. The following
edge semantics are retained and applied to the substituted expression:

- `negate`;
- `applicability_check`.

Therefore a regenerated OVAL document is not required to recreate the original
`extend_definition` serialization. A source reference and an equivalent
flattened criteria expression compare equal when their truth semantics match.

Metadata belonging only to the dereferenced supporting Definition is treated as
legacy provenance/descriptive material, not as part of the substituted truth
expression. Root Definition class, version, deprecation status, and assessment
title are preserved independently.

This is an intentional structural divergence and must remain documented in
round-trip structural-diff evidence.

## Schematron baseline policy

Self-Assertion and other source corpora sometimes intentionally contain content
that produces Schematron reports or assertions. Regenerated content is therefore
not required to be "cleaner" than its source.

The gate instead requires that the round trip introduce **no new Schematron
findings** after OVAL identifiers are normalized. This prevents the converter
from hiding source behavior while still detecting newly introduced validity or
constraint problems.

## Structural-diff policy

Semantic equality is the primary gate, but XML differences are also classified.
Expected categories currently include:

- regenerated OVAL IDs and references;
- `extend_definition` dereferencing;
- generator metadata regeneration;
- descriptive/provenance metadata separation;
- comment normalization;
- dependency duplication in the pre-dedup aggregate harness.

Any semantic difference is unclassified and fails the gate. Aggregate dependency
duplication is followed by a separate semantic-deduplication gate, whose output
must remain root-semantically equivalent and XSD/Schematron valid.

## Main tools

- `roundtrip_corpus_v003.py` — per-definition corpus round trip.
- `roundtrip_aggregate_v003.py` — complete-document aggregate round trip.
- `native_assessment_to_oval.py` — native v003 assessment to OVAL emitter.
- `compare_oval_semantics.py` — independent ID-free semantic normalizer.
- `dedup_oval_semantic.py` — semantic dependency reuse/deduplication.
- `verify_aggregate_roots.py` — post-dedup root verification.
- `validate_embedded_schematron.py` — embedded OVAL Schematron validation.
- `compare_schematron_baseline.py` and
  `compare_schematron_documents.py` — source-baselined Schematron gates.
- `classify_structural_diff.py` — XML structural-difference classification.

Legacy fixture-only `ng_to_oval.py` remains useful as a compact stress-fixture
emitter, but the corpus and aggregate harnesses are the authoritative v003
round-trip evidence path.
