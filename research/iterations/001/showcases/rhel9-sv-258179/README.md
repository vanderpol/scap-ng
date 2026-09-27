# RHEL 9 SV-258179 — Flagship Complexity Reduction Case

**Source:** published NIWC SCAP 1.4 content  
**Benchmark:** RHEL 9 V2R9 enhanced V13  
**Rule:** `xccdf_mil.disa.stig_rule_SV-258179r1155601_rule`  
**OVAL definition:** `oval:mil.disa.stig.rhel9os:def:258179`

This case is the flagship demonstration for both OVAL complexity reduction and conservative migration.

## Published OVAL closure

The standalone rule split contains:

| Construct | Count |
|---|---:|
| Definitions | 7 |
| Tests | 24 |
| Objects | 24 |
| States | 0 |
| Variables | 17 |
| Local variables | 8 |
| Constant variables | 9 |
| `variable_component` references | 64 |
| `concat` operations | 8 |
| Standalone OVAL bytes | 39,135 |

All 17 variables resolve statically in this case.

## Important source finding

The policy wording strongly suggests a 6-syscall × 2-architecture × 2-subject matrix, but the published OVAL does **not** implement a complete 24-cell matrix.

The 24 tests contain 22 unique conditions:

- `lsetxattr | b32 | root` is duplicated;
- `removexattr | b32 | root` is duplicated;
- `lsetxattr | b64 | root` is absent;
- `removexattr | b64 | root` is absent.

The duplicate pairs use byte-identical regular-expression conditions.

This is therefore both a complexity example and a migration-correctness test.

## Faithful generated conversion

The automated pipeline resolves the OVAL variables, interprets the 24 tests, collapses only Boolean-idempotent duplicate conditions, and emits the **22 unique conditions actually enforced**.

Generated artifacts:

- `../../generated/native-normalizations/rhel9-sv-258179/native-semantic.json`
- `../../generated/native-normalizations/rhel9-sv-258179/original-ng.yaml`
- `../../generated/native-normalizations/rhel9-sv-258179/ansible-inspired.yaml`

The migration status remains `requires_review` until differential execution proves equivalence.

The faithful generated authoring comparison is:

| Rendering | Lines | Characters |
|---|---:|---:|
| Original NG | 115 | 3,323 |
| Ansible-inspired | 121 | 3,518 |

Both are renderings of the same source-semantic object.

## Policy-review candidate

The files in this showcase named `review-candidate-*.yaml` intentionally show what the assessment could look like **if policy review confirms that the two missing b64/root conditions were intended**.

They are not faithful source conversions.

The review candidate can use a compact Cartesian matrix and is therefore much shorter:

| Rendering | Lines | Characters |
|---|---:|---:|
| Original NG review candidate | 71 | 1,756 |
| Ansible-inspired review candidate | 77 | 2,025 |

This separation is deliberate:

```text
published OVAL
     |
     v
faithful IR
     |
     +--> faithful 22-condition NG
     |
     +--> review finding
              |
              +--> possible 24-cell corrected matrix
```

SCAP-NG conversion must never jump directly to the corrected-looking matrix.

## Cross-STIG reuse result

Oracle Linux 9 `SV-271536` contains the same source semantics and the same anomaly.

Both normalize to semantic fingerprint:

```text
0f34fddeace27334af90bf5bb9e3dc26fc1800847d86b5cde6a119f4329f9421
```

See:

`../../generated/native-normalizations/rhel9-oracle9-xattr-reuse.json`

This is a strong published-content example of one technical assessment being reusable across different policy identities, while also demonstrating why reuse needs provenance and review status.

## Differential tests still required

Before promotion to `exact_normalized`, fixtures should cover:

- all source-enforced syscall/architecture/AUID combinations;
- the two duplicated conditions;
- the two absent b64/root conditions;
- combined syscall lists;
- both accepted action orderings;
- optional audit keys;
- unset AUID spellings;
- missing and malformed rules;
- collection/read failures.

The source behavior and any reviewed correction should be tested separately.
