# Pinned new-Test metadata reference

These two ESX XSDs are exact Git blobs from OVAL-Community/OVAL tag `v6.0`,
commit `5afcf590fb5d334687bfdc47f98716424cdb7f3d`. [Source pins](source-pins.json)
record upstream paths and SHA-256 digests. The upstream License/Disclaimer is
retained inside each file without modification.

This is a partial metadata snapshot for native new-Test mapping generation,
not an independently compilable OVAL schema bundle, an embedded OVAL runtime,
or OVAL 6.0 ingestion support. Imports are deliberately not vendored here.
The maintained audit compiles against the complete pinned public checkout in
CI. Existing 5.12.3 source schemas and native mappings remain unchanged.

Only newly added Tests and their associated contracts are in scope. Existing
6.0 language/result/namespace differences do not supersede later 5.12.3 fixes.
See [the inventory](../../docs/audit/capability-coverage-2026-10-03/README.md).
