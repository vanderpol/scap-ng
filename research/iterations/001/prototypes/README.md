# Iteration 001 Prototypes

These prototypes compare two content organizations while holding policy intent and result semantics constant.

- `combined-rule/` — policy and automation in the same rule object.
- `split-policy-assessment-binding/` — policy, reusable assessment, and binding are separate objects.

The syntax is illustrative. It is designed to expose architectural strengths and weaknesses, not to freeze field names or schema details.

## Scenarios

### Windows 1 — Conditional effective policy

Exercises native `if / elif / else`, branch explanation, native semantic collection, and compact failed-comparison output.

### Windows 2 — Nested Boolean security posture

Exercises an OVAL-like binary AND/OR criteria tree and compact minimal-root-cause reporting.

### Linux 1 — Large filesystem ownership

Exercises a potentially huge object population, evidence limits, early termination, lower-bound violation counts, and collection/diagnostic completeness.

### Policy-only examples

Windows and Linux policy-only rules demonstrate what a DISA-style publisher could create without automation. Existing Check Content is used directly as the default manual procedure.

## Important

All IDs, policy wording, observed values, and expected values are illustrative research data. These examples are not official DISA STIG rules.
