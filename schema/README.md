# SCAP-NG schemas

**Status:** versioned pre-alpha native schemas and capability mappings.

- [v0.4.0](v0.4.0/README.md) is the **current owner-approved pre-alpha authoring-sample schema**, not an OVAL Board standard, compiled bundle or scanner conformance result. [Six-STIG source samples](https://github.com/vanderpol/scap-ng/releases/tag/v0.4.0-six-stig-authoring-approved-20261020).
- [v0.3.0](v0.3.0/README.md) is the **archived previous version**. Its original schema, authoring and historical compiled demonstrations are [preserved](../archive/0.3.0/README.md).
- [v0.2.0](v0.2.0/README.md) and earlier versions are historical snapshots.

Every versioned directory must be physically self-contained: schemas, mappings and support data are version-local, with explicit version metadata and last substantive modification dates. JSON Schema validation does not establish migration equivalence, evaluation semantics, collector support or Board approval.

## Archived 0.3 validation (for historical reproduction)

```powershell
python tools/validate_native_json_schemas.py PATH_TO_CONTENT --schema-dir schema/v0.3.0
python tools/validate_native_semantics.py PATH_TO_CONTENT
```

## Current 0.4 schema validation

```powershell
python tools/test_v04_schema_draft.py
```

Current 0.4 source-schema checks, rejection fixtures and all 4,001 generated authoring documents were verified in both formats by the [0.4 six-STIG workflow](https://github.com/vanderpol/scap-ng/actions/runs/39472747469). This **does not** establish signed native .scapng compilation or scanner parity.

## Change discipline

Semantic changes follow [MAINTAINING.md](../MAINTAINING.md): evidence, source-backed examples, focused negative tests and explicit human approval before promotion. The [0.4 scope and release gates](../research/assessment-simplification/compact-authoring-04/0.4-SCOPE-AND-RELEASE-GATES.md) separate schema drafting, six-valued reference-model proof, six-anchor integration, full corpus release gates, and later scanner conformance.
