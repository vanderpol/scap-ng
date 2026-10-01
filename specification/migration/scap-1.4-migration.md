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

### XCCDF check-content reference fallback

XCCDF 1.2 defines multiple `check-content-ref` elements as **alternative
locations in source order**, not multiple checks to execute. Migration SHALL
preserve that resolution semantics during compilation:

1. attempt `check-content-ref` alternatives in XML document order;
2. select the first reference whose content can be resolved successfully;
3. use embedded `check-content` only when none of the references resolve;
4. report a conversion blocker if no reference resolves and no usable embedded
   content exists.

The converter SHALL NOT execute or combine multiple successfully resolvable
alternatives. Their purpose is retrieval fallback.

This legacy retrieval mechanism SHOULD be normalized away before scanner
runtime. A compiled SCAP-NG package SHALL contain the selected, resolved
Assessment/check content (or the native representation derived from it) and
SHALL NOT require runtime network/location fallback across legacy
`check-content-ref` alternatives.

Migration evidence SHOULD preserve:

- every source alternative in original order;
- each `href` and optional `name`;
- resolution success/failure;
- which alternative was selected, or whether embedded `check-content` was
  used;
- a digest/identity for the selected source content.

For reproducibility, converters SHOULD resolve references from a closed,
pinned input set such as a SCAP data stream/package. Mutable network retrieval
SHOULD NOT silently participate in a reproducible migration build; if external
retrieval is explicitly allowed, the retrieved artifact SHOULD be captured and
pinned by digest in migration evidence.

This fallback behavior is a migration/build concern, not a native SCAP-NG
authoring or execution feature.

### XCCDF cluster-id expansion

XCCDF `cluster-id` is a Profile-authoring indirection used to address multiple
related Rules/Groups or Values. SCAP-NG SHALL normalize this mechanism away
during Stage-1 migration rather than introduce a native runtime cluster object.

Before applying Profile semantics, a converter SHALL construct the effective
legacy cluster membership from source items and expand each Profile operation
whose `idref` targets a cluster into equivalent explicit operations on the
cluster's members.

Expansion SHALL preserve:

- the original Profile operation's position relative to surrounding operations;
- member source identity and source document order;
- operation type and attributes (`select`, `refine-rule`, `set-value`,
  `set-complex-value`, or `refine-value`);
- source cluster identity in migration provenance.

The converter SHALL apply the XCCDF type restrictions of the source operation.
Rule/Group operations SHALL NOT accidentally target Value members, and
Value-oriented operations SHALL NOT target Rules/Groups.

After deterministic expansion, ordinary Profile inheritance/override/effective
selection logic applies to the explicit member operations. A later explicit
operation on one member therefore retains the same precedence it had in the
legacy Profile.

A cluster reference with no compatible members SHALL be a migration diagnostic
and SHOULD fail Stage-1 conversion when it affects effective policy. If an
`idref` is ambiguous between a direct item identity and a cluster identity and
the legacy semantics cannot be proven unambiguously, the converter SHALL fail
closed rather than choose one interpretation.

Native Benchmark/Profile/Tailoring content need not retain `cluster-id`.
Complete migration evidence SHOULD retain the source cluster-to-member
crosswalk so reviewers can reconstruct why explicit NG operations were emitted.

### XCCDF item/Profile inheritance, abstract templates, and hidden presentation

XCCDF 1.2 requires inheritance to be resolved during Loading before Benchmark
traversal. Stage-1 SCAP-NG migration SHALL likewise flatten supported
`extends` relationships into effective content before emitting native objects.
Native Benchmark/Rule/Assessment/Parameter execution SHALL NOT require a
runtime XCCDF inheritance engine.

For supported Rule, Value, and Profile inheritance, the converter SHALL apply
the XCCDF 1.2 property processing models rather than a generic object merge:

- **None:** `abstract`, `cluster-id`, `extends`, `id`, `signature`,
  `status`, and `dc-status` are not inherited.
- **Prepend:** `source` and `choices`.
- **Append:** `requires`, `conflicts`, `ident`, `fix`, `value`,
  `complex-value`, `default`, `complex-default`, `lower-bound`,
  `upper-bound`, `match`, `select`, `refine-value`, `refine-rule`,
  `set-value`, `set-complex-value`, and `profile-note`.
- **Replace:** `hidden`, `prohibitChanges`, `selected`, `version`,
  `weight`, `operator`, `interfaceHint`, `check`, `complex-check`,
  `role`, `severity`, `type`, `interactive`, `multiple`, `note-tag`,
  and `impact-metric`. XCCDF's distinct-system/distinct-selector rule for
  `check` remains part of effective-property identity.
- **Override:** `title`, `description`, `platform`, `question`,
  `rationale`, `warning`, `reference`, and `fixtext`; explicit
  `override=true` replaces the corresponding inherited property, otherwise
  the property appends. Locale-distinct values remain distinct where XCCDF
  defines `xml:lang` identity.

The converter SHALL recursively resolve the extended object first, SHALL reject
missing or wrong-type `extends` targets, and SHALL reject inheritance cycles.
After resolution, the emitted native object SHALL contain its complete effective
semantics and SHALL NOT retain `extends` merely as an execution dependency.
Migration evidence SHOULD preserve the inheritance chain and the origin of each
effective property.

An XCCDF item or Profile with effective `abstract=true` is a template and is
removed after inheritance resolution. It SHALL NOT become an independently
executable/selectable native SCAP-NG object. Its contributed effective
properties remain present in concrete descendants, with source provenance.

XCCDF `hidden` affects generated-document presentation only; the XCCDF
specification explicitly permits hidden items to participate in assessment.
SCAP-NG therefore SHALL NOT give `hidden` execution semantics. Stage-1
migration MAY retain source `hidden` state in migration/presentation metadata,
but scanners SHALL NOT use it to select, skip, score, or otherwise alter
Assessment truth. A future document-generation profile MAY define native
presentation metadata independently of scanner execution.

**Deprecated XCCDF Group extension is an explicit migration blocker by default.**
XCCDF 1.2 requires fresh unique identifiers for descendant Group/Rule/Value
objects created through Group extension but states that no standardized ID
generation procedure exists and warns that vendor behavior is therefore
non-interoperable. A Stage-1 converter SHALL NOT invent random or
implementation-specific native identities and claim lossless equivalence. Such
content SHALL be quarantined for source cleanup or handled only by a separately
declared compatibility procedure that records its identity mapping completely.

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

<!-- spec-nav:start -->

---

**Specification navigation:** [← Previous: Results and Evidence](../results/results.md) · [Contents](../README.md) · [Next: OVAL 5.12.3 to SCAP-NG Migration →](oval-5.12.3-to-ng.md)

<!-- spec-nav:end -->
