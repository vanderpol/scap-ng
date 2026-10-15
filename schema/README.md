# SCAP-NG schemas

**Status:** versioned pre-alpha native schemas and capability mappings.

- [v0.4.0](v0.4.0/README.md) is the **working one-grammar draft**. It is not the accepted specification, a Board checkpoint, or vendor/scanner conformance evidence. See [#227](https://github.com/vanderpol/scap-ng/issues/227).
- [v0.3.0](v0.3.0/README.md) remains the active pre-alpha baseline and current Board review target. Existing 0.3 content, documentation and releases remain unchanged.
- [v0.2.0](v0.2.0/README.md) and earlier versions are historical snapshots.

Every versioned directory must be physically self-contained: schemas, mappings and support data are version-local, with explicit version metadata and last substantive modification dates. JSON Schema validation does not establish migration equivalence, evaluation semantics, collector support or Board approval.

## Current 0.3 validation

```powershell
python tools/validate_native_json_schemas.py PATH_TO_CONTENT --schema-dir schema/v0.3.0
python tools/validate_native_semantics.py PATH_TO_CONTENT
```

## Focused 0.4 schema draft validation

```powershell
python tools/test_v04_schema_draft.py
```

This test checks version-local identity, initial Test/State/record and Set filter grammar, and positive/negative fixtures. It does **not** assert that the existing 0.3 validator, converter, normalizer, or .scapng compiler supports 0.4.

## Change discipline

Semantic changes follow [MAINTAINING.md](../MAINTAINING.md): evidence, source-backed examples, focused negative tests and explicit human approval before promotion. The [0.4 scope and release gates](../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md) separate schema drafting, six-valued reference-model proof, six-anchor integration, full corpus release gates, and later scanner conformance.
