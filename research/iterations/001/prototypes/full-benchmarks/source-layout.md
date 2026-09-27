# Iteration 001 Source Layout

The authoring source is intentionally composed of small files. Aggregate policy or automation YAML files are **not** the source model.

## Combined-rule candidate

Linux currently demonstrates the direct combined form:

```text
combined-rule/linux/source/
  policy/
    benchmark.yaml
    profile.yaml
    provenance.yaml
    rules/<rule-id>.yaml
  automated/
    rules/<rule-id>.yaml
```

The Windows Client and Windows Server prototypes additionally demonstrate **shared combined rules with STIG-specific overlays**:

```text
combined-rule/
  shared-rules/
    windows/
      password-policy-by-role.yaml
      platform-security-posture.yaml
      defender-realtime.yaml
      remote-registry-disabled.yaml
      trusted-publisher-store.yaml

  windows-client/source/
    policy/
      rules/<rule-id>.yaml
    automated/
      overlays/<rule-id>.yaml
      rules/<benchmark-specific-rule-id>.yaml

  windows-server/source/
    policy/
      rules/<rule-id>.yaml
    automated/
      overlays/<rule-id>.yaml
      rules/<benchmark-specific-rule-id>.yaml
```

A shared combined rule contains reusable rule semantics and its automated assessment. A STIG-specific overlay may provide a different rule ID, title, references, discussion, Check/Fix text, and approved assessment parameter values.

The build resolves the shared rule plus overlay into an ordinary complete rule and verifies that the resolved policy portion exactly matches the corresponding policy-only rule. Overlay inheritance is therefore a source/build mechanism; scanners consume only resolved rules.

An overlay must not directly patch the assessment expression/collector tree. Reusable automation changes belong in a new version of the shared rule. Parameter values may be supplied only through the shared rule's declared parameter schema.

## Split policy / assessment / binding candidate

```text
split-policy-assessment-binding/<benchmark>/source/
  policy/
    benchmark.yaml
    profile.yaml
    provenance.yaml
    rules/<rule-id>.yaml
  automation/
    benchmark.yaml
    bindings.yaml
    assessments/<benchmark-specific-assessment>.yaml

split-policy-assessment-binding/shared-assessments/
  windows/<reusable-assessment>.yaml
```

Policy-only publication uses only the `policy/` tree. Automated publication resolves bindings and shared assessment dependencies into one self-contained signed `.scapng` package.

## Why the ZIP does not mirror the repository exactly

The repository is optimized for authoring, review, provenance, and reuse. The redistributable package is optimized for deterministic scanner ingestion.

The build step converts YAML source to canonical JSON members, resolves shared rules/overlays or assessment bindings, validates closure and policy equivalence, generates a manifest with hashes, and signs that manifest.
