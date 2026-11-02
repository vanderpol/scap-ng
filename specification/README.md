# Specification — SCAP-NG 0.4 (pre-alpha)

The [0.4 schema and metadata](../schema/README.md) are the current **machine-readable structural contract**. The human-readable normative specification is still being reconciled against the owner-approved 0.4 decisions.

Start with the [examples](../examples/README.md) and [generated reference](../docs/generated/schema-reference.md). These illustrate syntax; they do not introduce additional language requirements.

## Core terms

- **Benchmark:** a collection of policy Rules and Profiles.
- **Rule:** a policy requirement, separate from its implementation.
- **Assessment:** reusable instructions for checking a requirement.
- **Test:** a capability-specific check within an Assessment.
- **Object:** describes what system data to collect.
- **require:** defines how collected Items and fields must satisfy the check.
- **Result:** records what was evaluated and the outcome, with supporting evidence.

**Important distinction:** schema validity alone does not prove semantic correctness, scanner implementation, data collection or target compliance.

The next specification pass will document evaluation and missing-data semantics, applicability and result rollups, case sensitivity, Inputs, manual and shared Assessments, and packaging. Older 0.3 research and future 0.5 proposals must not silently become 0.4 requirements. Unresolved semantics require explicit review, not guesses.
