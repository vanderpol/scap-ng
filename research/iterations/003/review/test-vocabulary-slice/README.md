# Test vocabulary and relative-path review slice

Status: **INCOMPLETE — AUTHORING READINESS BLOCKED**. See [current design](../../design/CURRENT-DESIGN.md) and [preflight findings](readiness.json). Narrow tests passed, but Collection/Variable coverage and complete native vocabulary migration are missing. Architecture: **Benchmark → Rule → Assessment**; no separate Policy object or file. Two real RHEL 9 rules; no full benchmark regeneration, scanner execution, or runtime-equivalence claim.

Review these in order:

1. [Rule: vendor-supported release](rules/SV-257777.rule.yaml) — proposed `assessment_choices` and `default_assessment_choice`. Named selectors (`default`, `automated`, `manual`) retain their original identities and default selection. Each choice explicitly references an Assessment YAML path relative to the Rule file. `default` and `automated` intentionally select the same Assessment.
2. [Automated release Assessment](assessments/automated/SV-257777.automated.assessment.yaml) — `tests`, searchable `test-` IDs, `test_title`, and `evaluate.test`; `item_quantifier` replaces the vague Test-level `check` field. The existing multiple-State boundaries, operator and values remain intact. The removed native `deprecated` attribute is absent; stale `deprecated: false` in the baseline is discarded as historical metadata.
3. [Automated boot-target Assessment](assessments/automated/SV-257781.automated.assessment.yaml) — includes the symlink Test raised in the owner's feedback, now named `test-default-target-symlinked-multi-user-target`.
4. [Manual Assessment](assessments/manual/SV-257777.manual.assessment.yaml) — a Rule choice may select a manual procedure rather than a technical Test. This is why Rule choices are named separately from Assessment `tests`.
5. [Validation evidence](validation.json).

## Proposed terminology

| Meaning | Review-candidate field |
| --- | --- |
| Rule names an Assessment implementation | `assessment_choices.<selector>.assessment` |
| Rule identifies its default selector | `default_assessment_choice` |
| Assessment defines technical evaluations | `tests` |
| Technical Test identity | `test-<meaningful-name>` |
| Evaluation expression references a Test | `test` |
| Quantification across collected items | `item_quantifier` |

These names are a proposal for owner review. Selector semantics and assessment identity are preserved. Assessment IDs identify complete implementations; only technical Test IDs receive the `test-` prefix. IDs remain local to their Assessment, so identical names in separate files are allowed.

## Validation and provenance

Reproduce from the repository root:

```sh
python tools/scap_upconvert_v003/test_assessment_test_syntax.py
python tools/scap_upconvert_v003/test_split_policy_paths.py
python tools/scap_upconvert_v003/test_rule_assessment_slice.py
python tools/scap_upconvert_v003/build_test_vocabulary_slice.py
```

Fifteen focused regressions passed: nested Boolean references, repeated Test references, invalid Test targets, preservation of manual payloads, rejection of unintended semantic changes, source-path identity/type/boundary guards, direct Rule-to-Assessment resolution, absence of separate Policy linkage, and removal of stale `deprecated: false`. Deprecated or ambiguous status is rejected rather than emitted. Six explicit Rule-to-Assessment paths resolved. Six Assessment comparisons (including default/automated aliases) matched the baseline after the declared vocabulary substitutions.

Source: committed split-rule RHEL 9 review at `54f8764c`, ultimately derived from the pinned NIWC enhanced RHEL 9 SCAP 1.4 source recorded in `research/iterations/003/evidence/rhel9-full/source-package.json`. Category: **Adapted** for the mechanical vocabulary changes; **Inherited** for all retained Rule and Assessment content; **Evidence/Audit** for slice validation. Source values and defects are preserved; this slice does not update policy requirements.

Remaining work after owner syntax review: apply accepted names to the main generator and its consumers, regenerate and compare all RHEL 9 rules/assessments, then run full round-trip regression with the Windows 11 deprecated-Test rejection cases retained. The complete generated source and compiled package are unchanged by this slice. The earlier version of this slice mistakenly restored Policy files; this revision removes them and restores Rule-owned selection.
