# SCAP-NG schemas

**Status:** versioned pre-alpha native schemas and reviewed capability mappings.

The current frozen technical baseline is SCAP-NG **0.2.0** at `7cd8b1242d7fb4a2eb9b5f49c7ec3f48b2dd622d`.

## Current use

- `v0.2.0/` contains the current frozen schema set and capability mappings used for Board/content review.
- Earlier schema versions remain for compatibility/history and SHALL NOT be silently modified to match newer semantics.
- JSON Schema defines document structure. Runtime/evaluation semantics also live in the specification, capability mappings/reference docs, and focused conformance tests.
- Schema-valid does not imply migration-equivalent, collector-conformant, live-target-tested, or Board-approved.

## Human validation

Use:

```powershell
python tools/validate_native_json_schemas.py PATH_TO_CONTENT --schema-dir schema/v0.2.0
python tools/validate_native_semantics.py PATH_TO_CONTENT
```

For the full operator catalog, see [`tools/HUMAN-RUNNABLE-SCRIPTS.md`](../tools/HUMAN-RUNNABLE-SCRIPTS.md).

## Change discipline

Semantic schema changes require the human-review process in [`MAINTAINING.md`](../MAINTAINING.md). During the 0.2.0 review freeze, prefer small reproducer-backed fixes over broad redesign.
