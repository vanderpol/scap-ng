# Findings from Published NIWC SCAP 1.4 Migration Work

**Iteration:** 001  
**Status:** Active published-content findings  
**Authoritative source:** pinned NIWC Atlantic `scap-content-library/Current`

Earlier experimental migration examples sourced from development repositories were removed from the evidence corpus. Findings below are reproduced from pinned published NIWC content.

## Priority evidence set

The first depth pass uses:

- RHEL 9
- Oracle Linux 9
- Windows 11
- Windows Server 2025

The complete pre-specification gate remains every individual published benchmark in the pinned NIWC `Current/` tree.

## Finding 1 — rule-level splitting works across the four anchors

The splitter generated standalone OVAL Definitions documents for every XCCDF rule with an OVAL definition reference:

| Benchmark | XCCDF rules | Rules with OVAL | Standalone OVAL splits |
|---|---:|---:|---:|
| RHEL 9 | 445 | 418 | 418 |
| Oracle Linux 9 | 448 | 408 | 408 |
| Windows 11 | 257 | 246 | 246 |
| Windows Server 2025 | 291 | 261 | 261 |
| **Total** | **1,441** | **1,333** | **1,333** |

Every one of the 1,333 split files validates against the vendored SCAP 1.4 `omni-schema.xsd`. The splitter reported zero unresolved OVAL references and zero ambiguous definition references.

The closure is a fixed point over definitions, tests, objects, states, and variables. Typed dependency edges explicitly account for `extend_definition`, test/object/state/variable references, object sets, and filters.

## Finding 2 — variables materially expand rule closure

Variables occur in 104 of the 1,333 automated rule splits.

Across the per-rule closures:

- 78 variable instances can currently be evaluated as exact static values;
- 59 are object-dependent;
- 34 use functions not yet implemented by the static evaluator.

The priority corpus exercises variable/function constructs including:

- `object_component`
- `variable_component`
- `literal_component`
- `concat`
- `arithmetic`
- `count`
- `merge`
- `regex_capture`
- `split`
- `substring`
- `unique`

The largest current flagship rule contains 17 variables and 64 `variable_component` references.

**Finding:** variable closure is not an implementation detail. OVAL variables must be first-class nodes in the faithful semantic IR, and object-dependent variables can recursively pull additional objects into scope.

## Finding 3 — the RHEL 9 xattr audit rule exposes both complexity and a source anomaly

Published RHEL 9 rule `SV-258179` expands to:

- 7 definitions;
- 24 tests;
- 24 objects;
- 17 variables;
- 39,135 bytes as a standalone split OVAL document.

Its variables construct regular expressions used to inspect `/etc/audit/audit.rules`.

The converter can resolve all 17 variables exactly and recognize the source as syscall/architecture/AUID audit-rule conditions.

However, the 24 tests contain only **22 unique semantic conditions**:

- `lsetxattr | b32 | root` appears twice;
- `removexattr | b32 | root` appears twice;
- `lsetxattr | b64 | root` is absent;
- `removexattr | b64 | root` is absent.

The generated native normalization therefore preserves the 22 conditions actually enforced by the OVAL and marks the conversion `requires_review`. It does **not** silently create the two apparently missing b64/root conditions.

This is direct published-content evidence for the requirement that migration preserve source behavior before reviewed correction or simplification.

## Finding 4 — the same anomaly and semantics are reused by Oracle Linux 9

Published Oracle Linux 9 rule `SV-271536` independently normalizes to the same 22-condition semantic model, including the same duplicated/missing cells.

The source-independent native semantic fingerprint for both rules is:

```text
0f34fddeace27334af90bf5bb9e3dc26fc1800847d86b5cde6a119f4329f9421
```

This is the first iteration 001 evidence from published content that two different STIG policy identities can map to the same reusable technical assessment semantics.

It also demonstrates a reuse risk: a shared assessment can propagate a shared source defect. Reuse therefore increases the importance of provenance, review status, and differential tests.

## Finding 5 — authoring familiarity does not automatically mean less syntax

For the faithful generated RHEL 9 normalization:

| Rendering | Lines | Characters |
|---|---:|---:|
| Original NG authoring candidate | 115 | 3,323 |
| Ansible-inspired candidate | 121 | 3,518 |

The Ansible-inspired form is about 5–6% larger in this complex example.

That does not decide the authoring syntax. Familiar vocabulary may still improve comprehension for Ansible authors. But it is useful evidence that the Ansible-inspired style should not be assumed to be simpler merely because it is familiar.

A separate 24-cell Cartesian-matrix rendering remains in the showcase as a **policy-review candidate**, not a faithful migration result, because it adds the two b64/root conditions absent from the published OVAL.

## Finding 6 — the IR-first architecture prevented silent semantic repair

Had the converter translated directly from the policy title into a convenient 6 × 2 × 2 matrix, it would have produced a cleaner assessment while silently changing source behavior.

The successful path is instead:

```text
published SCAP 1.4
      |
      v
faithful OVAL dependency/variable IR
      |
      v
source-semantic normalization
      |
      +--> faithful 22-condition NG representation
      |
      +--> review finding: apparent 24-condition policy matrix
```

This provides concrete evidence for the decision to separate faithful interpretation from reviewed native normalization.

## Next work

The semantic parser now has a finite OVAL 5.12.3 variable-function checklist driven by the vendored schema. The next implementation work is to explicitly model the remaining function semantics and then mine additional difficult published rules from all four priority benchmarks.

Differential execution remains required before any native normalization moves from `requires_review` to `exact_normalized`.
