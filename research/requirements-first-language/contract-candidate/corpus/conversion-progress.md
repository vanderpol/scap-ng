# 0.4-B six-STIG executable conversion progress

**Research only. THIS IS NOT a completed conversion or scanner package.**
Source is the immutable published SCAP-NG 0.3 six-STIG authoring ZIP,
not original SCAP 1.4 XML. A valid JSON fixture IR is not source parity.

| Verified corpus dimension | Count |
| --- | ---: |
| STIG streams | 6 |
| Rules | 1567 |
| Assessment-choice links | 2958 |
| Distinct referenced Assessments | 2395 |
| Strictly lowered fixture-IR Assessments (not scanner-verified) | 13 |
| **Verified executable source-equivalent Assessments** | **0** |

## Per-stream conversion status

| Stream | References | Fixture IR (unverified) | Remaining/unimplemented |
| --- | ---: | ---: | ---: |
| apache_server_2-4_unix_server | 67 | 0 | 67 |
| ms_windows_11 | 502 | 0 | 502 |
| ms_windows_server_2025 | 550 | 0 | 550 |
| ms_windows_server_dns | 94 | 0 | 94 |
| oracle_linux_9 | 854 | 12 | 842 |
| rhel_9 | 861 | 11 | 850 |

## Classification

| Status | Distinct Assessments |
| --- | ---: |
| fixture_ir_compiled_source_parity_unverified | 13 |
| manual_contract_unimplemented | 1550 |
| unsupported_source_semantics | 832 |

Every referenced Assessment is in [the machine-readable conversion ledger](conversion-progress.json).
The research ZIP contains **only** validated fixture IR and metadata; it is
**not** a partial scanner content release. Unsupported/manual content
is never copied into executable IR or silently discarded from the ledger.

Remaining release gates: complete original SCAP 1.4 import; implement
OVAL Object/State/Variable/Set and source-specific collection behavior;
six-state runtime/evidence; manual, org-input, applicability, results;
full six-stream executable conversion and differential semantic proof.
No A/B bake-off until those comparable-capability gates pass.

Tracking: [#237](https://github.com/vanderpol/scap-ng/issues/237)
 and [#235](https://github.com/vanderpol/scap-ng/issues/235).
