# Windows 11 full SCAP 1.4 -> SCAP-NG conversion evidence

Generated from the pinned published NIWC Windows 11 SCAP 1.4 benchmark.

This directory intentionally commits compact, reviewable evidence rather than
duplicating the complete generated 257-rule source tree in Git. The workflow
artifact contains the full converted output for all three YAML renderings:
combined-rule, split policy/assessment/binding, and Ansible-inspired.

Supported automated assessments are currently marked `legacy_compatible`:
OVAL XML has been lowered to a structured SCAP-NG assessment graph, but native
collector/capability mappings have not all been independently promoted to
`exact_native` / `exact_normalized`.

The published benchmark contains one rule using deprecated Windows
`user_test`. That rule is preserved as an explicit source-remediation
blocker and is intentionally not included in an automated package. Policy-only
packages remain buildable; the package metrics record why automated packages
were withheld.

The simple and complex sample directories show the same source semantics
rendered as combined-rule, split policy/assessment/binding, and
Ansible-inspired YAML. The Ansible-inspired form is an authoring style only
and has no Ansible runtime dependency.
