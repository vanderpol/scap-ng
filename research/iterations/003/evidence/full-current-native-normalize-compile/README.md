# Full pinned NIWC Current native normalization/compiler experiment

All native input in this run was generated fresh from the pinned NIWC SCAP 1.4 Current ZIPs.
No iteration-001/002 or pre-existing generated SCAP-NG tree was used as input.

## Generation
- Pinned NIWC revision: 8c8e5dff860af6b1290ee9273a282db24278f8d5
- Source packages accounted for: **65**
- Native Benchmarks generated: **50**
- Source/conversion blockers: **15**

## Exact normalization
- Referenced Assessment definitions before: **12176**
- Definitions after proven exact normalization: **8279**
- Duplicate definitions avoided: **3897**
- Definition reduction: **32.01%**

## Manual-review candidates
- Near-duplicate Assessment groups: **84**
- Near-duplicate Rule candidates reported: **24791**

## Compiler experiment
- Unsigned bundles before: **50** / 16486324 bytes
- Unsigned bundles after: **50** / 16825541 bytes
- Aggregate standalone-bundle change: **-339217 bytes (-2.06%)**
- Self-signed CMS experimental bundles: **50**
- Signature trust: self-signed-experimental-no-publisher-trust

Standalone benchmark bundles remain self-contained, so cross-benchmark repository sharing does not necessarily reduce total independently distributed bundle size.
Repository-definition reduction is the primary normalization metric.
