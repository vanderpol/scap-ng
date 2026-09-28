# RHEL 9 full SCAP 1.4 -> SCAP-NG conversion evidence

Generated from the pinned published NIWC RHEL 9 SCAP 1.4 benchmark.

This directory intentionally commits compact, reviewable evidence rather than
duplicating the complete generated 445-rule source tree in Git. The workflow
artifact contains the full converted output for both candidate source layouts.

The generic automated assessments are currently marked `legacy_compatible`:
OVAL XML has been lowered to a structured SCAP-NG assessment graph, but native
collector/capability mappings have not all been independently promoted to
`exact_native` / `exact_normalized`.

The simple and complex sample directories show the same source rule rendered
as combined-rule and split policy/assessment/binding layouts.
