# B six-STIG source regex_capture parity risk audit

**Research only. Counts Python capture groups in converted 0.3 source,
not original OVAL regex compilation or source-equivalent execution.**

**Expressions:** 117
**Assessments:** 31

| Capture-group shape | Expressions |
| --- | ---: |
| first_capture_only | 101 |
| multiple_capture_groups | 16 |

The [published OVAL Definitions schema](https://github.com/OVALProject/Language/blob/master/schemas/oval-definitions-schema.xsd)
documents that regex_capture uses **only the first capture group**
and produces an **empty string** for a nonmatching target.
A converted expression with two or more groups is **not automatically
incorrect**, but must not be rewritten to select another group.

## Multi-group/zero-group source examples

| Assessment | Variable | Groups | Source expression path |
| --- | --- | ---: | --- |
| SV-214228.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214230.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214231.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214232.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214241.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214243.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214246.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214250.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214251.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214252.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214255.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214256.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214257.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214265.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214268.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |
| SV-214269.automated | apache-base-install-directories-unix-variable | 2 | expression/regex_capture |

[Complete exact source patterns](regex-capture-audit.json).
All resulting values still require original SCAP 1.4 source
differential tests, including OVAL-versus-Python regex lexical parity.
These cases are **not** added to executable conversion totals.
