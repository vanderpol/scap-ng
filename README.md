# SCAP-NG

**Pre-alpha 0.4 — specification, schemas and examples.**

SCAP-NG is a pre-alpha successor to SCAP 1.4 designed to preserve supported assessment meaning while simplifying authoring, review, collection, results and scalable distribution.

This repository provides the current schema candidate, a small set of readable examples and supporting specification material.

**Status:** SCAP-NG 0.4.0 has not been released or approved by the OVAL Board. Schema-valid content does not establish scanner support or compliance.

## Start here

1. [Examples](examples/README.md) — four curated Assessments, from simple Registry checks to complex examples.
2. [Schema](schema/README.md) — the authoritative machine-readable 0.4 structure and metadata.
3. [Specification](specification/README.md) — current status and outstanding semantic documentation.
4. [Reference](docs/generated/schema-reference.md) and [capabilities](docs/generated/capability-catalog.md) — generated from the schema.

## More content and tools

- [VS Code authoring editor](https://github.com/vanderpol/scap-ng-vscode)
- [Conversion and authoring tools](https://github.com/vanderpol/scap-ng-tools)
- [Scanner implementation reference](docs/generated/scanner-implementation-catalog.md)

## Validation and provenance

Converted content represented as current native authoring must pass the shared [Tools publication admission gate](https://github.com/vanderpol/scap-ng-tools/pull/41). This repository's schema/documentation checks do not qualify a converted corpus or establish scanner equivalence. CI rejects publication sinks that bypass the shared boundary. Final deployment verification and administrative inspection limits remain tracked in [Tools #40](https://github.com/vanderpol/scap-ng-tools/issues/40).

The versioned 0.4 schema files are in flat `schema/`. Pin the **whole repository** to an exact commit until a release tag exists.

Run the baseline integrity tests:

```sh
python3 -m unittest discover -s tests -p 'test_schema_integrity.py' -v
```

For exact schema hashes, source history and example origins, see [provenance](docs/PROVENANCE.md). Generated references are checked for drift in CI; changes to their metadata require regenerating them with `python3 tools/generate_docs.py`.

## License

Project-owned source is licensed under [Apache-2.0](LICENSE). Referenced SCAP/OVAL materials and converted third-party content retain their respective rights; see [third-party notices](docs/THIRD-PARTY.md).
