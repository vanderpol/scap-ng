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

## 9. Public-corpus migration gate

Before the SCAP-NG specification is considered stable for final publication,
the project SHALL demonstrate repeatable forward conversion of a declared,
versioned public SCAP 1.4 corpus.

The corpus SHALL be defined by a checked-in manifest that identifies immutable
source revisions/artifacts and digests.

The migration process SHALL provide construct-level accounting sufficient to
demonstrate:

- zero silently ignored Rules/checks/definitions;
- zero silently discarded source constructs;
- explicit status for every migrated policy/check component;
- explicit unsupported or review-required reasons;
- traceability from NG source back to the legacy source through authoring
  comments and/or conversion reports.

Representative differential testing SHOULD compare legacy and NG execution for:

- Platform/applicability decisions;
- per-Rule outcome;
- missing-input/not-evaluated/error behavior;
- effective Profile and Parameter resolution;
- decisive evidence/explanation where comparable.

A deprecated or intentionally unsupported legacy construct MAY block conversion
of that source content without blocking the NG specification when the standards
process has explicitly declared the construct out of scope. The converter SHALL
report such blockers rather than rewriting them silently.

## 10. Reference implementation timing

A reference scanner SHOULD eventually be used for conformance and differential
testing.

The scanner implementation SHALL NOT be allowed to define or constrain
language semantics merely because it was implemented before the source and
semantic model stabilized.


## 11. XCCDF check selectors and conversion failure

Stage-1 migration SHALL preserve XCCDF check-selection semantics. When a legacy
Rule exposes alternative checks selectable by selector, the converted SCAP-NG
policy SHALL expose semantically corresponding named check selectors and
Tailoring/Profile selection SHALL resolve to the corresponding alternative.

A converter SHALL NOT flatten multiple selectable legacy checks into a single
Assessment when doing so would change selectable behavior.

A converter SHALL NOT silently replace an unsupported automated check with a
Manual Assessment, silently choose another selector, or silently fall back to a
default check.

More generally, a conforming Stage-1 converter SHALL either produce
semantically equivalent SCAP-NG content or report a conversion error. It SHALL
NOT knowingly emit content that is weaker, stronger, or otherwise
non-equivalent to the supported source semantics.

Every newly encountered source construct that requires a new semantic mapping
SHOULD be added to the migration/conformance regression corpus after support is
implemented.


## 12. CPE inventory migration

SCAP 1.4 OVAL inventory definitions that map to CPE identifiers SHALL preserve
the product-identity relationship during Stage-1 migration.

When a legacy inventory definition is used to establish the presence of an
operating system or application and a corresponding CPE identifier is known,
the converted Platform/Inventory Assessment SHOULD retain that identifier as a
descriptive inventory output.

A successful converted Platform/Inventory Assessment MAY therefore contribute
an observed product record to the result package, including the corresponding
CPE identifier.

This inventory side output SHALL NOT change:

- Benchmark Platform truth;
- Rule selection;
- Rule applicability;
- compliance Assessment truth.

The migration converter SHALL distinguish:

1. CPE as product inventory identity; and
2. legacy CPE/XCCDF applicability processing.

Preserving the former SHALL NOT silently introduce the latter into native
SCAP-NG semantics.

If the source CPE identifier cannot be mapped unambiguously to the migrated
inventory Assessment, the converter SHOULD preserve the original relationship
as migration provenance and report it for review rather than invent a product
identifier.
