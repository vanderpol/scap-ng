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

## Scale beyond four benchmarks

The four anchors were selected for depth and for two natural reuse pairs. They
are not a claim about ecosystem-wide reuse percentage.

Once the fingerprint/mapping method is stable, the same analysis can run across
all individual benchmarks in the pinned NIWC `Current/` corpus. That larger
run can provide:

- total exact reusable assessment groups;
- reuse fan-out across multiple STIGs;
- platform-family reuse percentages;
- duplicated maintenance units avoided across the corpus;
- parameterization candidates that merit human review.

The full-corpus result, combined with an organization's own H/C/R values, is
the appropriate basis for an at-scale cost estimate.

## Parameterization upper bound

After literal values are abstracted, the four-anchor sample contains **400**
unique semantic shapes versus 1,331 assessment instances. This corresponds to
an upper-bound candidate reduction of **69.95%**.

This is **not** counted as proven reuse. Literal abstraction can group checks
whose differing paths, thresholds, names, or values are policy-significant.
Each candidate must be reviewed and typed before it can become a reusable
parameterized assessment.
