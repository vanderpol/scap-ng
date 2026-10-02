# RHEL 9 full-review example

This is the stable reviewer-facing entry point for the generated RHEL 9 SCAP-NG example.

## What was demonstrated

The current source-driven RHEL 9 review covered:

- 445 Rules;
- 11 Profiles;
- 418 automated Assessments;
- 445 manual Assessments;
- 18 source-driven applicability conditions;
- 4,895 Rule/Profile selection comparisons matching the pinned source.

Automated/applicability definition round trips and pinned schema checks passed for the reviewed checkpoint. This is migration/representation evidence, not proof of target-runtime evaluator equivalence.

## Review use

Use this example to inspect how the current Benchmark → Rule → Assessment model scales to a complete STIG.

The exhaustive generated tree is evidence, not normative source. During repository rebaselining, bulk generated output is being separated from the main review repository. Representative examples and summaries remain here; exhaustive proof belongs in `vanderpol/scap-ng-evidence`.

## Provenance

Original generated tree:

`research/iterations/003/review/rhel9-current-full/`

Original tree identity:

`c0259cc7a1f9d28780d9ad449c8d631e246ba6dd`

Supporting evidence already migrated includes:

- `runs/rhel9/2026-09-30-full/`
- `runs/rhel9/2026-09-30-review-slice/`

in `vanderpol/scap-ng-evidence`.

The pre-rebaseline Git tag/history remains the recovery source for the original generated tree.
