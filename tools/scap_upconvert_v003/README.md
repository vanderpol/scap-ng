# Current local conversion for SCAP-NG review

Use `convert_full_review.py` with a pinned original SCAP 1.4 ZIP. For the full operator catalog, see [`../HUMAN-RUNNABLE-SCRIPTS.md`](../HUMAN-RUNNABLE-SCRIPTS.md). The original `run_local.py` section below is retained only for historical reproduction.

From the repository root, using Python 3.12:

```powershell
python -m pip install PyYAML==6.0.3 lxml==6.1.1
python tools/scap_upconvert_v003/convert_full_review.py --input "PATH_TO_PINNED_SCAP.zip" --sha256 "EXPECTED_SHA256" --output work/review --schema third_party/scap-1.4-schemas/omni-schema.xsd
```

Replace the two input placeholders with the package path and independently recorded checksum. `work/review` is a short local output path. This source/design review command does not publish or modify the original package. Read the emitted evidence, source warnings/exclusions and validation results before accepting the output.

[RHEL 9 full guide](../../docs/rhel9-review.md) · [Windows 11 guide](../../research/iterations/003/review/windows11-current-full/README.md) · [Converter delivery requirements](../../research/iterations/003/design/converter-stability-and-windows.md).

Structural validation can be repeated with:

```powershell
python -m pip install jsonschema
python tools/validate_native_json_schemas.py work/review --schema-dir schema/v0.2.0 --report work/schema-validation.json
```

This is the maintained local full-review conversion command for the frozen 0.2.0 review phase. It is not proof of target-runtime equivalence; unsupported or unresolved source semantics must remain explicit.

## Preserved historical instructions

The following section is retained verbatim as historical reproduction documentation. Its output paths and package mode SHALL NOT be used as the current handoff baseline.

# SCAP-NG v003 local conversion tools

The v003 conversion tooling can be run directly from a local checkout. GitHub
Actions remains the reproducibility/CI path, but is not required for normal
development runs.

## Requirements

- Python 3.12 or later
- PyYAML
- Internet access for source retrieval unless the converter is later pointed at
  a local source package

Install the current dependency:

    python -m pip install pyyaml

## RHEL 9

Run the complete RHEL 9 conversion:

    python tools/scap_upconvert_v003/run_local.py rhel9

Run only the six-Rule review slice:

    python tools/scap_upconvert_v003/run_local.py rhel9 --mode slice

Return a nonzero exit status when ERROR diagnostics remain:

    python tools/scap_upconvert_v003/run_local.py rhel9 --fail-on-error

The local runner performs the same important post-generation gates used by the
v003 CI workflow:

1. native-output cleanliness;
2. package manifest object resolution;
3. package member SHA-256 and size verification;
4. Benchmark Rule resolution;
5. applicability catalog and Assessment resolution;
6. diagnostic summary.

Full RHEL 9 output is written under:

    research/iterations/003/source/split-rule-assessment/rhel9-full/
    research/iterations/003/evidence/rhel9-full/
    research/iterations/003/packages/rhel9-full.scap-ng.zip
    research/iterations/003/packages/rhel9-full.manifest.json

## Windows

The local runner is intentionally structured so additional targets use the same
entry point. Windows 11 will be added as a target when its v003 native converter
is wired to the current Rule/Assessment/package model.

## Development behavior

By default the local runner completes successfully when isolated conversion
ERROR diagnostics exist, because the diagnostics inventory is itself useful
during converter development.

Use `--fail-on-error` when local behavior should match the CI quality gate.

FATAL generation or validation failures always stop the run.
