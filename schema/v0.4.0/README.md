# SCAP-NG pre-alpha 0.4 schema family

This directory contains the **owner-frozen 0.4 schema JSON set**, copied without
modification from the approved source commit. This is a language-contract freeze,
not release authorization or scanner conformance.

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

Consumers SHOULD pin to this exact versioned path. Do not mix historical 0.3
grammars, old converter drafts or newer research proposals with 0.4 documents.

The original source is retained in `vanderpol/scap-ng`; see
[provenance](../../docs/PROVENANCE.md) for the exact commit and JSON digest.

