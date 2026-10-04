# Version promotion and freeze requirements

Status: working normative project requirement

A SCAP-NG version SHALL NOT be described as authoring-frozen, content-ready, or
ready for external content delegation until the complete effective versioned
schema surface is present and machine-verifiable on `main`.

## Mainline integration gate

Accepted feature work SHALL be reachable from `main` before it contributes to
a freeze claim. A branch or pull request is not authoritative merely because its
tests passed. Before a freeze:

- every accepted feature head SHALL be an ancestor of, or patch-equivalent to,
  the candidate `main` commit;
- every branch ahead/diverged from `main` SHALL have an explicit disposition:
  merge, held/deferred, historical preservation, or retire;
- intentionally held/deferred work SHALL be excluded from the supported-version
  claim;
- the final validation runs SHALL identify `main` and the exact candidate SHA.

## Versioned schema-surface gate

A version SHALL expose a complete effective schema set for all document types it
claims to support. Unchanged contracts MAY be promoted from the previous version,
but the effective version SHALL NOT depend on silent validator fallback to an
older schema directory.

Capability mappings MAY remain single-source when semantics are unchanged. When
reused by a later version, generators and validators SHALL resolve those mappings
against the later version's shared schema/result contracts. A later-version
generated capability contract SHALL NOT contain references to an older schema
version unless that cross-version dependency is explicitly normative and tested.

Before freeze, an automated regression SHALL:

1. enumerate the required authoring schemas for the candidate version;
2. validate every schema as JSON Schema;
3. reject unintended references to older-version schema IDs;
4. generate every supported inherited capability against the candidate version;
5. deep-validate representative candidate-version Assessment content using an
   inherited capability;
6. verify candidate-version additions/deferred capabilities have explicit scope;
7. run focused feature tests and broad current-design, Self-Assertion and
   production-migration gates against the same `main` candidate SHA.

## Freeze terminology

A semantic checkpoint is not automatically an authoring-schema freeze. A freeze
record SHALL distinguish semantic stability, schema-surface completeness,
conformance evidence, migration evidence and live-target evidence. Failure of a
stronger gate SHALL reopen the corresponding freeze claim without erasing valid
evidence from weaker completed gates.

This requirement was added after the 2026-10-03 0.2.0 checkpoint exposed a gap:
the new 0.2.0 feature work was merged and regression-tested on `main`, but the
complete 0.2.0 authoring schema surface had not yet been promoted and inherited
capability generation still resolved shared schema IDs to v0.1.0.
