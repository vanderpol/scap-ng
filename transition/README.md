# Current SCAP-NG handoff status

SCAP-NG 0.2.0 is technically frozen for bounded content/conformance review at schema baseline `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

## Current state

- The six-case converter-produced OVAL Board pilot has been delivered under [`board/review-content/0.2.0/`](../board/review-content/0.2.0/).
- Human review of those examples is the immediate gate before broad content expansion.
- Schema development remains frozen unless a focused reproducer demonstrates a genuine defect or accepted Board/human review requires a change.
- Content/conformance work remains ahead of editor development.
- ESX/VMware expansion and the two Kubernetes OVAL 6-only tests remain deferred pending the recorded guidance/decisions.

## Read first when resuming work

1. [Current design](../research/iterations/003/design/CURRENT-DESIGN.md)
2. [0.2.0 freeze record](0.2.0-freeze-record-2026-10-04.md)
3. [Maintenance process](../MAINTAINING.md)
4. [Branch registry](../BRANCH-MANAGEMENT.md)
5. [OVAL Board packet](../board/README.md)
6. [Human-runnable tooling](../tools/HUMAN-RUNNABLE-SCRIPTS.md)

## Validation boundary

All required 0.2.0 technical freeze gates passed, including Windows/Linux current-design regression, Self-Assertion, smoke/preservation, fast-five integration, and the intentional full NIWC deliverable run.

Those gates do not establish exhaustive human semantic review, complete collector coverage, independent scanner equivalence, or Board ratification.

## ChatGPT / Codex continuity

GitHub is the durable project record. Before switching interfaces, commit or otherwise record current decisions, implementation state, validation evidence, blockers, and the next bounded task.

Use ChatGPT primarily for architecture/standards/semantic reasoning and Codex primarily for bounded repository implementation once intended behavior is defined. Only one interface/session should own an overlapping workstream at a time.

Historical transition records remain in this directory for evidence. They are dated snapshots and SHALL NOT override the current design, freeze record, or later explicit owner decisions.
