# Eleven fixed original-source validation cases

[Report and source citations](../../../docs/audit/v04-independent-validation-20261030.md).
`manifest.json` pins original archive revision, the frozen DRAFT hash, the prior
4,258-record proof-floor digest, fixture hashes and exact original-node closure
hashes. XML files are node-exact extracted OVAL closures with original generator
metadata, not complete signed originals. JSON files retain existing native
Assessment bodies/hashes and original full-component validation observations.
No source node was repaired and no native/program/status was rebased.

Run `python tools/audit_v04_bounded_source_validation.py --output NEW_REPORT.json`.
Add `--originals PINNED_ZIP_DIR` for full original-component XSD/Schematron replay
and every-node rejoin. Without that option the validation observations are
explicitly labeled retained. DISA/NIWC ownership follows OVAL node identifiers.
The sample is intentionally diagnostic, not a corpus yield estimate.
