# Iteration 001 Full-Benchmark Prototypes

These are the primary iteration 001 architecture prototypes. Each model/platform pair contains a seven-rule benchmark rather than isolated rule fragments.

Each pair includes:

- human-readable authoring source;
- a complete policy-only seven-rule benchmark definition;
- automation source where applicable;
- complete policy-only manual scan results;
- complete automated/mixed-method scan results;
- actual policy-only and resolved automated `.scapng` ZIP-compatible bundles;
- benchmark/profile, individual rule or policy objects, assessment/binding objects where applicable, provenance, a member-hash manifest, and a prototype digital signature inside each bundle.

All eight bundles are generated from the committed source by `research/iterations/001/tools/build_full_benchmarks.py` and verified by `tools/verify_scapng_prototype_bundle.py`. The GitHub Actions workflow `.github/workflows/build-scapng-iteration001.yml` rebuilds and verifies them so binary artifacts remain reproducible from source.

The same logical policy and automated outcomes are used in both architecture tracks so the comparison tests organization and lifecycle behavior rather than different security semantics.

## Committed bundles

- combined-rule / Windows policy-only
- combined-rule / Windows automated
- combined-rule / Linux policy-only
- combined-rule / Linux automated
- split-policy-assessment-binding / Windows policy-only
- split-policy-assessment-binding / Windows automated
- split-policy-assessment-binding / Linux policy-only
- split-policy-assessment-binding / Linux automated

All content is illustrative. It is not an official DISA baseline. The prototype signatures use a public RFC 8032 Ed25519 test key and demonstrate package integrity/signature mechanics only; they provide no publisher trust.
