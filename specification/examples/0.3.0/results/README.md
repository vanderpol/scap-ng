# SCAP-NG 0.3 result examples

These small synthetic examples demonstrate the current 0.3 result schemas. They
are designed for human review and schema/conformance testing; they are not claims
about a live target scan.

- [Scan Result](scan-result.json) — run/target index and references to normalized
  Benchmark and Assessment Results.
- [Benchmark Result](benchmark-result.json) — policy-facing counters, Rule
  outcomes, concise messages, reasons, applicability, and references to detailed
  Assessment Results.
- [Assessment Result](assessment-result.json) — Test, State, entity comparison,
  collected Item, provenance, completeness, field use, and bounded evidence
  summary for one automated failure.
- [Bounded-evidence Assessment Result](assessment-result-bounded-evidence.json) —
  logically decisive result with an intentionally incomplete retained
  population and explicit evidence cap.
- [Manual Assessment Result](manual-assessment-result.json) — human technical
  determination with assessor identity, time, comments, and evidence references.

The examples use `result_schema_version: 0.3.0`. They should be regenerated or
revalidated at each 0.3 prerelease checkpoint as required by the repository
release process.

These fixtures are intentionally small. The full vendor-facing feature/expected
result corpus is tracked in
[#128](https://github.com/vanderpol/scap-ng/issues/128).
