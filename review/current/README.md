# Current SCAP-NG 0.4.0 owner review

**Status: current 0.4.0 pre-alpha authoring samples; not a final scanner release, certification, or OVAL Board ratification.** The authoring-language decision and its rationale are documented separately.

## Start with the actual six-STIG source

**[0.4.0 sample release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020)** · [YAML authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.yaml.zip) · [JSON authoring ZIP](https://github.com/vanderpol/scap-ng/releases/download/v0.4.0-six-stig-authoring-approved-20261020/scap-ng-0.4.0-six-stigs.json.zip)

This covers RHEL 9, Oracle Linux 9, Windows 11, Windows Server 2025, Windows Server DNS and Apache 2.4 UNIX; **4,001 authoring documents, 1,375 distinct Tests and 2,958 Rule-choice links**. All six Benchmark Assessment-specification declarations were updated from 0.3.0 to the exact referenced 0.4.0 specification under the owner's approved policy. The original source and precise per-Benchmark changes remain auditable.

## What to read

Begin with the [short review guide](REVIEW-GUIDE.md), then [Benchmark/Rule examples](../../specification/examples/README.md) and [Assessment examples](../../specification/examples/assessments.md). [RHEL 9](examples/rhel9-full.md) and [Windows 11](examples/windows11-full.md) provide entry points to the complete version-pinned files.

The [release gate tracker](0.4.0-FINALIZATION-GATES.md) distinguishes parsed source, semantic-model tests, native compilation, signing, and scanner equivalence. **4,001 files passing schema and static dependency checks do not prove scanner execution.** The 172 uncommon source-preserving requirements and independent native scanner/compiler work remain unresolved.

Older 0.3 examples and historical compiled bundles are available from the [archived 0.3.0 index](../../archive/0.3.0/README.md). The old A/B/C/D comparison labels are historical research variants, not product versions.
