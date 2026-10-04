<!-- scap-ng-discussion-id: CANONICAL-JSON-AUTHORING-RESEARCH -->

# Canonical execution representation research

**Status:** historical research note; **not** a current voting question.

This note predates the current Benchmark → Rule → Assessment architecture. The current design has **no separate Policy object**.

## Current question

Can multiple human-friendly authoring presentations compile to one versioned resolved SCAP-NG execution representation without changing assessment or policy semantics?

That question is now represented by **P053 — Canonical execution representation**. P053 does not approve Ansible as a runtime or restore a Policy object.

## Required safeguard

Successful compilation, schema validation, or self-round-trip is not enough. Any alternate authoring language must demonstrate independently that equivalent author intent produces equivalent execution and results, with traceability from source to compiled node to result evidence.

## Current direction

- Keep the core native language and execution semantics authoritative.
- Treat alternate authoring presentations as optional compiler front ends.
- Fail closed on unsupported or ambiguous constructs.
- Do not assume arbitrary Ansible modules, shell execution, or command-capable syntax is safe or equivalent.
- Use independently reviewed examples and expected outcomes before admitting another authoring form.

See [P053](../proposals/P053.md) for the current Board proposal and [SCAP 1.4 → SCAP-NG key changes](../SCAP-1.4-TO-SCAP-NG-KEY-CHANGES.md) for the current architecture summary.
