# Windows 11 current full SCAP-NG review

Generated from the pinned NIWC Windows 11 V2R10 SCAP 1.4 package at
repository revision `8c8e5dff860af6b1290ee9273a282db24278f8d5`.

Start with `benchmark.yaml`, then follow a Rule in `rules/` through
its explicit relative `assessment_choices` path to `assessments/`.
Conversion/audit evidence is kept in the JSON files at this directory
root.

## Deprecated OVAL handling

Deprecated OVAL Tests are conversion errors for automated SCAP-NG
Assessment content. They are not silently translated or reinstated.
Where the published STIG also supplies a verified manual check, the
affected Rule is emitted as manual-only for review and the skipped
automated source is recorded in `evidence.json`.

The published Windows 11 source includes a deprecated `windows.user_test`
in one Rule and an associated applicability condition. Those automated
paths are intentionally skipped; the source manual procedure remains
available to determine the Rule result/applicability. No round-trip
equivalence claim is made for the skipped deprecated paths.

## Review boundary

This artifact is intended for native source/design review. Successful
source comparison, reverse OVAL validation and semantic round-trip
checks establish conversion/representation evidence for supported
automated content; they do not by themselves prove target-runtime
evaluator equivalence.
