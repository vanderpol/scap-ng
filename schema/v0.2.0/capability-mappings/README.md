# SCAP-NG 0.2.0 capability mappings

This directory is the human review entry point for the complete effective
SCAP-NG 0.2.0 capability catalog.

- **[supported/](supported/README.md)** — all 100 supported, non-deprecated
  OVAL 5.12.3-derived capabilities. Their canonical mapping JSON remains
  single-source under `schema/v0.1.0/capability-mappings/`, and each capability
  is linked individually from the supported catalog. Under a 0.2.0 Assessment,
  the generator and validator resolve them exclusively against 0.2.0 shared
  schema/result contracts.
- **[experimental/](experimental/README.md)** — retained 0.2.0 research mappings
  that are not part of the supported content-development baseline. This currently
  contains the four ESX drafts.
- **Kubernetes OVAL 6.0 Tests** — explicitly deferred for 0.2.0; no native
  capability mappings are present.

The machine-readable scope is
[`../capability-scope.json`](../capability-scope.json). The permanent
`tools/test_schema_v02_promotion.py` regression verifies the supported count,
the experimental inventory, schema-version isolation, and generation of every
supported inherited capability against 0.2.0 schema IDs.

Do not infer support from physical placement alone. A capability is supported
only when listed by the 0.2.0 scope contract and accepted by the versioned
registry/validation gates.
\n## Strict authoring versus legacy-converter bridge\n\nStrict 0.2.0 validation is the default and is the contract for newly authored\ncontent, including the Codex pilot. The historical SCAP 1.4 converter may retain\nits lossless aligned OVAL vocabulary for a supported mapping until that mapping\nis explicitly marked `native.post_alignment_ready`. The full-corpus conversion\ngate may opt into that narrow bridge explicitly; it does not make the aligned\nlegacy shape valid for new 0.2.0 authoring. Unknown capabilities still fail.\n