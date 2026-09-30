# SCAP 1.4 OVAL → SCAP-NG v003 → OVAL Compatibility Evidence

Status: active regression evidence  
Updated: 2026-09-30

This document records the current evidence for lossless OVAL semantic transport
through the native SCAP-NG v003 assessment representation. The goal is not byte-
or serialization-identical XML. The requirement is semantic equivalence with no
unexplained differences.

## Acceptance gates

A corpus is considered clean only when all of the following applicable gates pass:

1. SCAP 1.4 OVAL can be lowered into the native v003 assessment model without
   silently dropping unsupported semantics.
2. Native v003 can be regenerated as OVAL 5.12.3.
3. Source and regenerated OVAL compare equal using an ID-independent semantic
   graph comparison.
4. Regenerated OVAL validates against the authoritative OVAL 5.12.3 XSDs.
5. Regenerated OVAL introduces no new embedded-Schematron findings relative to
   its source.
6. Aggregate documents retain semantic equality after dependency deduplication.
7. Remaining structural XML differences are classified. Any unclassified
   structural difference is a failure until explained or fixed.

Deprecated OVAL tests are not converted into native SCAP-NG. They remain explicit,
intentional conversion blockers because SCAP-NG SHALL NOT support deprecated OVAL
test types.

## Current passing evidence

### SCAP 1.4 Self-Assertion

- 144 XML files.
- 167 OVAL definitions.
- 167/167 lower successfully into native v003.
- 167/167 semantic round trips are equal.
- XSD validation passes.
- Source-baselined Schematron comparison passes.
- Maximum observed dependency depth: 6.

This is the primary OVAL language-surface corpus.

### RHEL 10 per-rule singles

Source: `vanderpol/scap-content/projects/linux/rhel10/oval/`

- 405 per-rule OVAL singles.
- 786 OVAL definitions.
- 786/786 semantic round trips are equal.
- XSD validation passes.
- Source-baselined Schematron comparison passes.
- Maximum observed dependency depth: 10.
- Deepest observed root:
  `oval:navy.navwar.niwcatlantic.scc:def:28103700001`.

This is the primary real-world deep dependency-graph corpus.

### RHEL 10 complete aggregate OVAL

Source:
`U_RHEL_10_V1R2_STIG_SCAP_1-4_Benchmark-oval.xml`

- 793 definitions.
- 793/793 source roots remain semantically equal after round trip.
- Regenerated aggregate is OVAL 5.12.3 XSD-valid.
- New Schematron findings: 0.
- Semantic dependency deduplication removes 2,382 duplicate dependency nodes:
  - objects: 1,636 → 733
  - states: 1,089 → 366
  - tests: 1,493 → 822
  - variables: 124 → 39
- After deduplication:
  - 793/793 definitions remain semantically equal.
  - XSD validation still passes.
  - New Schematron findings remain 0.
- Structural-diff classification reports 0 unexplained differences.

Classified aggregate structural differences:

- regenerated OVAL IDs;
- intentional `extend_definition` dereferencing;
- descriptive/provenance metadata separation from native assessment truth
  semantics;
- generator metadata regeneration;
- comment/provenance normalization;
- semantic dependency deduplication.

### RHEL 9 published benchmark

Pinned NIWC SCAP 1.4 corpus:

- 828 definitions.
- 828/828 semantic round trips are equal.
- XSD validation passes.
- New Schematron findings: 0.
- Maximum observed dependency depth: 8.

### Oracle Linux 9 published benchmark

Pinned NIWC SCAP 1.4 corpus:

- 823 definitions.
- 823/823 semantic round trips are equal.
- XSD validation passes.
- New Schematron findings: 0.
- Maximum observed dependency depth: 8.

### Windows 11 published benchmark

The Windows 11 platform expansion passes:

- published SCAP split into per-rule OVAL dependency closures;
- all nonblocked definitions round-trip semantically;
- regenerated closures are XSD-valid;
- source-baselined Schematron comparison passes;
- deprecated OVAL test types remain explicit conversion blockers rather than
  being silently translated.

## Intentional semantic-preserving normalizations

### `extend_definition`

SCAP-NG native assessment source does not require a legacy
`extend_definition` graph. Conversion dereferences the referenced Definition
and embeds the resulting truth semantics. Therefore regenerated OVAL is not
required to reconstruct the original `extend_definition` serialization.

Flags on an `extend_definition` edge, including `negate` and
`applicability_check`, are applied to the dereferenced expression. The semantic
comparator canonicalizes the referenced and flattened forms to the same logical
expression.

### OVAL identifiers

OVAL identifiers are serialization identities rather than native SCAP-NG
semantic identities. Reverse generation may issue new OVAL IDs. Semantic
comparison is therefore ID-independent while preserving the complete reference
graph.

### Metadata and comments

Legacy OVAL comments and descriptive/provenance metadata are not assessment truth
semantics. Useful native titles and required root Definition metadata are
preserved, while legacy provenance is retained separately from native assessment
logic. This separation is intentional and SHALL be documented rather than
mistaken for semantic loss.

## Regression rule

Any future change to the native v003 assessment model, OVAL converter, reverse
generator, comparator, or deduplication machinery SHALL keep the established
corpora green. A newly observed difference is a defect until it is either fixed
or documented as an intentional semantic-preserving normalization.
