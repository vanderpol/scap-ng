# Full pinned NIWC Current native normalization/compiler experiment

All native input in this run was generated fresh from the pinned NIWC SCAP 1.4 Current ZIPs.
No iteration-001/002 or pre-existing generated SCAP-NG tree was used as input.

## Generation
- Pinned NIWC revision: 8c8e5dff860af6b1290ee9273a282db24278f8d5
- Source packages accounted for: **65**
- Native Benchmarks generated: **65**
- Source/conversion blockers: **0**

## Exact normalization
- Referenced Assessment definitions before: **16125**
- Definitions after proven exact normalization: **10633**
- Duplicate definitions avoided: **5492**
- Definition reduction: **34.06%**

## Manual-review candidates
- Near-duplicate Assessment groups: **99**
- Near-duplicate Rule candidates reported: **45794**

## Compiler experiment
- Unsigned bundles before: **65** / 21982728 bytes
- Unsigned bundles after: **65** / 22079541 bytes
- Aggregate standalone-bundle change: **-96813 bytes (-0.44%)**
- Self-signed CMS experimental bundles: **65**
- Signature trust: self-signed-experimental-no-publisher-trust

Standalone benchmark bundles remain self-contained, so cross-benchmark repository sharing does not necessarily reduce total independently distributed bundle size.
Repository-definition reduction is the primary normalization metric.
