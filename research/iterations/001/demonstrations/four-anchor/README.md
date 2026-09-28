# Four-Anchor SCAP-NG Content Development Demonstration

This directory is intended to be read like a hypothetical SCAP-NG content
development repository, not merely as generated test evidence.

It demonstrates how published SCAP 1.4 content can move through:

    published SCAP 1.4 source
      -> faithful semantic conversion
      -> reviewable SCAP-NG authoring source
      -> cross-benchmark mapping/reuse
      -> resolved/validated source
      -> deterministic distribution package

## Benchmarks

The demonstration uses four published NIWC/DISA anchors:

- `rhel9`
- `oracle-linux9`
- `windows11`
- `windows-server-2025`

Each benchmark is generated from the pinned source revision documented by the
iteration-001 public corpus manifest.

## Benchmark directory layout

Each benchmark directory is generated with this general structure:

    <benchmark>/
      source/
        combined-rule/
          benchmark.yaml
          rules/
          ...
        split-policy-assessment-binding/
          benchmark.yaml
          policy/rules/
          automation/assessments/
          automation/bindings.yaml
          ...
        ansible-inspired/
          benchmark.yaml
          policy/rules/
          automation/assessments/
          automation/bindings.yaml
          ...
        canonical-benchmark.json
        conversion-summary.json
        conversion-blockers.json

      distribution/
        package-metrics.json
        manifests/
        signatures/

The complete YAML under `source/` is intentionally committed. A reviewer
should be able to inspect any rule, assessment, binding, or overlay directly
in Git and see normal line-by-line history and diffs.

The `.scapng` ZIP packages themselves remain CI/release artifacts because
they are deterministic binary distributions rather than authoring source.
Their manifests and prototype signature metadata are committed under
`distribution/` so package composition is still reviewable in Git.

## Shared reuse and benchmark mapping

Cross-benchmark evidence is maintained under:

    shared-reuse/
      assessment-reuse.json
      reuse-views/
      ...

Rule alignment uses either:

1. identical normalized XCCDF Check Text; or
2. equivalent complete normalized OVAL assessment semantics.

Equivalent OVAL semantics is also evidence for exact automation reuse.

Measured exact reuse is rendered using all three candidate authoring designs:

- combined shared technical rule + policy overlays;
- split shared assessment + bindings;
- Ansible-inspired shared assessment + bindings.

This makes reuse mechanics visible rather than merely reporting overlap
statistics.

## What belongs in Git

Commit:

- policy/rule YAML;
- assessment YAML;
- mappings/bindings;
- overlays;
- applicability/profile/value source;
- migration/blocker diagnostics;
- reuse mappings;
- package manifests;
- schema/spec references needed to understand the source;
- human-readable methodology and provenance.

Keep as build artifacts:

- temporary split datastream trees;
- parser caches;
- duplicated intermediate IR not useful for normal review;
- final ZIP/`.scapng` binary packages when the same package is reproducible
  from committed source.

## Relationship to the future up-conversion tool

The current research scripts generate this tree. The long-term plan is to
extract their reusable logic into the open-source converter described in:

    research/iterations/001/upconversion-tool-roadmap.md

A future content developer should be able to run one conversion command,
review the generated/updated YAML in Git, edit or remediate source where
required, validate it, and build the same distribution package in CI or
locally.


## Suggested variable-semantics review cases

These Windows 11 rules are useful starting points for reviewing how faithful
OVAL variable/function semantics currently lower into SCAP-NG and for discussing
whether the future specification can express the same behavior more directly.

- `SV-253363r971535` — OVAL `merge` over a registry multi-string
  `object_component` (SSL/ECC curve ordering). This is a compact example of
  target-collected values feeding a local variable expression.
- `SV-253340r958434`, `SV-253341r958434`, and
  `SV-253342r958434` — OVAL `concat` expressions with target-dependent
  variable/object inputs.
- `SV-253401r1210296` — another target-dependent `concat` case useful for
  comparing the canonical graph with the Ansible-inspired ordered-step view.
- `SV-253435r991589` and `SV-253436r991589` — smaller `concat` cases
  suitable for side-by-side source-format review.

For each rule, compare:

    windows11/source/combined-rule/rules/<rule-id>.yaml

with:

    windows11/source/split-policy-assessment-binding/
      policy/rules/<rule-id>.yaml
      automation/assessments/ng.scap14.<rule-id>.yaml

and:

    windows11/source/ansible-inspired/
      policy/rules/<rule-id>.yaml
      automation/assessments/ng.scap14.<rule-id>.yaml

The original faithful OVAL semantic IR remains available under:

    research/iterations/001/generated/niwc-rule-splits/windows11/rules/<rule-id>/
      oval.xml
      oval-ir.json
      provenance.json

This gives a direct lineage from the SCAP 1.4 OVAL source, through the semantic
IR, into each candidate NG authoring form.
