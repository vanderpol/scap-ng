# Draft 0.2.0 result-package integration

Provenance: Evidence/Audit of owner-authorized continuation; Common original
schemas, helper and synthetic test content. Working draft pending Board review.
0.1.0 remains unchanged; this is not a complete 0.2.0 release or scanner.

The draft Scan/Benchmark/Rule Result schemas connect policy-facing Rule instances
to Assessment execution IDs through an unsigned ZIP manifest. Logical IDs, never
filenames, bind references. Each Assessment invocation has one artifact, shared
by all its Rule/dependency references. Independent evaluation groups can contain
repeated Assessment identities with distinct execution IDs and target/binding
contexts. Dependency cycles, cross-context links and unreachable artifacts fail.

The closed manifest pins each member's exact UTF-8 JSON bytes, SHA-256 and size.
Verification rejects unlisted/missing members, duplicate IDs/paths, case-colliding
paths, traversal, symlinks, encrypted files and unsupported compression without
extracting files. Default bounds are 10,000 members and 64 MiB uncompressed;
API callers can set smaller or larger limits. Serialization is deterministic
within a runtime; compressed ZIP bytes are not promised identical across zlib
versions. Duplicate/nonfinite or lossy JSON values are rejected.

Verification checks result schemas, canonical Item/context/reference consistency,
materialization, Scan registries, target/run identities, Rule-selected Assessment
identity/version/mode, applicability execution purpose, dependency links and
Benchmark outcome counts. Resolved sources optionally add the existing
source-aware Assessment validation and expression-schedule replay. Policy Rule
aggregation, class-specific truth interpretation, scoring and source Benchmark
policy resolution are not recomputed by this slice. Technical true does not
universally imply policy pass. Reported elements remain a derived projection;
canonical Items and global redaction are separate.

`unsigned` is mandatory. A digest proves consistency with the included manifest,
not authenticity: an attacker can replace both bytes and hashes. Signature
profiles/trust, external auxiliary evidence members, source Benchmark replay,
real acquisition lineage and vendor target conformance remain downstream work.
Unbound evidence references are rejected rather than silently omitted.

See [the reproducible known result](../tests/result-package-0.2.0/README.md).
Run `PYTHONPATH=tools python tools/test_result_package_v02.py` for the focused
regressions, and the maintained current-regression workflow for integration.
