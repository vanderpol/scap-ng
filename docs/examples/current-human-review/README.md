# Real SCAP-NG 0.4.0 authoring files — human-readable layout review

These **complete YAML documents** are byte-for-byte copies of two verified
native authoring Rule/Assessment pairs from the
[65-stream human-readable REVIEW library](https://github.com/vanderpol/scap-ng-evidence/releases/tag/v04-human-readable-review-20261030-ab5cddd).
They are directly browseable here for reviewers who cannot download the full ZIP.

| Original STIG | Rule | Assessment | What it demonstrates |
| --- | --- | --- | --- |
| RHEL 9 | [SV-257966 Rule](authoring/rhel_9/rules/SV-257966.rule.yaml) | [SV-257966 automated Assessment](authoring/rhel_9/assessments/automated/SV-257966.automated.yaml) | An inline `unix.sysctl` Object with an explicit value requirement |
| Windows 11 | [SV-253475 Rule](authoring/ms_windows_11/rules/SV-253475.rule.yaml) | [SV-253475 automated Assessment](authoring/ms_windows_11/assessments/automated/SV-253475.automated.yaml) | An inline `windows.registry` Object and explicit AND of value/type requirements |

Both original Rules are `CONVERTED_VERIFIED` in the pinned original-source
ledger. This is *independent static source/authoring proof*, not a live scanner
test or assertion of OVAL Board approval. Source-native IDs (including their
legacy generated suffixes) are deliberately unchanged; the **physical
filenames** now use original SV-IDs, with no randomly appended suffixes.
The Rule-to-Assessment connection resolves by logical `id`, not by filename.

These four files are **illustrative slices**, not a self-contained complete
Benchmark: use the full review ZIP's `authoring/<STIG>/benchmark.yaml`,
`applicability.yaml`, and remaining Rule/Assessment files for complete
reference-resolution and compilation.

The historic six-STIG examples and original normalized v1 archive remain
available for exact reproduction, but are not the recommended current author
navigation. See the [current downloads and sample index](../../releases/0.4.0-downloads-and-samples.md).
