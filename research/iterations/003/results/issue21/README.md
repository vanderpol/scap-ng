# Issue #21 result projection fixtures

This directory contains a small canonical SCAP-NG result package slice, its
deterministic JSONL/SIEM projection, and matched SCAP 1.4 ARF comparison
fixtures.

Files:

- `scan-result.json` — run-level canonical result index.
- `benchmark-result.json` — policy-facing Benchmark/Rule result with selected
  Assessment identity/version, effective check selector, weight, applicability,
  policy outcome/reason, evidence references, and instance reference. Detailed
  expected/observed State, bounded-evidence, and input-execution data remain in
  the referenced Assessment Result.
- `expected.jsonl` — deterministic derived projection produced by
  `tools/project_results_jsonl.py`.
- `matched-scap14.arf.xml` — minimal matched XCCDF-only ARF result for the
  same target/Rule outcome.
- `matched-scap14-detailed.arf.xml` — self-contained matched detailed ARF with
  XCCDF, source OVAL Definition/Test/Object/State, OVAL Results, and OVAL System
  Characteristics.
- `size-comparison.md` — raw-byte comparison, scope, and limitations.

The projection intentionally contains one `scan_summary` event followed by one
independently useful `rule_result` event. Detailed Assessment execution graphs
remain referenced through `assessment_result_ref` rather than being copied in
full into each SIEM event.

The regression suite:

- compares generated JSONL byte-for-byte with `expected.jsonl` on Linux and
  Windows;
- validates the canonical scan/Benchmark result fixtures against the versioned
  SCAP-NG JSON Schemas using an offline schema registry;
- validates the ARF container against the vendored SCAP 1.4 ARF/XCCDF schemas;
- separately validates the nested OVAL Results/System Characteristics/source
  Definitions with the vendored OVAL 5.12.3 schemas;
- checks that the deterministic Rule message is consistent with the referenced
  authoritative detailed Assessment result;
- covers non-Boolean Rule outcomes while bounded-evidence/early-stop detail stays
  at Assessment-result scope.

## Size comparison interpretation

The minimal XCCDF-only ARF is intentionally retained even though the
self-contained JSONL Rule event is larger for this one-Rule case. It shows the
cost of denormalized SIEM context honestly.

The detailed comparison uses the self-contained ARF so both formats carry the
expected and observed configuration needed to interpret the failure. See
`size-comparison.md` for current byte counts.

These are controlled fixture measurements, not universal compression claims.
Rule count, evidence volume, repeated context, signing/manifest data,
serialization, and compression can materially change the ratio.
