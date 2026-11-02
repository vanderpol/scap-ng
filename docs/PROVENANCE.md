# Frozen 0.4 staging import provenance

**Staging import: 2026-11-02. Not a release or name cutover.**

| Boundary | Exact reference |
| --- | --- |
| Original source repository | `vanderpol/scap-ng` |
| Owner-accepted schema candidate | `6efe0d053e79d513339f7999c52d214886b6d201` |
| Schema freeze merge commit | `1401c2851516e1af230231abe47a40419bca3dc1` |
| Source commit used for staging | `d12a644f4607cdc9c9ada50e3a96d4fd0060c6d9` (Apache-2.0 LICENSE added; frozen schema tree unchanged) |
| Schema source subtree | `schema/v0.4.0/` |
| Versioned JSON files | **143** |
| Root JSON Schema definitions | **34** |
| Root schema `$ref` occurrences | **242** |
| Immutable JSON aggregate SHA-256 | `476f5767276f5c2114f91b211cf4e159a75bee0806ea736fc631d9c40f4c4b80` |

The aggregate digest is SHA-256 over each JSON file, sorted by relative
POSIX path, by feeding `relative-path UTF-8 + NUL + exact file bytes`. It
protects the complete version-local JSON family, not only root schema files.
Every JSON file copied into staging is byte-for-byte identical to source.

The four Markdown navigation pages within the schema subtree were
**intentionally rewritten** for staging so outdated research, 0.3 drafts
and broken relative links do not appear as current normative guidance.
They are not included in the immutable JSON digest.

## Example source paths (bytes preserved)

- `docs/examples/conformance-remediation-20261101/windows-server-2025-shows-on-lock-screen-sv-278080-assessment.yaml`
- `docs/examples/conformance-remediation-20261101/windows-server-2025-control-permissions-sv-278139-assessment.yaml`
- `docs/examples/owner-contract-20261031/linux-home-mount-nosuid-assessment.yaml`
- `docs/examples/input-presence-20261101/optional-lock-screen.assessment.yaml`

## Explicitly not done

- No changes to the original `scap-ng` repository, schemas, releases, tags,
  CI, historical issues, source research or proof baselines.
- No compiler, converter, authoring normalizer, application runtime, scanner
  or independent collection proof imported.
- No 0.4.0 release, OVAL Board ratification, schema flattening, repository
  rename, privacy change or public URL cutover.
- Historical evidence remains tracked independently in the original and
  `scap-ng-evidence` repositories until a reviewed public-link migration.

