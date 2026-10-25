# Exact original-source/package proof fixtures

These eight fixtures contain the complete original OVAL dependency closure
selected from checksum-pinned NIWC SCAP 1.4 ZIPs, the exact packaged native
Assessment and compiled program, and original-source/package provenance.
They are minimal dependency extractions, **not newly converted OVAL** or complete
standalone XSD-conformant OVAL documents (the original generator is omitted).
Original signed ZIPs remain unchanged outside the repository and are identified
by immutable revision, path and SHA-256 in every fixture's provenance.

`test_v04_source_package_semantics.py` checks each extracted node fingerprint and
native member digest against that provenance before comparison. The live audit
reads the full pinned original SCAP, resolves the XCCDF check through its catalog
and follows all original Definition/Test/Object/State/Variable references.

Regenerate all eight explicitly with the documented audit CLI and
`--fixtures-dir tests/fixtures/v04-source-package-pilot`. This invokes no
converter or scanner. Keep the four unsupported outcomes visible; do not replace
them with easier cases or treat the Oracle archive exception as source proof.

See the [engineering report](../../../docs/audit/v04-eight-assessment-pilot.md)
for exact pins, commands, current proof coverage and limitations.
