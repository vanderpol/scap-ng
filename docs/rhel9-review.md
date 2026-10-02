# RHEL 9 source/design review

This guide points to the current full-review tree rather than the superseded `source/` baseline. The previously advertised `rhel9-current-full/README.md` is absent from the pinned tree; this maintained guide is outside the generated directory so regeneration cannot erase it.

The [recorded evidence](../research/iterations/003/review/rhel9-current-full/evidence.json) identifies NIWC revision `8c8e5dff860af6b1290ee9273a282db24278f8d5` and original ZIP SHA-256 `70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5`. It records 4,895 Rule/Profile comparisons and 18 applicability conditions. Read its explicit limits: prototype grammar, incomplete OCIL treatment and representation checks rather than target runtime equivalence.

## Browse in order

1. [Benchmark](../research/iterations/003/review/rhel9-current-full/benchmark.yaml): membership, Groups, Profiles and publication metadata.
2. [Typical Rule](../research/iterations/003/review/rhel9-current-full/rules/SV-257777.rule.yaml): requirement and named Assessment choices.
3. [Automated Assessment](../research/iterations/003/review/rhel9-current-full/assessments/automated/SV-257777.automated.assessment.yaml) and [manual Assessment](../research/iterations/003/review/rhel9-current-full/assessments/manual/SV-257777.manual.assessment.yaml): technical graph versus human procedure.
4. [Variable/dependency stress example](../research/iterations/003/review/rhel9-current-full/assessments/automated/SV-258179.automated.assessment.yaml): complex OVAL-derived behavior; source defects must not be silently repaired.
5. [Applicability registry](../research/iterations/003/review/rhel9-current-full/applicability.yaml), [profile audit](../research/iterations/003/review/rhel9-current-full/profile-selection-audit.json), [source Rule audit](../research/iterations/003/review/rhel9-current-full/rule-source-audit.json) and [validation](../research/iterations/003/review/rhel9-current-full/validation.json).

For the most recent reviewed native capability normalization, use the [full-corpus shared Assessment snapshot](../research/iterations/003/review/full-current-native-normalized/README.md) and its separate provenance/handled-error reports. Do not assume every earlier full-review payload already expresses every later clean-native capability mapping.

## Reproduce locally

Use the original pinned NIWC RHEL 9 V2R9 SCAP 1.4 ZIP, not a previously generated YAML tree. From the checkout root:

```powershell
python -m pip install PyYAML==6.0.3 lxml==6.1.1
python tools/scap_upconvert_v003/convert_full_review.py --input "PATH_TO_RHEL9.zip" --sha256 70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5 --output work/rhel9 --schema third_party/scap-1.4-schemas/omni-schema.xsd
```

[Maintained converter](../tools/scap_upconvert_v003/README.md) · [Current working design](../research/iterations/003/design/CURRENT-DESIGN.md) · [Board proposal index](../board/proposals/README.md).
