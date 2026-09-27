# Iteration 001 Source Layout

The authoring source is intentionally composed of small files. Aggregate policy or automation YAML files are **not** the source model.

## Combined-rule candidate

```text
combined-rule/<benchmark>/source/
  policy/
    benchmark.yaml
    profile.yaml
    provenance.yaml
    rules/
      <rule-id>.yaml
  automated/
    rules/
      <rule-id>.yaml
```

The `policy/rules` files represent what a policy-only publisher such as DISA could create.

The `automated/rules` files represent the candidate combined form. Each automated rule repeats the policy fields and contains its assessment inline. The manual-only rule has no assessment.

## Split policy / assessment / binding candidate

```text
split-policy-assessment-binding/<benchmark>/source/
  policy/
    benchmark.yaml
    profile.yaml
    provenance.yaml
    rules/
      <rule-id>.yaml
  automation/
    benchmark.yaml
    bindings.yaml
    assessments/
      <benchmark-specific-assessment>.yaml

split-policy-assessment-binding/shared-assessments/
  windows/
    <reusable-assessment>.yaml
```

Policy-only publication uses only the `policy/` tree.

Automated publication resolves each binding, including shared assessment references, into one self-contained signed `.scapng` bundle.

## Why the ZIP does not mirror the repository exactly

The repository is optimized for authoring, review, provenance, and reuse. The redistributable package is optimized for deterministic scanner ingestion.

The build step converts YAML source to canonical JSON members, resolves all assessment dependencies, generates a manifest with hashes, and signs that manifest.
