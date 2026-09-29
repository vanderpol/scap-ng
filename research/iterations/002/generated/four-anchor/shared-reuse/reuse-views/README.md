# Exact assessment reuse rendered three ways

Generated only from cross-benchmark groups whose complete normalized OVAL semantics are equivalent.

The same measured reuse groups are represented as:

- combined-rule: one shared technical rule base plus policy overlays;
- split policy/assessment/binding: one shared assessment plus explicit bindings;
- Ansible-inspired: one shared Ansible-like assessment plus explicit bindings/vars surface.

Parameterization candidates are intentionally excluded until reviewed.

## Summary

- Exact cross-benchmark reuse groups: **6**
- Assessment instances in those groups: **12**
- Shared assessments required: **6**
- Duplicate assessment definitions avoided: **6**
- Definition reduction within exact-reuse groups: **50.0%**

See reuse-view-manifest.json for per-group source-size and mapping metrics.
