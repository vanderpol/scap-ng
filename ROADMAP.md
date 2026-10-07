# SCAP-NG development roadmap

Updated: 2026-10-07.

SCAP-NG 0.3.0 is the active pre-alpha development version. The 0.2.0 schema is
the frozen earlier review baseline.

## Current — stabilize the 0.3 language

- Finish the bounded modernization research and human-review candidate set.
- Resolve terminology and authoring questions only where they make content
  meaningfully clearer or more interoperable.
- Promote accepted changes into the 0.3 schemas, specification, converter, and
  compiler together.
- Regenerate/revalidate source and result examples for the exact prerelease.
- Use focused tests and the fast integration set during development; use the full
  NIWC corpus only for intentional checkpoints.

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
