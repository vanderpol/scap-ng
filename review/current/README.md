# Current SCAP-NG 0.4.0 owner review

**Status (October 30, 2026):** current **pre-alpha native authoring review**, not a final scanner release, certification, signed publisher package or OVAL Board ratification. The current published source is the full 65-stream DRAFT plus its normalized editable YAML review library; older six-STIG sample runs remain pinned historical checkpoints.

## Start with the current native source

**[0.4 downloads and Assessment samples — start here](../../docs/releases/0.4.0-downloads-and-samples.md)** · [normalized editable all-65 YAML review ZIP and toolchain](https://github.com/vanderpol/scap-ng-evidence/tree/v04-normalized-library-review-20261030-ff69d46b3/runs/v04-library/2026-10-30-all65-normalized-review-ff69d46b3) · [full 65-stream original-source DRAFT](https://github.com/vanderpol/scap-ng-evidence/tree/v04-revised-all65-draft-files-20261030-a08c9beb9/runs/v04-converter/2026-10-30-all-65-revised-draft-download).

The source accounting covers **65 streams /8,892 original Rules**. The normalized review holds **60 editable native Benchmarks and 6,817 compiled candidate Assessments** (4,258 independently statically source-proved; 2,559 explicitly UNVERIFIED); **422 blocked automated and 1,653 manual/OCIL** records remain visible, without fabricated native Assessments. Five original-only streams have no editable native Benchmark. The 13,754 YAML files are byte-identical to the revised DRAFT and the original source/proof ledger is retained. The [normalization CLI contract](../../docs/developer/NATIVE-LIBRARY.md) serves authoring tools without declaring runtime scanner equivalence.

## Earlier six-STIG authoring review (historical checkpoint)

[October 22 six-STIG YAML/JSON downloads](../../docs/releases/0.4.0-six-stig-authoring.md) supersede the original [October 20 six-STIG authoring release](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020) for reproduction of that smaller sample. The October 20 sample had **4,001 source documents, 1,375 Tests and 2,958 Rule-choice links**; those are **not** the current all-65 library counts. The original source and per-Benchmark version-declaration changes remain auditable.

## How to review the Assessment model

Start with the [small real 0.4 direct-converter examples](../../docs/examples/README.md), [Benchmark/Rule orientation](../../specification/examples/README.md) and [Assessment syntax illustrations](../../specification/examples/assessments.md). The [short six-STIG review guide](REVIEW-GUIDE.md) and [RHEL 9](examples/rhel9-full.md)/[Windows 11](examples/windows11-full.md) entry points describe their **pinned earlier file layout**, not the normalized `content/` paths.

The [OVAL Boolean-operator versus quantifier review](0.4.0-BOOLEAN-OPERATORS-VS-QUANTIFIERS.md) and [field requirement scope discussion](0.4.0-FIELD-REQUIREMENT-SCOPE.md) preserve dated source-backed questions and may use pre-canonical spellings. Do not treat proposed wording or older review counts as the current 0.4 schema; use a coherent exact source/schema/toolchain pin.

The [historical release gate tracker](0.4.0-FINALIZATION-GATES.md), [candidate operator guide](../../docs/releases/0.4.0-rc.md) and [#260 decision packet](https://github.com/vanderpol/scap-ng/issues/260) distinguish schema validity, compilation, static source proofs, runtime scanner behavior and publisher trust. **No native conversion or proof status implies a live scanner PASS.**

Older 0.3 source/examples/bundles remain in the [0.3.0 archive](../../archive/0.3.0/README.md); A/B/C/D review labels are historical research variants, not separate SCAP-NG releases.
