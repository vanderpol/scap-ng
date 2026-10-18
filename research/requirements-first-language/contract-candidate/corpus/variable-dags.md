# B six-STIG converted-source Variable DAG census

**Source 0.3 structural research only — not original SCAP 1.4 XML parity or executable content.**

**Assessments declaring Variables:** 77
**Declared local Variables:** 376
**Largest observed declared dependency depth:** 9
**Assessments with cycles (structural analyzer):** 0
**Assessments with unresolved Variable references:** 0

## Variable expression operators

| Operator | Declared Variables using it |
| --- | ---: |
| concat | 220 |
| regex_capture | 77 |
| merge | 34 |
| unique | 16 |
| values | 15 |
| count | 7 |
| split | 5 |
| arithmetic | 1 |
| literal | 1 |

## Small and complex example graphs

| Assessment | Variables | Depth | Operators |
| --- | ---: | ---: | --- |
| SV-253363.automated | 1 | 1 | merge(1) |
| SV-253401.automated | 1 | 1 | concat(1) |
| SV-253433.automated | 1 | 1 | values(1) |
| SV-253435.automated | 1 | 1 | concat(1) |
| SV-253436.automated | 1 | 1 | concat(1) |
| SV-214268.automated | 19 | 9 | concat(12), merge(2), regex_capture(4), unique(1) |
| SV-214228.automated | 18 | 9 | concat(11), merge(2), regex_capture(4), unique(1) |
| SV-214257.automated | 18 | 9 | concat(11), merge(2), regex_capture(4), unique(1) |
| SV-214230.automated | 17 | 9 | concat(10), merge(2), regex_capture(4), unique(1) |
| SV-214232.automated | 17 | 9 | concat(10), merge(2), regex_capture(4), unique(1) |
| SV-214251.automated | 17 | 9 | concat(10), merge(2), regex_capture(4), unique(1) |
| SV-214252.automated | 17 | 9 | concat(10), merge(2), regex_capture(4), unique(1) |
| SV-214265.automated | 17 | 9 | concat(10), merge(2), regex_capture(4), unique(1) |

[Complete per-Assessment DAGs](variable-dags.json).

Graph references are inferred structurally from literal variable
references; source OVAL lexical cardinality, set semantics and
Object/State scope must still be proven separately. A cycle-free
source DAG is NOT necessarily executable by the current B pilot.
