# Full pinned NIWC Current native normalization/compiler experiment

All native input in this run was generated fresh from the pinned NIWC SCAP 1.4 Current ZIPs.
No iteration-001/002 or pre-existing generated SCAP-NG tree was used as input.

## Generation
- Pinned NIWC revision: 8c8e5dff860af6b1290ee9273a282db24278f8d5
- Source packages accounted for: **65**
- Native Benchmarks generated: **46**
- Source/conversion blockers: **19**

## Exact normalization
- Referenced Assessment definitions before: **11019**
- Definitions after proven exact normalization: **7699**
- Duplicate definitions avoided: **3320**
- Definition reduction: **30.13%**

## Manual-review candidates
- Near-duplicate Assessment groups: **55**
- Near-duplicate Rule candidates reported: **22778**

## Compiler experiment
- Unsigned bundles before: **46** / 15096477 bytes
- Unsigned bundles after: **46** / 16832674 bytes
- Aggregate standalone-bundle change: **-1736197 bytes (-11.5%)**
- Self-signed CMS experimental bundles: **46**
- Signature trust: self-signed-experimental-no-publisher-trust

Standalone benchmark bundles remain self-contained, so cross-benchmark repository sharing does not necessarily reduce total independently distributed bundle size.
Repository-definition reduction is the primary normalization metric.
