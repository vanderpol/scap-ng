# SCAP-NG 0.3 result examples

These small synthetic examples demonstrate the current 0.3 result schemas. They
are designed for human review and schema/conformance testing; they are not claims
about a live target scan.

- [Scan Result](scan-result.json) — run/target index and references to normalized
  Benchmark and Assessment Results.
- [Benchmark Result](benchmark-result.json) — policy-facing counters, Rule
  outcomes, concise messages, reasons, applicability, and references to detailed
  Assessment Results.
- [Assessment Result](assessment-result.json) — one Test with its collected file attributes, expected-versus-observed owner comparison, and provenance together.
- [Multi-file Assessment Result](assessment-result-multi-file.json) — three files/directories, each reported beside its Test outcome with typed system attributes and comparisons.
- [Bounded-evidence Assessment Result](assessment-result-bounded-evidence.json) — 20 observed failures, two retained Item details, incomplete population.
- [Diagnostic override Assessment Result](assessment-result-diagnostic-override.json) — the **same Assessment content**, with a scanner-requested 50-Item limit and 20 Items retained; the technical outcome is unchanged.
- [Manual Assessment Result](manual-assessment-result.json) — human technical
  determination with assessor identity, time, comments, and evidence references.

The examples use `result_schema_version: 0.3.0`. They should be regenerated or
revalidated at each 0.3 prerelease checkpoint as required by the repository
release process.

These fixtures are intentionally small. The full vendor-facing feature/expected
result corpus is tracked in
[#128](https://github.com/vanderpol/scap-ng/issues/128).

These examples show **SCAP-NG's difference from OVAL Results/System Characteristics**: a Test's technical outcome and reported system Items are adjacent, instead of separated into cross-referenced sections. The scanner can retain bounded Items for routine scans and more detailed evidence for authorized debugging without changing Benchmark or Assessment content. Neither cap authorizes a change to the check's truth, redaction or resource-safety behavior.
