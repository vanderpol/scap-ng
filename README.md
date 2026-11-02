# SCAP-NG

**Pre-alpha 0.4 specification and schema staging repository.**

This is the clean staging home for the next-generation Security Content
Automation Protocol (SCAP-NG) specification. It is **not yet the public
authoritative repository, an OVAL Board-approved standard, a released 0.4.0
distribution, or evidence of a working scanner**.

## Start here

- [Frozen 0.4 schema family](schema/v0.4.0/README.md) — the complete, versioned
  JSON Schema and capability metadata set.
- [Specification status](specification/README.md) — scope and limits of the
  current pre-alpha language contract.
- [Current authoring examples](examples/README.md) — representative real
  converted Assessments, with explicit qualification limits.
- [Source and freeze provenance](docs/PROVENANCE.md) — exact source commit,
  immutable JSON byte digest and permitted migration boundary.
- [Third-party source policy](docs/THIRD-PARTY.md) — provenance and license
  boundaries for mapping metadata and examples.

SCAP-NG separates **policy Rules** (what must be true) from **Assessments**
(how the requirement is tested). The 0.4 language uses direct capability
selectors, explicit collection/matching requirements, typed Input and Variable
contracts, and native Result structures. Versioned schemas and machine-readable
metadata are intended to be reusable by editors, producers, validators and
scanner implementations.

## Repositories

| Project | Responsibility |
| --- | --- |
| This staging repository | Specification and frozen versioned schemas |
| [SCAP-NG tools](https://github.com/vanderpol/scap-ng-tools) | Converter and shared authoring/normalization utilities (in migration) |
| [VS Code editor](https://github.com/vanderpol/scap-ng-vscode) | Interactive authoring UI |
| [Evidence](https://github.com/vanderpol/scap-ng-evidence) | Proof and release evidence |
| [Original development repository](https://github.com/vanderpol/scap-ng) | Historical research, tooling and source history until controlled cutover |

No historical release tags or artifacts have been moved. The editor and existing
toolchain still pin the original `schema/v0.4.0` location; this staging copy
retains that path and all frozen JSON bytes unchanged.

## Check the schema distribution

Run the Python standard-library integrity gate:

    python3 -m unittest discover -s tests -p 'test_schema_integrity.py' -v

The complete CI gate also validates Draft 2020-12 schemas and the curated
examples using the dependencies in `requirements-dev.txt`.

## License

Project-owned source in this repository is offered under
[Apache License 2.0](LICENSE). This does not relicense referenced SCAP 1.4/OVAL
sources, third-party standards, or converted source content. See the
[third-party policy](docs/THIRD-PARTY.md).

