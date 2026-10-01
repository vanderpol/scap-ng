# Capability Schema Mapping Sources

These files are the maintained, reviewed inputs for generated deep SCAP-NG
Assessment capability schemas.

They are **not** generated JSON Schemas themselves.

## Ownership model

For each supported capability:

1. A mapping file identifies the pinned OVAL 5.12.3 source Test/Object/State
   family and the intended native capability identity.
2. `tools/generate_capability_schema.py` extracts source-backed structural
   details from the pinned XSD.
3. Cross-field or context-sensitive OVAL Schematron behavior that JSON Schema
   cannot express safely is retained explicitly as semantic-validator rules.
4. Generated capability schema fragments are disposable build artifacts. They
   SHALL be regenerated from the mapping + pinned source rather than hand-edited.
5. A capability is not considered covered merely because a generated JSON
   Schema exists; semantic-validator fixtures and corpus validation are also
   required.

## Review rules

A mapping change SHOULD explain whether it:

- preserves an OVAL semantic construct directly;
- intentionally simplifies or replaces a legacy construct;
- moves a constraint from JSON Schema to semantic validation;
- excludes a deprecated/unsupported feature;
- changes native terminology or structure.

Any removal or simplification of a legacy construct SHALL also be represented
in `specification/migration/legacy-feature-disposition.md` when applicable.

## First vertical slice

`unix.file.json` is the first vertical slice. It is intentionally limited to
proving the generator architecture before scaling across the OVAL capability
catalog.

The slice currently covers:

- Test/Object/State family identity;
- Object selector alternatives (`filepath` vs `path` + `filename`);
- FileBehaviors defaults and enumerations;
- State field inventory and source datatype hints;
- Test result-control vocabularies;
- Schematron-derived semantic-validator obligations.

Shared operation legality, Variable binding legality, quantifier semantics and
other cross-capability entity rules belong in reusable common schemas/semantic
validation rather than being duplicated in every capability fragment.
