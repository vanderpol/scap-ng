# Prototype Comparison Criteria

Iteration 001 implements the same assessment concepts using two candidate source organizations and complete file-oriented benchmark prototypes.

## Candidate A — Combined rule with optional shared-rule overlays

A normal combined rule keeps policy text, Check Content, applicability, and automation in one object.

The Windows prototypes additionally demonstrate a reuse mechanism:

- reusable combined rule base;
- STIG-specific overlay;
- build-time resolution into one complete rule.

The overlay can specialize policy identity/wording and approved parameter values, but cannot silently rewrite the shared assessment logic.

## Candidate B — Split policy / assessment / binding

Policy rules, assessment definitions, and mappings are separate authored objects. The Windows prototype has a shared assessment library used by two distinct STIG-like policies.

## Controlled prototype set

Both candidates contain equivalent seven-rule Windows Client, Windows Server, and Linux benchmarks, each with policy-only and automated distributions plus complete result examples.

The set covers native conditional logic, nested OVAL-style AND/OR logic, exact and parameterized cross-STIG reuse, applicability, collection errors, manual assessment, large filesystem populations, evidence caps, early termination, effective configuration parsing, and typed comparisons.

## Cross-STIG reuse experiment

Five Windows technical concepts appear in both Windows Client and Windows Server:

1. password policy by role — parameterized reuse;
2. platform-security nested Boolean logic — exact reuse;
3. Defender real-time status — exact reuse despite different policy wording;
4. Remote Registry service state — exact reuse despite different titles;
5. TrustedPublisher certificate state — exact reuse.

In the split model, those five assessment definitions exist once and each policy has its own binding.

In the combined model, those five **shared combined rules** exist once and each STIG supplies an overlay. The build resolves each overlay into a complete scanner-facing rule and verifies its policy fields against the policy-only source.

This gives us a much fairer comparison than simply duplicating combined rules.

## Architectural tension to evaluate

The combined overlay mechanism preserves a rule-centric authoring experience and can provide cross-STIG reuse, but it introduces inheritance/overlay semantics.

The split model uses explicit composition: policy + assessment + binding.

The key review question is therefore not merely "can both reuse automation?" They can. The more useful question is which abstraction is easier to author, validate, explain, version, migrate from SCAP 1.4, and implement consistently.

## Questions to answer after review

| Area | Combined rule + overlays | Split policy/assessment/binding | Evidence / notes |
|---|---|---|---|
| Understand one resolved rule | TBD | TBD | |
| Understand source dependencies | TBD | TBD | |
| DISA policy-only authoring burden | TBD | TBD | |
| Add automation without repeating policy | TBD | TBD | |
| Reuse automation across separate STIGs | TBD | TBD | |
| Parameterize shared automation safely | TBD | TBD | |
| Prevent STIG overlay from changing assessment semantics | TBD | TBD | |
| Preserve independent policy identities/references | TBD | TBD | |
| Avoid duplicated policy metadata | TBD | TBD | |
| Avoid duplicated assessment logic | TBD | TBD | |
| Maintain provenance/version lineage | TBD | TBD | |
| Avoid dangling references | TBD | TBD | |
| Review changes in Git | TBD | TBD | |
| Convert XCCDF + OVAL faithfully | TBD | TBD | |
| Render a complete resolved rule view | TBD | TBD | |
| Scanner package indexing complexity | TBD | TBD | |
| Build/validation complexity | TBD | TBD | |
| Support policy-only manual scans | TBD | TBD | |
| Package/signing clarity | TBD | TBD | |
| Long-term version management | TBD | TBD | |

No architecture decision should be made solely because one representation is shorter or has fewer files.
