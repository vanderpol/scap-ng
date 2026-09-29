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
