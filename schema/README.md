# SCAP-NG pre-alpha 0.4 schema family

This directory contains the **owner-accepted 0.4 schema candidate**, physically
flattened for whole-repository release-tag versioning. The original owner-frozen
bytes remain recoverable at the prior Git commit. The owner approved a pre-release
0.4 amendment grouping Item counts into `require.item_requirement`. This is not
release authorization or scanner conformance.

- 143 JSON files, including 34 root `.schema.json` definitions and their
  version-local supporting metadata.
- 242 JSON Schema references across the 34 root definitions, resolved locally
  by the staging schema integrity gate.
- [Supported and experimental capability mappings](capability-mappings/README.md)
  retain distinct classification and original-source identity.
- `selector-api-contracts.json` records Windows selector case behavior and
  acquisition metadata.
- `authoring-vocabulary.en.json` and `editor-default-policy.json` supply
  version-scoped authoring/editor metadata, **not scanner-side hidden defaults**.
- [Generated structural reference](../docs/generated/schema-reference.md),
  [capability catalog](../docs/generated/capability-catalog.md) and
  [scanner documentation coverage](../docs/generated/scanner-implementation-catalog.md)
  are reproducible and audited by CI from the same release snapshot.

Consumers MUST pin the **whole repository** to a versioned release tag (once
published) or to an exact commit, not to a floating `main` branch. The JSON
`$id` identifiers remain explicitly versioned even though the files live in
flat `schema/`. Loading tools must register those identifiers against these
local files; no implicit web lookup or schema rewrite is required. Do not mix
0.3 or newer experimental language elements with 0.4 content.

For historical source lineage, some JSON metadata continues to
record the historical source path `schema/v0.4.0/`; this is source lineage,
**not a directory to load in this staging checkout**. The current files live
under `schema/` and no frozen JSON was rewritten during flattening.

The original research source is retained privately in `vanderpol/scap-ng-research`;
see [provenance](../docs/PROVENANCE.md) for the original and amended digests.
