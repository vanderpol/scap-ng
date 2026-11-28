# Unsigned Result package fixture

Two targets invoke the existing ordered Assessment with absent Inputs and
record its documented fallback. The package ties each Rule to a
target-scoped execution ID and retains the distinction between an invoked
Assessment with a technical outcome and a Rule disabled by policy. Exact
member bytes, paths, sizes and SHA-256 digests are carried in the manifest.

The local tests validate the document shapes and exercise the manifest links,
fallback trace, scope, summaries and byte integrity against independent
expectations. The input binding and retention negatives exercise existing
schema rules. The fixture omits scoring and signature qualification. A
consumer Result-package verifier and a scanner-generated receipt remain open.

## Qualification

The Studio metadata pack at the canonical schema pin admitted the
manifest and all five native Result documents. This checked schema
admission through Studio's validator. At RI revision
`f39ac725b820353e6f6b8fc71af673c08857d895`, six focused existing Result
tests passed for redaction, traces, dependency provenance and Benchmark
CPE identity. They use RI unit fixtures. Full guard traces, external
package verification and scanner-emitted Results await a canonical
replay receipt. [RI #196](https://github.com/vanderpol/scap-ng-ri/issues/196)
and [Evidence #3](https://github.com/vanderpol/scap-ng-evidence/issues/3).
