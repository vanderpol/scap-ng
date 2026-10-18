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
| Strictly lowered automated fixture IR (not scanner-verified) | 37 |
| Manual procedures compiled (human result still required) | 1550 |
| **Verified executable source-equivalent Assessments** | **0** |

## Per-stream conversion status

| Stream | References | Automated fixture IR | Manual procedure IR | Remaining |
| --- | ---: | ---: | ---: | ---: |
| apache_server_2-4_unix_server | 67 | 0 | 45 | 22 |
| ms_windows_11 | 502 | 0 | 257 | 245 |
| ms_windows_server_2025 | 550 | 0 | 291 | 259 |
| ms_windows_server_dns | 94 | 0 | 73 | 21 |
| oracle_linux_9 | 854 | 36 | 448 | 370 |
| rhel_9 | 861 | 34 | 445 | 382 |

## Classification

| Status | Distinct Assessments |
| --- | ---: |
| fixture_ir_compiled_source_parity_unverified | 37 |
| manual_procedure_ir_compiled | 1550 |
| unsupported_source_semantics | 808 |

Every referenced Assessment is in [the machine-readable conversion ledger](conversion-progress.json).
The research ZIP contains **only** validated fixture IR, manual procedures and metadata; it is
**not** a partial scanner content release. Unsupported content
is never copied into executable IR or silently discarded. Manual procedures remain unevaluated until a human responds.

Remaining release gates: complete original SCAP 1.4 import; implement
OVAL Object/State/Variable/Set and source-specific collection behavior;
six-state runtime/evidence; manual, org-input, applicability, results;
full six-stream executable conversion and differential semantic proof.
No A/B bake-off until those comparable-capability gates pass.

Tracking: [#237](https://github.com/vanderpol/scap-ng/issues/237)
 and [#235](https://github.com/vanderpol/scap-ng/issues/235).
