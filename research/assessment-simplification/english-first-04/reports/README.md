# Six-STIG research reports — readable on github.com

**Pre-alpha research; not approved SCAP-NG 0.4 syntax or scanner-conformance evidence.**

This page is for networks and phones that cannot access GitHub Actions artifact downloads. Reports are being moved to ordinary Markdown and JSON files directly under this repository, so readers do not need to download ZIP artifacts from GitHub's separate artifact-hosting domains.

**[Read the verified six-STIG checkpoint in Markdown](2026-10-16-verified-checkpoint.md)** — full table of corpus coverage, complexity counts, six-state comparisons and remaining limitations, hosted entirely on github.com.

## Latest previously verified results

| Research gate | Previously verified result | Evidence |
| --- | --- | --- |
| Whole source-Assessment structural reconstruction | 871 of 872 automated Assessments (1,374 of 1,375 Tests) | [Six-STIG run 38922336217](https://github.com/vanderpol/scap-ng/actions/runs/38922336217) |
| Generic six-state comparison | 125,268 agreed defined cases; 12 excluded empty-population cases | [Six-STIG and six-state run 38922336217](https://github.com/vanderpol/scap-ng/actions/runs/38922336217) |
| Remaining unusual source shape | A Linux boot-loader check combines none_exist with an attached State | [Research explanation](https://github.com/vanderpol/scap-ng/blob/main/research/assessment-simplification/english-first-04/README.md) |

These are **historical verified figures**, not confirmation that the newer direct-Set and reference-dependency audit has passed. Structural reconstruction is **not** original OVAL runtime/evidence parity.

## Updated report publishing

The [six-STIG workflow](https://github.com/vanderpol/scap-ng/actions/workflows/research-english-first-census-04.yml) is being configured to publish each successful audit as a Markdown summary and, where the JSON is small enough for GitHub's online viewer, the source JSON. Once publication succeeds, this page will automatically list the report links (including the named source and variable reference graph).

The existing ZIP artifacts remain optional, not the primary way to read results.

Tracking: [English-first research issue #235](https://github.com/vanderpol/scap-ng/issues/235).
