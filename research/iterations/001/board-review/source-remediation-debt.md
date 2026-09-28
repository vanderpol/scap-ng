# SCAP 1.4 Source-Remediation Debt Before SCAP-NG Conversion

The full 65-benchmark pinned NIWC survey identifies **155 automated rules** that
cannot be converted to SCAP-NG because they reference OVAL tests whose effective
status remains deprecated.

This report treats those rules as **SCAP 1.4 source-remediation debt**, not as a
reason for SCAP-NG scanners to implement obsolete collectors.

## Effective deprecated-test references

Across the 155 blocked rules:

| OVAL test | Deprecated-test references in blocked rules | Replacement / disposition |
| --- | ---: | --- |
| Windows `accesstoken_test` | 168 | use supported `userright_test` semantics where applicable |
| Windows `wmi_test` | 36 | migrate to supported `wmi57_test` |
| Windows `user_test` | 10 | migrate to supported `user_sid55_test` |

The reference count is larger than the blocked-rule count because one rule can
contain more than one deprecated test reference.

## Benchmark-level remediation backlog

| Published benchmark | Blocked automated rules | Deprecated-test references |
| --- | ---: | --- |
| Windows Server 2012/2012 R2 Domain Controller | 42 | 32 `accesstoken_test`, 20 `wmi_test` |
| Windows Server 2012/2012 R2 Member Server | 39 | 45 `accesstoken_test`, 3 `user_test`, 14 `wmi_test` |
| Windows Server 2016 | 39 | 51 `accesstoken_test`, 2 `wmi_test` |
| Windows 10 | 29 | 40 `accesstoken_test`, 1 `user_test` |
| Windows 11 | 1 | 1 `user_test` |
| Windows Server 2019 | 1 | 1 `user_test` |
| Windows Server 2022 | 1 | 1 `user_test` |
| Windows Server 2025 | 1 | 1 `user_test` |
| SQL Server 2016 Instance | 1 | 1 `user_test` |
| SQL Server 2022 Instance | 1 | 1 `user_test` |

## Current Windows migration opportunity

For the current Windows client/server demonstration, the modernization burden is
small and concrete:

- Windows 11: one automated rule must move from `user_test` to
  `user_sid55_test`; a Windows 11 applicability definition also uses
  `user_test` and must be corrected.
- Windows Server 2025: one automated rule must move from `user_test` to
  `user_sid55_test`; its applicability assessment is otherwise convertible.
- Windows Server 2019 and 2022 similarly contain one blocked automated
  `user_test` rule each.

Correcting these source definitions in SCAP 1.4 first would let the same
deterministic converter reevaluate them for SCAP-NG without adding deprecated
runtime semantics.

## Why reject rather than auto-rewrite

The converter deliberately does not silently substitute a modern test.

Even when a supported replacement is obvious at the test-family level, a
migration tool must not invent object/state semantics, account-identity
interpretation, or policy intent. The content publisher should make the source
change, validate the updated SCAP 1.4 content, and then rerun conversion.

That preserves a clean migration audit trail and prevents SCAP-NG from becoming
a compatibility layer for known-obsolete OVAL constructs.

## Board/content-author value

This backlog makes the transition requirement actionable:

1. modernize the small number of blocked current-platform rules now;
2. validate them using the existing SCAP 1.4 toolchain;
3. retain supported OVAL semantics as the source of truth;
4. rerun the SCAP-NG conversion and differential tests;
5. leave deprecated collectors out of the future SCAP-NG scanner contract.

The older Windows benchmarks quantify historical debt, while Windows 11 and
Server 2025 show that current published content is already very close to this
clean conversion boundary.
