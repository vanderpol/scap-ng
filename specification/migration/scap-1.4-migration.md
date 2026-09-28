# SCAP 1.4 to SCAP-NG Migration

**Status:** pre-alpha normative draft

## 1. Conversion requirement

SCAP-NG SHALL provide a defined migration path from supported SCAP 1.4 content.

Conversion capability is a design requirement, not an optional convenience.

A candidate SCAP-NG syntax SHALL NOT be considered mature until representative
published SCAP 1.4 content can be converted without silent semantic loss.

## 2. Lossless-first conversion

Migration SHALL separate:

1. Stage 1 — lossless semantic conversion;
2. Stage 2 — optional native semantic refactoring.

Stage 1 SHALL preserve effective behavior, including source anomalies where
required for equivalence.

A converter SHALL NOT silently repair likely authoring errors.

If lossless conversion is not possible, the converter SHALL report the blocker
rather than approximate behavior without disclosure.

## 3. Explicit legacy defaults

Where legacy SCAP/OVAL semantics rely on behavior-affecting defaults, Stage 1
NG output SHOULD make those semantics explicit.

## 4. Native refactoring

Stage 2 MAY replace legacy implementation complexity with clearer native
capabilities or expressions.

A behavior-changing Stage 2 transformation SHALL require explicit review.

Stage 2 SHOULD be regression-tested against the Stage 1 baseline.

## 5. Policy normalization

Migration MAY normalize legacy representation when the effective policy is
preserved.

Examples include:

- reducing Profile selection snapshots to subtractive deltas;
- separating product Platform identity from reusable applicability when exact;
- resolving an effective legacy Value/Profile selection into an NG Parameter
  binding.

A converter SHALL NOT preserve obsolete mechanism merely for syntactic
similarity when equivalent policy can be represented directly and losslessly.

## 6. Manual checks

XCCDF Check Text SHALL be preserved as a valid Manual Assessment procedure.

Lossless migration SHALL NOT depend on OCIL being present.

Legacy OCIL that is only a generated interaction wrapper around Check Text MAY
be omitted when no additional authoritative semantics are lost, because the
SCAP-NG Manual Assessment contract supplies default operator interaction.

## 7. Provenance

Legacy identifiers and concise lineage SHOULD be preserved in authoring
comments when useful.

Complete conversion lineage SHOULD be available from a separate conversion
report.

Historical migration lineage SHALL NOT be required in scanner-facing
Assessment semantics.

## 8. Corpus validation

The project SHOULD demonstrate conversion across a broad, pinned corpus of
published SCAP 1.4 content before declaring the format stable.

Migration tooling SHOULD report unsupported constructs and conversion status
explicitly.
