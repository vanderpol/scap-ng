# Assessment Reuse and Maintenance-Cost Evidence

## What is measured

The four-anchor analysis measures duplicated **technical assessment definitions**,
not merely similar rule wording.

The observed baseline contains **1,331** supported generic automated assessment
instances. Exact semantic fingerprinting reduces these to **804** unique
technical assessments.

Therefore **527 independently maintained assessment definitions are avoidable**
if the exact reuse already present in the published content is expressed
explicitly.

That is a **39.59% reduction in assessment-definition maintenance units** for
this four-benchmark sample.

## Pair-level impact

| Pair | Automated instances | Exact reusable rules | Duplicate definitions avoided |
| --- | ---: | ---: | ---: |
| RHEL 9 + Oracle Linux 9 | 826 | 368 rules on each side | 369 |
| Windows 11 + Server 2025 | 505 | 158 rules on each side | 158 |
| **Four-anchor total** | **1,331** | — | **527** |

The Linux duplicate count is 369 rather than 368 because one exact semantic
group contains four policy rules: two RHEL rules and two Oracle Linux rules
share the same technical assessment.

## Why this can reduce cost

A duplicated assessment can impose repeated work for:

- initial authoring or migration;
- technical review;
- test-fixture development;
- regression testing;
- provenance/version updates;
- future collector/schema changes;
- defect repair;
- platform-version refreshes.

SCAP-NG reuse does not eliminate policy review. It removes repeated maintenance
of technical logic that has already been proven equivalent.

## Organization-specific formulas

Let:

- **D** = exact duplicate assessment definitions avoided;
- **H** = average hours to author/review/test one assessment for a given event;
- **C** = average relevant maintenance events per assessment per year;
- **R** = loaded labor rate per hour.

For the measured four-anchor set, **D = 527**.

One-time or full-cycle effort avoided:

    hours_avoided = D * H

Recurring annual effort avoided:

    annual_hours_avoided = D * C * H

Illustrative annual labor-cost model:

    annual_cost_avoided = D * C * H * R

No value for H, C, or R is asserted by this research. Organizations should
apply their own measured labor and change-rate data.

### Effort-only illustration

If a complete assessment author/review/test event averages:

| Hours per duplicated assessment event | Four-anchor hours avoided |
| ---: | ---: |
| 1 | 527 |
| 2 | 1,054 |
| 4 | 2,108 |
| 8 | 4,216 |

These are arithmetic scenarios, not observed labor measurements.

## Scale across all 65 signed benchmarks

The fingerprint/mapping method has now been run across all **65 individual
published signed benchmark ZIPs** in the pinned NIWC `Current/` corpus.

Measured at that scale:

| Measure | Result |
| --- | ---: |
| XCCDF rules | 8,892 |
| Supported automated assessment instances | 7,084 |
| Unique exact technical assessments | 3,413 |
| Duplicate assessment definitions avoided, total exact reuse | **3,671** |
| Total exact maintenance-unit reduction | **51.82%** |
| Cross-benchmark exact-reuse groups | 1,701 |
| Cross-benchmark exact-reuse instances | 5,340 |
| Duplicate definitions avoided specifically across benchmarks | **3,639** |
| Cross-benchmark reduction over supported automated assessments | **51.37%** |

For a broad "deduplicate all identical assessments" cost model, **D = 3,671**.
For the narrower cross-STIG/cross-benchmark reuse argument, **D = 3,639**.
The remaining 32 avoidable units are duplicates found within individual
benchmarks. The four-anchor deep demonstration has D = 527 in either framing.

### Full-corpus effort-only illustration

If a complete assessment author/review/test event averages:

| Hours per duplicated assessment event | All exact duplicates (D=3,671) | Cross-benchmark only (D=3,639) |
| ---: | ---: | ---: |
| 1 | 3,671 | 3,639 |
| 2 | 7,342 | 7,278 |
| 4 | 14,684 | 14,556 |
| 8 | 29,368 | 29,112 |

These remain arithmetic scenarios, not observed labor measurements. They show
how measured reuse units can be translated into an organization's own labor
model without inventing a universal dollar value.

### Fan-out matters

Exact reuse is not confined to two related STIGs. The full-corpus survey found
exact assessment groups spanning as many as **13 different benchmarks**. A
single correction, test improvement, or collector migration for such an
assessment can therefore replace repeated work across many policy publications.

## Parameterization upper bound

After literal values are abstracted, the four-anchor sample contains **400**
unique semantic shapes versus 1,331 assessment instances, an upper-bound
candidate reduction of **69.95%**.

At full-corpus scale, 7,084 supported automated assessment instances collapse
to **1,593** semantic shapes after literal abstraction, an upper-bound candidate
reduction of **77.51%**.

This is **not** counted as proven reuse. Literal abstraction can group checks
whose differing paths, thresholds, names, or values are policy-significant.
Each candidate must be reviewed and typed before it can become a reusable
parameterized assessment.
