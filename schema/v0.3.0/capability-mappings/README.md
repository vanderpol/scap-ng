# SCAP-NG 0.3.0 capability mappings

This directory is the human review entry point for the complete effective
SCAP-NG 0.3.0 capability catalog.

- **[supported/](supported/README.md)** — all supported, non-deprecated OVAL 5.12.3-derived capabilities for this version. The canonical 0.3.0 mapping JSON is version-local under `schema/v0.3.0/capability-mappings/supported/`; 0.3.0 does not resolve normative mappings from v0.1.0. Each mapping retains exact OVAL source Test/Object/State identity as durable provenance while the native capability name may intentionally differ.
- **[experimental/](experimental/README.md)** — retained 0.3.0 research mappings
  that are not part of the supported content-development baseline. This currently
  contains the four ESX drafts.
- **Kubernetes OVAL 6.0 Tests** — explicitly deferred for 0.3.0; no native
  capability mappings are present.

The machine-readable scope is
[`../capability-scope.json`](../capability-scope.json). The permanent
`tools/test_schema_v02_promotion.py` regression verifies the supported count,
the experimental inventory, schema-version isolation, and generation of every
supported inherited capability against 0.3.0 schema IDs.

Do not infer support from physical placement alone. A capability is supported
only when listed by the 0.3.0 scope contract and accepted by the versioned
registry/validation gates.
\n## Strict authoring versus legacy-converter bridge\n\nStrict 0.3.0 validation is the default and is the contract for newly authored\ncontent, including the Codex pilot. The historical SCAP 1.4 converter may retain\nits lossless aligned OVAL vocabulary for a supported mapping until that mapping\nis explicitly marked `native.post_alignment_ready`. The full-corpus conversion\ngate may opt into that narrow bridge explicitly; it does not make the aligned\nlegacy shape valid for new 0.3.0 authoring. Unknown capabilities still fail. Publisher/private extensions that are not part of official SCAP 1.4/OVAL vocabulary are **conversion blockers** and SHALL NOT be preserved through the migration bridge or promoted implicitly into SCAP-NG. If equivalent functionality is desired, it requires a separate reviewed native capability proposal rather than lossless SCAP 1.4 conversion.\n
## Native naming and historical OVAL suffixes

Historical OVAL numeric suffixes (for example `54`, `55`, `57`, `58`, `511`, and `512`) identify the OVAL revision in which a revised Test family was introduced; they are not automatically part of the native SCAP-NG semantic name.

A reviewed native capability MAY use a clearer semantic name when the mapping proves equivalence and preserves the exact source identity in its durable `source` and `migration_crosswalk` metadata. The established example is `windows:wmi57_test` -> `windows.wmi.query`.

Importers SHALL NOT simply strip a numeric suffix when doing so would make a revised Test appear interchangeable with an older/deprecated predecessor. Version-suffixed capability names that have not yet received an explicit semantic rename remain unchanged for 0.3.0. Codex content work SHALL use the names defined by the versioned mappings and SHALL NOT invent or normalize capability names independently.
