# Requirements-first B — six-STIG source-coverage importer

**Structural import only. NOT a successful native translation, lossless source execution, or A/B bake-off.**
Input is the published immutable **SCAP-NG 0.3 six-STIG authoring ZIP**,
**not** a raw SCAP 1.4 XML datastream. Capsule documents retain exact parsed
source YAML, ID, raw digest, original path and an independent normalized digest.
Every referenced choice and Rule ID is checked; native and compatibility
execution remain pending.

| Source property | Verified value |
|---|---:|
| Benchmark directories | 6 |
| Rules with validated choice bindings | 1567 |
| Unique referenced Assessments | 2395 |
| Assessment-choice bindings | 2958 |
| Source YAML files examined | 4012 |

## Per benchmark

| Benchmark | Rules |
|---|---:|
| apache_server_2-4_unix_server | 45 |
| ms_windows_11 | 257 |
| ms_windows_server_2025 | 291 |
| ms_windows_server_dns | 81 |
| oracle_linux_9 | 448 |
| rhel_9 | 445 |

## What this does not prove

It does not prove semantic equivalence to SCAP 1.4, native rewrite coverage,
manual handling quality, imported OVAL State/Variable behavior, applicability
execution, six-state evaluation or a working scanner. The preserved source
capsules are **nonexecutable** and marked compatibility_execution_pending.
The original six-STIG 0.3 authoring ZIP is itself a converted source;
raw SCAP 1.4 parity requires a separate importer using the existing
oval_semantic_ir.py and scap14_benchmark_ir.py source parsers.

Neither A nor B has been competitively scored here. This is B capability
engineering pursuant to [the readiness gate](../CAPABILITY-READINESS-GATE.md).
