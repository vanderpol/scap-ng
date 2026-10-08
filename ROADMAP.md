# SCAP-NG development roadmap

Updated: 2026-10-07.

SCAP-NG 0.3.0 is the active pre-alpha development version. The 0.2.0 schema is
the frozen earlier review baseline.

## Current — owner review, then publish the 0.3 Board checkpoint

The frozen 0.3 requirement set is implemented and the six-benchmark owner-review
candidate is 6/6 schema/semantic green. The pinned 65-package checkpoint also
completed with only the four known explicit blockers.

- Complete owner review of the stable candidate and its modernization examples.
- Make only blocker/correctness fixes during review; do not add new 0.3 features.
- After owner acceptance, publish one immutable prerelease review package with
  SHA-256 and source/build provenance.

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
