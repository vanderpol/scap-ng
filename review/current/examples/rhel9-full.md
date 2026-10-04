# RHEL 9 full-review example

Use this page to inspect how the current **Benchmark → Rule → Assessment** model scales to a complete RHEL 9 STIG and to reproduce the source-driven review.

The reviewed source set covered **445 Rules, 11 Profiles, 418 automated Assessments, 445 manual Assessments, 18 applicability conditions, and 4,895 Rule/Profile selection comparisons**. Those comparisons matched the pinned source at the recorded checkpoint. This is migration/representation evidence, not proof of live-target or independent-scanner equivalence.

## Browse the generated review

1. [Benchmark](../../../research/iterations/003/review/rhel9-current-full/benchmark.yaml) — membership, Groups, Profiles, and publication metadata.
2. [Typical Rule](../../../research/iterations/003/review/rhel9-current-full/rules/SV-257777.rule.yaml) — requirement and named Assessment choices.
3. [Automated Assessment](../../../research/iterations/003/review/rhel9-current-full/assessments/automated/SV-257777.automated.assessment.yaml) and [manual Assessment](../../../research/iterations/003/review/rhel9-current-full/assessments/manual/SV-257777.manual.assessment.yaml) — technical graph versus human procedure.
4. [Variable/dependency stress example](../../../research/iterations/003/review/rhel9-current-full/assessments/automated/SV-258179.automated.assessment.yaml) — complex OVAL-derived behavior.
5. [Applicability registry](../../../research/iterations/003/review/rhel9-current-full/applicability.yaml), [profile audit](../../../research/iterations/003/review/rhel9-current-full/profile-selection-audit.json), [source Rule audit](../../../research/iterations/003/review/rhel9-current-full/rule-source-audit.json), and [validation](../../../research/iterations/003/review/rhel9-current-full/validation.json).

The [recorded evidence](../../../research/iterations/003/review/rhel9-current-full/evidence.json) pins NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5` and original ZIP SHA-256 `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`.

## Reproduce locally

Use the original pinned NIWC RHEL 9 V2R9 SCAP 1.4 ZIP, not a previously generated YAML tree:

```powershell
python -m pip install PyYAML==6.0.3 lxml==6.1.1
python tools/scap_upconvert_v003/convert_full_review.py --input "PATH_TO_RHEL9.zip" --sha256 70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5 --output work/rhel9 --schema third_party/scap-1.4-schemas/omni-schema.xsd
```

For the maintained tool catalog see [Human-runnable SCAP-NG tools](../../../tools/HUMAN-RUNNABLE-SCRIPTS.md). The exhaustive generated tree is evidence rather than normative source; compact summaries stay here while bulk proof may live in `vanderpol/scap-ng-evidence`.
