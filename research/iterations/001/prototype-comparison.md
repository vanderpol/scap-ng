# Prototype Comparison Criteria

Iteration 001 intentionally implements the same assessment semantics using two candidate source organizations.

The comparison must be based on actual prototype experience rather than aesthetics.

## Candidate A — Combined rule

Policy text, manual procedure, applicability, and automation live in the same rule object.

## Candidate B — Split policy / assessment / binding

Policy, reusable assessment logic, and mapping are separate objects.

## Questions to answer after implementation

| Area | Combined rule | Split policy/assessment/binding | Evidence / notes |
|---|---|---|---|
| Understand one rule by opening one file | TBD | TBD | |
| DISA policy-only authoring burden | TBD | TBD | |
| Add automation without rewriting policy | TBD | TBD | |
| Reuse one assessment across many rules | TBD | TBD | |
| Reuse one policy concept across platforms | TBD | TBD | |
| Avoid duplicated policy metadata | TBD | TBD | |
| Avoid duplicated assessment logic | TBD | TBD | |
| Maintain independent policy/automation provenance | TBD | TBD | |
| Avoid dangling mappings/references | TBD | TBD | |
| Review changes in Git | TBD | TBD | |
| Convert XCCDF + OVAL faithfully | TBD | TBD | |
| Render a complete resolved rule view | TBD | TBD | |
| Scanner package indexing complexity | TBD | TBD | |
| Validation complexity | TBD | TBD | |
| Support policy-only manual scans | TBD | TBD | |
| Package/signing clarity | TBD | TBD | |
| Long-term version management | TBD | TBD | |

## Controlled prototype requirement

Both candidate architectures must represent identical policy intent and produce equivalent result semantics for the Windows conditional, Windows nested-logic, Linux large-filesystem, and policy-only examples.

If an architectural choice requires different result semantics, that difference must be documented as a design consequence rather than hidden in the prototype.

## Evaluation principle

No decision should be made solely because one representation is shorter.

The preferred architecture should minimize the total lifecycle burden across:

- policy publication;
- automation authoring;
- reuse;
- migration;
- validation;
- scanner ingestion;
- reporting;
- provenance;
- signing;
- maintenance across benchmark revisions.
