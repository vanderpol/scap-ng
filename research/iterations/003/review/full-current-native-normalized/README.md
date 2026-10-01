# Full pinned NIWC Current native normalization/compiler experiment

All native input in this run was generated fresh from the pinned NIWC SCAP 1.4 Current ZIPs.
No iteration-001/002 or pre-existing generated SCAP-NG tree was used as input.

## Generation
- Pinned NIWC revision: 8c8e5dff860af6b1290ee9273a282db24278f8d5
- Source packages accounted for: **65**
- Native Benchmarks generated: **65**
- Source/conversion blockers: **0**

## Exact normalization
- Referenced Assessment definitions before: **15873**
- Definitions after proven exact normalization: **10484**
- Duplicate definitions avoided: **5389**
- Definition reduction: **33.95%**

## Manual-review candidates
- Near-duplicate Assessment groups: **99**
- Near-duplicate Rule candidates reported: **45794**

## Compiler experiment
- Unsigned bundles before: **65** / 21768447 bytes
- Unsigned bundles after: **65** / 22320575 bytes
- Aggregate standalone-bundle change: **-552128 bytes (-2.54%)**
- Self-signed CMS experimental bundles: **65**
- Signature trust: self-signed-experimental-no-publisher-trust

Standalone benchmark bundles remain self-contained, so cross-benchmark repository sharing does not necessarily reduce total independently distributed bundle size.
Repository-definition reduction is the primary normalization metric.

## Review snapshot layout

This directory is a generated **iteration-003 review artifact**, not hand-authored
normative SCAP-NG source.

- `shared/assessments/` — canonical Assessments after exact semantic
  normalization across the complete pinned NIWC Current corpus.
- `conversion-output/logs/` — stdout/stderr captured from each SCAP 1.4 to
  native NG conversion invocation. These are retained so handled warnings,
  exclusions, and source-content problems can be reviewed.
- `conversion-output/status/` — per-package converter exit/status records.
- `conversion-output/source-generation/` — per-package structured generation
  summaries emitted by the conversion scripts.
- `evidence/normalizer-report.json` — exact-reuse groups, complete
  source/consumer lineage, near-duplicate review candidates, and reuse totals.
- `evidence/experiment-summary.json` — compact corpus-wide generation,
  normalization, and compile statistics.
- `evidence/compiler-before.json` and `compiler-after.json` — package metrics
  before and after repository normalization.
- `evidence/native-schema-census.json` — native construct census used for
  schema stabilization.

The shared Assessment files intentionally contain only native Assessment data.
Conversion and normalization provenance is kept in the adjacent evidence so a
reviewer can inspect lineage without making migration metadata part of the
native authoring model.
