# SCAP-NG schemas

**Status:** versioned pre-alpha native schemas and reviewed capability mappings.

SCAP-NG **0.3.0** is the active pre-alpha schema and the next OVAL Board review target. SCAP-NG 0.2.0 is frozen historical reference only.

## Current use

- `v0.3.0/` is the active, complete, independent schema tree for the forthcoming Board checkpoint.
- `v0.2.0/` is the frozen earlier checkpoint and is no longer an active review target.
- Earlier schema versions remain for compatibility/history and SHALL NOT be silently modified to match newer semantics.
- JSON Schema defines document structure. Runtime/evaluation semantics also live in the specification, capability mappings/reference docs, and focused conformance tests.
- Schema-valid does not imply migration-equivalent, collector-conformant, live-target-tested, or Board-approved.

## Human validation

Use:

```powershell
python tools/validate_native_json_schemas.py PATH_TO_CONTENT --schema-dir schema/v0.3.0
python tools/validate_native_semantics.py PATH_TO_CONTENT
```

For the full operator catalog, see [`tools/HUMAN-RUNNABLE-SCRIPTS.md`](../tools/HUMAN-RUNNABLE-SCRIPTS.md).

## Change discipline

Semantic schema changes require the human-review process in [`MAINTAINING.md`](../MAINTAINING.md). Do not add 0.3.0 features to the frozen 0.2.0 tree. New semantic changes belong in `v0.3.0/` with focused reproducer-backed tests and human review.
