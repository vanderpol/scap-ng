# SCAP-NG 0.4 schemas

This directory contains the **pre-release 0.4 schema candidate** and its supporting metadata. It defines document structure, not whether a scanner implements a capability or whether a target complies.

## What is here

- **35 root JSON Schemas**, with supporting metadata (145 JSON files total).
- [Capability mappings](capability-mappings/README.md) — supported and experimental capabilities.
- `selector-api-contracts.json` — selector and acquisition contracts.
- `native-selector-contracts.json` — reviewed capability-specific native selector inputs; `native-selector.schema.json` is the deterministic generated overlay consumed by the canonical Assessment schema.
- `authoring-vocabulary.en.json` and `editor-default-policy.json` — authoring and editor guidance, **not implicit scanner defaults**.

For readable descriptions, use the generated [schema reference](../docs/generated/schema-reference.md), [capability catalog](../docs/generated/capability-catalog.md) and [scanner coverage notes](../docs/generated/scanner-implementation-catalog.md).

## Using the schemas

Pin the **entire repository** to an exact commit until a 0.4 release tag exists. The files live in flat `schema/`, but retain versioned JSON `$id` identifiers. Schema loaders must resolve those identifiers to local files, not fetch them from the web.

The owner-approved pre-release amendment groups Item requirements under `require.item_requirement`. Do not mix earlier 0.3 syntax with this candidate.

See [provenance](../docs/PROVENANCE.md) for exact source commits, original and amended schema hashes, and migration details. **0.4.0 is not released or OVAL Board-approved.**

## Capability-specific selector overlay

Run `python tools/generate_native_selector_schema.py --check` to verify the generated native selector pack and the complete supported-selector audit. The overlay currently closes `windows.registry` (`hive`, `key`, `name`) and `linux.partition.mount_point`; all other supported selectors are inventoried as unresolved rather than receiving inferred restrictions.
