# B six-STIG source Variable graph scheduling coverage

**Converted-0.3 structural planning only. No scanner execution, no original SCAP 1.4 parity.**

**Automated Assessments declaring Variables:** 77
**Closed topological source plans:** 77
**Plan failures (source integrity and supported graph shape):** 0

A structural plan preserves the source expressions and shared-Object
references and ensures dependency closure. It does **not** implement
the source expressions, execute commands, evaluate Rule results,
or increase the six-STIG fixture IR conversion count.

## Unplanned source Assessments

| Assessment | Blocker |
| --- | --- |
| None | All reference graphs structurally schedulable |

The [full per-Assessment plan report](variable-plan-coverage.json)
contains source SHA-256 values, declared operators and shared Object references.
The [19-Variable Apache exemplar](apache-variable-plan.json) is separately
published and explicitly marked execution_supported=false.
