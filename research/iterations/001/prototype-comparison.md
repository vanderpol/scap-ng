# Prototype Comparison Criteria

Iteration 001 implements the same assessment concepts using two candidate source organizations and complete file-oriented benchmark prototypes.

## Candidate A — Combined rule

Policy text, Check Content, applicability, and automation live in the same automated rule object. Policy-only rule files separately represent what a policy publisher would create.

## Candidate B — Split policy / assessment / binding

Policy rules, assessment definitions, and mappings are separate authored objects. The Windows prototype additionally has a shared assessment library used by **two distinct STIG-like policies**.

## Controlled prototype set

Both candidates contain equivalent seven-rule Windows Client, Windows Server, and Linux benchmarks, each with policy-only and automated distributions plus complete result examples.

The set covers native conditional logic, nested OVAL-style AND/OR logic, exact and parameterized cross-STIG assessment reuse, applicability, collection errors, manual assessment, large filesystem populations, evidence caps, early termination, effective configuration parsing, and typed comparisons.

## Cross-STIG reuse experiment

Five Windows assessment concepts appear in both Windows Client and Windows Server:

1. `demo.windows.password-policy-by-role` — parameterized reuse;
2. `demo.windows.platform-security-posture` — exact reuse;
3. `demo.windows.defender-realtime` — exact reuse despite different policy wording;
4. `demo.windows.remote-registry-disabled` — exact reuse despite different titles;
5. `demo.windows.trusted-publisher-store` — exact reuse.

In the split model those five definitions exist once and each policy has its own binding. In the combined model equivalent automation is repeated inline in each rule. This is intentional evidence for the architecture comparison.

## Questions to answer after review

| Area | Combined rule | Split policy/assessment/binding | Evidence / notes |
|---|---|---|---|
| Understand one rule by opening one source object | TBD | TBD | |
| DISA policy-only authoring burden | TBD | TBD | |
| Add automation without repeating policy | TBD | TBD | |
| Reuse one assessment across rules in one benchmark | TBD | TBD | |
| Reuse one assessment across separate STIGs | TBD | TBD | |
| Parameterize shared assessment logic safely | TBD | TBD | |
| Preserve independent policy identities/references | TBD | TBD | |
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

No architecture decision should be made solely because one representation is shorter or has fewer files. If reuse in the combined model requires a generalized reference/overlay mechanism, we should explicitly ask whether that mechanism is recreating the split model under another name.
