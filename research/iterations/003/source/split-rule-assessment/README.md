# Split Rule / Policy / Assessment Source (iteration 003 — work in progress)

> **Design review warning:** The committed `rhel9-full/` source is **generated conversion evidence**, not a ratified native authoring format or production content. The complete Rule → Policy → Assessment reference chain is **not yet implemented**. See [issue #31](https://github.com/vanderpol/scap-ng/issues/31) and the [review readiness checklist](../../review/FULL-BENCHMARK-READINESS.md).

## Accepted logical design

```text
Benchmark
  ├─ profiles: overrides of effective baseline rule selections
  ├─ groups, parameters and applicability references
  └─ Rule ID
        └─ Policy ID                    [NOT YET IMPLEMENTED]
             ├─ named check selector(s)
             ├─ default selector
             └─ Assessment ID
                  └─ resolved exact assessment file via manifest/registry
```

A Rule must not choose an assessment implementation directly. Policy declares selectors and how they resolve to assessments. An applicability ID maps to an applicability assessment through the separate registry.

## What the current RHEL 9 generated artifacts actually contain

- `rhel9-full/benchmark.yaml` contains benchmark metadata, profiles, groups, a list of 445 Rule IDs and the applicability registry file.
- `rhel9-full/rules/SV-257777.rule.yaml` has `checks` pointing to **assessment IDs**, not paths or independent Policy objects.
- `rhel9-full/assessments/automated/SV-257777.automated.assessment.yaml` is the associated assessment, and `assessments/manual/` holds manual variants. Filenames happen to follow IDs today, but implicit path inference is not accepted as a normative reference protocol.
- `rhel9-full/applicability.yaml` contains separate applicability binding information.
- Profiles currently express only `disabled_rules` exceptions for rule selections turned off; empty profiles carry no explicit changes. The effective baseline and XCCDF Group/Rule defaults must still be verified against the source. See [issue #30](https://github.com/vanderpol/scap-ng/issues/30).

For a current **illustrative** trace, follow `SV-257777` from `benchmark.yaml` to `rules/SV-257777.rule.yaml`, read its `checks.default` assessment ID, then inspect `assessments/automated/SV-257777.automated.assessment.yaml`. This is a temporary reviewer navigation aid, **not** the final SCAP-NG authoring contract.

## Planned directory shape (not implemented in full)

```text
<benchmark>/
  benchmark.yaml
  applicability.yaml
  rules/
  policies/             # new: explicit Rule → Policy check bindings
  assessments/
    automated/
    manual/
    applicability/
```

The Benchmark owns its profiles, groups and parameters. Legacy XCCDF/OVAL/CPE XML IDs, input XML metadata, conversion diagnostics and provenance belong in evidence, not native source. No SCAP 1.4 serialization structure is permitted in native assessment logic.

## Reviewer status

This iteration is still under active development. The incomplete Policy boundary and unproven inherited profile selection are **handoff blockers**, even where package ID resolution and OVAL regression tests pass. RHEL 9 and Windows 11 readiness must be evaluated independently.
