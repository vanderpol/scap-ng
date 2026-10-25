# Fixed Windows batch source/package fixtures

These 24 immutable-source dependency extractions correspond exactly to the
manifest committed before comparison. Each includes the original complete OVAL
closure, exact packaged Assessment and compiled program, original SCAP ZIP/XML
provenance, member hashes and the attempted outcome. Seven outcomes intentionally
remain unverified; passing classification tests does not promote those graphs.

The full original signed SCAP files remain unchanged. These minimal OVAL
extractions omit the original generator and are not standalone XSD-conformant
OVAL documents or newly generated conversions. Node fingerprints are checked
against their full-source closure records. Fixture bytes and native/program/source
hashes are listed in the engineering fixture inventory.

Regenerate explicitly with `audit_v04_proof_expansion.py --fixtures-dir` using
the same original ZIPs and reviewed native bundles. No converter or scanner runs.
See the [engineering report](../../../docs/audit/v04-proof-expansion.md) for
commands, pins, proof limits, all outcomes and remaining obligations.
