# Findings from Published NIWC SCAP 1.4 Migration Work

**Iteration:** 001  
**Status:** Evidence reset / findings pending  
**Authoritative source:** pinned NIWC Atlantic `scap-content-library/Current`

Earlier experimental migration examples sourced from development repositories were removed from the evidence corpus. Their implementation experience may inform hypotheses, but they are not treated as published-content proof.

## Priority evidence set

The first depth pass uses four published benchmarks:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

The complete pre-specification gate remains every individual published benchmark in the pinned NIWC `Current/` tree.

## Questions to answer with published evidence

1. Which OVAL constructs appear in the four priority benchmarks?
2. Which constructs are hardest to map into the current collect/derive/assert model?
3. How much RHEL 9 / Oracle Linux 9 automation is exactly reusable versus parameterizable versus merely similar?
4. How much Windows 11 / Server 2025 automation is reusable across distinct policy identities?
5. Which semantic capabilities recur often enough to justify standardization?
6. Which OVAL set/filter/local-variable constructs truly require first-class equivalents?
7. Which cases require explicit applicability, cardinality, completeness, or error semantics?
8. Can both candidate YAML authoring forms render the same semantic IR without loss?
9. Do both compile back to the same canonical semantic digest?
10. Can differential execution reproduce SCAP 1.4 applicability/outcomes/errors?

Findings will be added here only after they are reproduced from the pinned published packages.
