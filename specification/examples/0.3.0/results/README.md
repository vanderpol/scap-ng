# SCAP-NG 0.3 result examples

These small synthetic examples demonstrate the current 0.3 result schemas. They
are designed for human review and schema/conformance testing; they are not claims
about a live target scan.

- [Scan Result](scan-result.json) — run/target index and references to normalized
  Benchmark and Assessment Results.
- [Benchmark Result](benchmark-result.json) — policy-facing counters and
  **embedded Rule Results**. Its automated Rule contains a typed owner-UID
  comparison; the manual Rule has an explanatory message and Assessment
  reference without fabricating collected Items.
- [Organizational Input Benchmark Result](benchmark-result-organizational-input.json) — **synthetic**, with one authoritative approved value/provenance record and concise Rule-level value and reference.
- [Matching Organizational Input Assessment Result](assessment-result-organizational-input.json) — **synthetic**, records the exact consumed State input and stable provenance reference without copying supplier/authorizer details.
- [Assessment Result](assessment-result.json) — one Test with its collected file attributes, expected-versus-observed owner comparison, and provenance together.
- [Passing, routine Items omitted](assessment-result-pass-omitted.json) — **synthetic** complete evaluation of 10,000 file-owner comparisons, zero failures and zero retained system Items; no evidence truncation.
- [Passing, decisive positive witness](assessment-result-pass-witness.json) — **synthetic** required file observed with UID 0, retaining its typed Item and comparison as useful proof of success.
- [Multi-file Assessment Result](assessment-result-multi-file.json) — three files/directories, each reported beside its Test outcome with typed system attributes and comparisons.
- [Bounded-evidence Assessment Result](assessment-result-bounded-evidence.json) — 20 observed failures, two retained Item details, incomplete population.
- [Diagnostic override Assessment Result](assessment-result-diagnostic-override.json) — the **same Assessment content**, with a scanner-requested 50-Item limit and 20 Items retained; the technical outcome is unchanged.
- [Manual Assessment Result](manual-assessment-result.json) — human technical
  determination with assessor identity, time, comments, and evidence references.

All retained per-Item comparison results refer to the **Test-local predicate position** (for example, `file-owner-is-root.states[0]`), not a separately authored State ID. These lexical references remain stable within the immutable packaged Assessment. Original OVAL State IDs and comments, where applicable, remain in migration provenance rather than ordinary executable content or result references.

The examples use `result_schema_version: 0.3.0`. They should be regenerated or
revalidated at each 0.3 prerelease checkpoint as required by the repository
release process.

These fixtures are intentionally small. The full vendor-facing feature/expected
result corpus is tracked in
[#128](https://github.com/vanderpol/scap-ng/issues/128).

These examples show **SCAP-NG's difference from OVAL Results/System Characteristics**: a Test's technical outcome and reported system Items are adjacent, instead of separated into cross-referenced sections. The scanner can retain bounded Items for routine scans and more detailed evidence for authorized debugging without changing Benchmark or Assessment content. Neither cap authorizes a change to the check's truth, redaction or resource-safety behavior.

The passing examples distinguish **deliberate omission of routine successful Items**
from a reporting cap and show that a successful check may still need a positive
witness. Both are manually constructed normative-behavior illustrations checked
against the current JSON Schema and result-accounting validator; neither is
proof that a vendor scanner collected or reported these observations.
