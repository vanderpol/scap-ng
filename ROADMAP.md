# SCAP-NG roadmap

Updated: October 8, 2026. **0.3.0 is the active pre-alpha release checkpoint**;
0.2.0 is historical and does not require rebuilding as a 0.3 gate.

## Now — finish the 0.3 checkpoint

The [first full 65-source active-0.3 pipeline](https://github.com/vanderpol/scap-ng/actions/runs/37838382899)
**succeeded** on `799d083`: 61 supported generated benchmark packages, four
known nonstandard SQL-extension source blockers, schema and semantic checks,
graph checks, normalization, compilation and test signing.
The [follow-up run](https://github.com/vanderpol/scap-ng/actions/runs/37846666574)
covers subsequent Organizational Input and Result changes and must pass
independently. The [six-benchmark regression](https://github.com/vanderpol/scap-ng/actions/runs/37849528026)
and [current documentation audit](https://github.com/vanderpol/scap-ng/actions/runs/37849528014)
have passed at the later documentation checkpoint.

Finish the final full-corpus gate, reconcile any real correctness failures,
and obtain owner acceptance. Then publish a durable, checksum-identified
review/prerelease package; an expiring Actions ZIP is not the final release
asset. Keep the [release issue](https://github.com/vanderpol/scap-ng/issues/191)
as the single authoritative release checklist.

No new 0.3 feature design is required. Shared Observation and changes to
`evaluate` are deferred; see the
[scope boundary](specification/deferred-after-0.3.md).

## Next — independent implementation and conformance

Build and exercise a reference evaluator/scanner, compare actual vendor
execution against independently reviewed oracles, and test collected Item
semantics, redaction, evidence retention, signing, caching, offline operation
and enterprise-scale performance. Full automated Self-Assertion
generation/execution/comparison is targeted at 1.0
([#206](https://github.com/vanderpol/scap-ng/issues/206)).

## Later — governance and standards

Stabilize trust and packaging profiles, vendor-facing conformance material,
versioned releases, and the standards path.

[Core objectives](specification/objectives.md) ·
[Current review](review/current/README.md) ·
[Draft specification](specification/README.md) ·
[Issues](https://github.com/vanderpol/scap-ng/issues)
