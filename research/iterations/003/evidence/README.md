# Iteration 003 Conversion Evidence

This directory contains migration and equivalence evidence, not native
SCAP-NG source.

Appropriate contents include:

- source artifact hashes;
- provenance ledgers;
- legacy source IDs and component linkage;
- conversion diagnostics;
- semantic accounting;
- equivalence reports;
- unsupported/deferred construct reports;
- regression evidence.

Legacy XCCDF/OVAL/OCIL/CPE identifiers and namespaces may appear here when
needed for traceability.


## Current OVAL compatibility evidence

See [oval-roundtrip-compatibility.md](oval-roundtrip-compatibility.md) for the
current SCAP 1.4 OVAL → native SCAP-NG v003 → OVAL regression evidence,
including Self-Assertion, RHEL 10 singles and aggregate, RHEL 9, Oracle Linux 9,
Windows 11, intentional `extend_definition` dereferencing, and structural-diff
classification.
