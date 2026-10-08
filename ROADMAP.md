# SCAP-NG development roadmap

Updated: 2026-10-08.

SCAP-NG 0.3.0 is the active pre-alpha checkpoint. The 0.2.0 schema is
historical evidence, not a content-reproduction requirement.

## Current — validate, review, then publish 0.3

The six-benchmark review candidate has passed an earlier full authoring build.
The **active-0.3 full-corpus release gate is not yet green**: the previous run
found 25 Google Chrome Registry-type semantic failures after conversion;
the exact OVAL-to-native crosswalk fix is now in regression testing.
The [new 65-source run](https://github.com/vanderpol/scap-ng/actions/runs/37838382899)
is the relevant correctness checkpoint, not the earlier modernization census.

- Confirm the latest code's smoke/current-design and six-benchmark conversion,
  schema, semantic, normalization and compilation gates.
- Pass the active 0.3 full corpus: 61 supported packages, four explicit
  deprecated SQL-extension blockers, zero unexplained semantic errors.
- Review the complete current six-benchmark sample and result contracts,
  then publish a permanent SHA-256-identified GitHub prerelease asset
  **only after owner acceptance**.

No new feature design is required merely to make 0.3 larger. Correctness
repairs and explicitly accepted input/result contracts remain in scope.

Observation and evaluate redesign are deferred beyond 0.3; do not reopen them
during checkpoint stabilization unless an implementation blocker proves the
frozen requirements inconsistent.

## Next — prove independent implementation

- Expand conformance/known-result coverage.
- Build a minimal reference evaluator/scanner and perform differential execution.
- Validate acquisition/collector behavior separately from schema/converter proof.
- Measure packaging, memory use, concurrency, caching, offline behavior, and
  enterprise-scale performance.

## Later — release and standards path

- Stabilize deterministic packaging and signing/trust profiles.
- Complete implementation guidance and vendor-facing conformance material.
- Promote releases from immutable reviewed checkpoints.
- Carry accepted semantics and governance decisions into broader standards work.

The [core objectives](specification/objectives.md) define why changes belong in
SCAP-NG. [Objective-to-issue traceability](OBJECTIVES.md) maps active 0.3 work to
those goals.

[Current review](review/current/README.md) ·
[Open issues](https://github.com/vanderpol/scap-ng/issues) ·
[Specification](specification/README.md) ·
[Current design](research/iterations/003/design/CURRENT-DESIGN.md)
