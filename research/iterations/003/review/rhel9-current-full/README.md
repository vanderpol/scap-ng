# Full RHEL9 current-design review

This is the current full research review generated directly from the original checksum-pinned NIWC RHEL9 V2R9 ZIP. It replaces the historical full tree as the preferred review target. It does not derive from previously generated YAML or invoke a historical whole-benchmark generator.

Start with [benchmark.yaml](benchmark.yaml), the [all-445-Rule index](all-rules.md), and [applicability.yaml](applicability.yaml). Rules directly own named Assessment choices and relative Assessment YAML paths; there are no separate Policy files.

## Coverage and executed checks

| Coverage | Result |
|---|---:|
| Rules | 445 |
| Profiles | 11 |
| Rule/Profile selection comparisons | 4,895, zero mismatches |
| Automated Assessments | 418 |
| Manual Assessments | 445 |
| Applicability Assessments/conditions | 18 |
| Native YAML documents | 1,328 |

Every automated Assessment and all 18 applicability definition graphs compared equal against the original source using root-scoped, ID-independent OVAL semantic comparison; their regenerated OVAL passed the pinned SCAP 1.4 omni-schema. Source-platform negation is represented separately and retained. Distinct GNOME predicates remain distinct; RHEL, Rocky and AlmaLinux applicability use the original publisher's source tests rather than invented OS discovery.

The independent [Rule/source audit](rule-source-audit.json) compares all 445 Rule selector sets, defaults, Assessment source-definition bindings, manual inline procedures, titles, severity, role and weight. All matched. For the 27 manual-default Rules, default and manual selectors reference the same original questionnaire; inline text is shared only after matching its source binding. Conflicting procedures fail. This is an explicit binding, independent of write order.

The [profile audit](profile-selection-audit.json) computes source Benchmark/Group/Rule defaults, profile selectors and inherited selections, then compares the native result. The [selection provenance](profile-selection-provenance.json) retains source actions/inheritance; per-Rule source/default versus explicit attribute evidence is in [evidence.json](evidence.json). This source has no XCCDF Values or non-selection Profile actions; unsupported policy forms fail rather than being silently omitted.

[Validation](validation.json) checks package-boundary-safe relative references, referenced document types, identity uniqueness, defaults, group membership, applicability bindings, current vocabulary and native cleanliness. Collection → Variable → Test → evaluation presentation order is checked across the full review. Generated identity listings are evidence, not an author-maintained lookup index.

Executed focused regressions: 13 named/private Collection tests, 16 retained Variable/filter/set depth tests, 3 shared manual-binding regressions and 3 profile-selection regressions passed locally. The full original-package build, comparative audits and reverse omni-schema validation passed on both Windows and Linux in [CI run 36777776205](https://github.com/vanderpol/scap-ng/actions/runs/36777776205), using converter commit `93c0f8de6ea5d80f0795e173a97be6f2b51cd67c`. See [ci-verification.json](ci-verification.json).

## Useful review entry points

- [SV-257777 Rule](rules/SV-257777.rule.yaml): default/automated/manual choices with explicit relative paths.
- [SV-257778 Rule](rules/SV-257778.rule.yaml): manual default alias with a verified shared questionnaire binding.
- [SV-258013 Assessment](assessments/automated/SV-258013.automated.assessment.yaml): named Collection shared by a Test and Variable.
- [SV-258155 Assessment](assessments/automated/SV-258155.automated.assessment.yaml): Variable-only source capability binding and arithmetic.
- [SV-257889 Assessment](assessments/automated/SV-257889.automated.assessment.yaml): set/filter dependencies and Variables.

## Reproduce on a Windows development computer

With the repository checked out, Python 3.12 installed, and the pinned ZIP available locally, run from the repository root. The output directory must be new or empty. Conversion itself needs no network, credentials, Linux shell or GitHub Actions.

```powershell
python -m pip install PyYAML==6.0.3 lxml==6.1.1
python tools/scap_upconvert_v003/convert_full_review.py `
  --input "C:/SCAP/U_RHEL_9_V2R9_STIG_SCAP_1-4_Benchmark-enhancedV13-signed.zip" `
  --sha256 70aa6a16221df2c53b094b11b48b16aca1f6d7147c11123b655659ca7711dbb5 `
  --output work/rhel9-current-full
```

The CLI can also run from another working directory using its absolute script/input/output paths; its default schema is located relative to the script. It emits native YAML and comparative evidence, not this editorial README/index. Re-running into a populated directory is rejected. The checksum is verified before parsing. Source revision: `8c8e5dff860af6b1290ee9273a282db24278f8d5`.

## Research limits and pending design

This is a complete Rule/Assessment review for this pinned package, not a stable converter or an approved NG specification. `assessment_choices`, Variable `collection_capabilities`, and `assertion.item_quantifier` remain working grammar pending design/Board review. Both named-reference and private embedded Collection Variable forms remain required; source conversion uses named identities to preserve sharing. `ng_schema_version` is explicitly null until an NG schema is assigned.

Representation comparison and reverse schema validation do not establish scanner execution equivalence, complete language conformance, finalized NG JSON-schema validity or source STIG accuracy. Manual Check Text is preserved; the complete OCIL questionnaire execution model is not validated. Benchmark/Profile selection parity does not prove tailoring/runtime behavior. Compiled package/signature generation and shared cross-Benchmark reuse are later integration work. The broader NGINX Test/Collection capability mismatch remains a source conversion blocker outside this RHEL9 package.

Provenance: **Inherited** pinned source content and established semantic helpers; **Common** native graph/relative-reference rendering and validation; **Evidence/Audit** independent source comparisons, profile resolution, schema checks and focused regressions. Legacy identities stay in JSON evidence, outside native source.
