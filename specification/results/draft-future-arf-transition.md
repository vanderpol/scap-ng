# Future ARF transition and compatibility

**Status:** future design tracker; not part of the settled 0.2.0 result model.

## Why this exists

SCAP-NG intentionally does not reproduce NIST ARF as its canonical result model. In practice, ARF was rarely consumed directly by end users because complete ARF packages could become very large, while most user-facing workflows relied on XCCDF-oriented results.

However, some implementations have used ARF as a meaningful integration/output format. jOVAL/Arctic Wolf is a known example. Those implementations need a deliberate migration path rather than an assumption that ARF can simply disappear without compatibility impact.

## Current boundary

The current NG result model remains authoritative:

- compact Benchmark/Rule results;
- detailed linked Assessment results;
- explicit summary counters;
- structured messages/reasons;
- bounded evidence and completeness;
- normalized run/target/policy context;
- optional projections/exports for external consumers.

ARF compatibility SHALL NOT become a reason to duplicate the canonical NG result graph or reintroduce ARF-scale repetition into core results.

## Future work

An implementation that depends on ARF SHOULD propose the transition requirements based on real interoperability needs.

That proposal should answer:

1. Which ARF structures are actually consumed by existing products/integrations?
2. Which of those semantics are already represented natively in NG results?
3. Which ARF fields require a deterministic projection from NG?
4. Are any ARF semantics genuinely missing from NG rather than merely serialized differently?
5. Can a conforming ARF export be generated as a projection without changing NG assessment truth?
6. Which provenance, target, Benchmark, Rule, Assessment, and evidence references must be preserved?
7. How should bounded evidence and redaction map into ARF structures without falsely implying completeness?
8. Is round-trip fidelity required, or only one-way compatibility for downstream consumers?

## Preferred direction

The likely transition model is:

> canonical NG results → optional ARF compatibility projection

rather than:

> ARF semantics embedded back into canonical NG results.

This should remain a future Board/vendor interoperability discussion until a developer with an actual ARF dependency provides concrete requirements and examples.
