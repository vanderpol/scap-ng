# Iteration 001 Full-Benchmark Prototypes

These are the primary iteration 001 architecture prototypes. Each model/platform pair contains a seven-rule benchmark rather than isolated rule fragments.

Each pair includes:

- human-readable authoring source;
- a policy-only benchmark source;
- automation source where applicable;
- complete policy-only manual scan results;
- complete automated/mixed-method scan results;
- two actual `.scapng` ZIP-compatible bundles (policy-only and resolved automated);
- sidecar manifest/signature files for review.

The `.scapng` archives themselves contain the proposed redistributable directory structure: benchmark/profile documents, individual policy/rule documents, assessment/binding documents where applicable, provenance, a member-hash manifest, and a prototype digital signature.

All content is illustrative. It is not an official DISA baseline.
