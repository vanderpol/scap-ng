# Prototype Comparison Criteria

Iteration 001 implements the same policy intent and result semantics using two candidate source organizations.

The comparison must be based on actual full-benchmark prototype experience rather than aesthetics.

## Candidate A — Combined rule

Policy text, Check Content, applicability, and automation live in the same automated rule object.

## Candidate B — Split policy / assessment / binding

Policy, reusable assessment logic, and mapping are separate authored objects.

## Controlled prototype set

Both candidates now contain equivalent **seven-rule Windows and seven-rule Linux benchmarks**, including policy-only and automated distributions and complete scan-result examples.

The full benchmark set intentionally covers:

- conditional `if / elif / else`;
- nested OVAL-style AND/OR logic;
- multi-assertion rules;
- applicability and Not Applicable;
- collection Error;
- policy/manual assessment;
- large filesystem populations;
- evidence truncation and early termination;
- effective configuration parsing;
- typed version comparisons.

Both architectures compile into self-contained signed `.scapng` bundles. The result semantics are intentionally kept equivalent so organization can be compared independently from scanner reporting behavior.

## Questions to answer after review

| Area | Combined rule | Split policy/assessment/binding | Evidence / notes |
|---|---|---|---|
| Understand one rule by opening one source object | TBD | TBD | |
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

## Measured iteration 001 package observations

These measurements are descriptive only and are **not** an architecture score:

- combined-rule automated packages currently contain 12 ZIP members;
- split automated packages currently contain 19 ZIP members because assessments and bindings are independently addressable;
- policy-only packages contain 12 members in both candidate models;
- all current packages remain very small because this is a seven-rule research benchmark.

Package byte size should not determine the architecture. The significant comparison is lifecycle complexity across policy publication, automation authoring, reuse, migration, validation, scanner ingestion, reporting, provenance, signing, and maintenance.

## Evaluation principle

No architecture decision should be made solely because one representation is shorter or uses fewer files.

If a candidate requires different result semantics merely because source organization differs, that should be treated as an architectural warning rather than hidden in the prototype.
