# Verified six-STIG English-first research checkpoint

**Research as of October 16, 2026. Source: [passing pinned six-STIG workflow 38922336217](https://github.com/vanderpol/scap-ng/actions/runs/38922336217).**

This report is readable entirely on github.com without Actions artifact downloads. The numbers below were extracted from the previously verified workflow's JSON reports, **not from the newer direct-Set/reference-graph workflow**.

| Measure | Previously verified result |
| --- | ---: |
| Unique automated Assessments in pinned six STIGs | 872 |
| Complete original source Assessment structures reconstructed | **871** |
| Unsupported source shapes | **1** |
| Named Tests in reconstructed Assessments | **1,374 / 1,375** |
| Negative structure guards passed | 871 |
| English-first compact-layout YAML reduction | **4.49%** |
| Generic six-state result combinations agreeing | **125,268** |
| Empty-population reference cases still unresolved | **12** |

## Corpus shape and authoring challenges

These counts overlap; they are not a partition of the 1,375 Tests.

| Source characteristic | Count |
| --- | ---: |
| Named Tests | 1,375 |
| Simple scalar Tests | 918 |
| Tests with collector parameters | 675 |
| State-free Tests | 387 |
| Tests with State logic | 219 |
| Tests using Sets | 145 |
| Tests referencing Variables in Objects | 139 |
| Tests with record structures | 66 |
| Tests with unusual/objectless source shapes | 114 |

## Limitations

**Source-structure equality is not runtime equivalence.** A 0.4 scanner has not independently demonstrated OVAL collection and six-state evidence parity. The single remaining source exception combines `none_exist` with an attached State, and 12 empty State-result cases are not defined by the generic reference helper. No semantic rewrite was accepted to conceal either issue.

The subsequent direct `union`/`difference` compact layout and named source/variable dependency checker were **not included in this verified run**. Their own results must be published and reviewed separately.

The new research reports are listed at [the online six-STIG reports home](README.md).
