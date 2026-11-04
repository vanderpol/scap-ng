# SCAP-NG 0.4 provenance

This page records **which schema and examples were imported, what changed before release, and what has not been proved**. For authoring guidance, start with the [specification](../specification/README.md); for the four small examples, see [examples](../examples/README.md).

**Current status:** pre-alpha 0.4 candidate; no released 0.4.0 distribution, OVAL Board approval, or scanner-runtime equivalence claim.

## Current candidate — 2026-11-02 Item grouping amendment

The owner explicitly approved a narrow **pre-release change to the frozen 0.4
authoring grammar** before VS Code editor handoff. In complete Tests, the
two independent Item quantifiers now serialize as
`require.item_requirement: {items_found: one_or_more, items_satisfying: every}`;
existence-only Tests use `item_requirement: {items_found: one_or_more}`.
`field_requirement` retains its separate sibling scope and original meaning.
Legacy ungrouped Item keys fail schema validation. Result reporting fields
remain unchanged: no scanner-result wire redesign was authorized.

| Audit boundary | SHA-256 |
| --- | --- |
| Historical frozen flat 0.4 JSON family | `476f5767276f5c2114f91b211cf4e159a75bee0806ea736fc631d9c40f4c4b80` |
| Amended flat 0.4 JSON family | `ab1933f2d9171ee0af70c0fab855b00f5faf78bf59ad4924fbf24b402ac4072a` |

The same sorted-relative-path-plus-NUL byte algorithm is enforced by
`tests/test_schema_integrity.py`. It covers all **143 JSON files**, **34 root
schemas**, **242 `$ref` occurrences** and **100 supported capabilities**.
Four current Assessment samples were mechanically regenerated and their exact
bytes re-pinned. The previous bytes, original source/proof records and historical
publications remain available through Git history and archival evidence; their
digests are not silently relabeled as new-semantic proofs. 0.4.0 is **not
released**, and scanner/provider/runtime equivalence is not inferred from
schema acceptance.

## Historical staging import (2026-11-02)

The import occurred before the public repository name cutover. The historical development source is now `vanderpol/scap-ng-research`; the current public specification repository uses `vanderpol/scap-ng`. The original import did not constitute a release.

| Boundary | Exact reference |
| --- | --- |
| Original source repository (now renamed/private) | `vanderpol/scap-ng-research` |
| Owner-accepted schema candidate | `6efe0d053e79d513339f7999c52d214886b6d201` |
| Schema freeze merge commit | `1401c2851516e1af230231abe47a40419bca3dc1` |
| Source commit used for staging | `d12a644f4607cdc9c9ada50e3a96d4fd0060c6d9` (Apache-2.0 LICENSE added; frozen schema tree unchanged) |
| Schema source subtree | `schema/v0.4.0/` |
| New staging location | `schema/` (files flattened; JSON bytes unchanged) |
| Versioned JSON files | **143** |
| Root JSON Schema definitions | **34** |
| Root schema `$ref` occurrences | **242** |
| Immutable JSON aggregate SHA-256 | `476f5767276f5c2114f91b211cf4e159a75bee0806ea736fc631d9c40f4c4b80` |

The aggregate digest is SHA-256 over each JSON file, sorted by relative
POSIX path, by feeding `relative-path UTF-8 + NUL + exact file bytes`. It
protects the complete version-local JSON family, not only root schema files.
Every JSON file copied into staging is byte-for-byte identical to source.

The source-relative JSON paths beneath the old `schema/v0.4.0/` directory
are exactly the same as the target-relative paths beneath flat `schema/`.
The future 0.4 release tag will version **the entire specification, schema,
metadata, examples and conformance suite together**, not just one directory.

The four Markdown navigation pages within the schema subtree were
**intentionally rewritten** for staging so outdated research, 0.3 drafts
and broken relative links do not appear as current normative guidance.
They are not included in the immutable JSON digest.

## Original locations of the four curated examples

- `docs/examples/conformance-remediation-20261101/windows-server-2025-shows-on-lock-screen-sv-278080-assessment.yaml`
- `docs/examples/conformance-remediation-20261101/windows-server-2025-control-permissions-sv-278139-assessment.yaml`
- `docs/examples/owner-contract-20261031/linux-home-mount-nosuid-assessment.yaml`
- `docs/examples/input-presence-20261101/optional-lock-screen.assessment.yaml`

## Scope of the historical staging import

The staging import did **not** move the compiler, converter, authoring normalizer, scanner, runtime or independent collection proofs. It did not change source-research evidence or proof baselines, publish a 0.4.0 release, or obtain OVAL Board ratification. Repository naming and visibility changed **after** this import; those later administrative changes must not be confused with schema validation or release qualification.

Historical conversion artifacts and proofs are research records, not current 0.4 authoring samples. The obsolete public corpus has been retired from project navigation; its verified retention belongs in the private research repository. No complete 65-stream library has yet been qualified against the current pre-alpha grammar. See the [evidence publication tracker](https://github.com/vanderpol/scap-ng-evidence/issues/1) for qualification and retirement status.

## Generated documentation and source audit

`tools/generate_docs.py` derives five offline reference/audit artifacts from
the frozen schema tree and independent source-note metadata in
`docs/metadata/`. The CI `--check` mode detects missing, stale or hand-edited
outputs by exact-byte comparison, including the generator input-hash audit.

An inventory of 5.12.3 OVAL `ntuser` XSD annotations was generated from the
original research checkout using `tools/harvest_oval_ntuser.py`; this retains
source file identities, annotation counts and hashes, but not copyrighted
source documentation text. Every one of the 15 native NTUSER fields is matched
against both legacy `ntuser_item` and `ntuser_state` annotations. Semantic
equivalence remains **pending review**.

Every supported and experimental capability receives a generated scanner
implementation section. Documentation completeness is **not** asserted:
unreviewed or missing acquisition instructions and vendor references are
identified as coverage gaps. `independent.shellcommand`, `windows.appcmd`,
and `windows.appcmdlistconfig` are explicitly prioritized for future research.


## Issue #14 native Object selector contract candidate — 2026-11-04

This draft candidate preserves the approved 0.4.0 baseline while adding a
capability-conditioned native selector overlay. The reviewed contract closes
`windows.registry.hive`, `windows.registry.key`, `windows.registry.name`, and
`linux.partition.mount_point`; the other **137 of 141** supported selector
fields remain explicitly unresolved and retain the generic baseline. No
operator subset is inferred from `selector_source_operations` alone.

`matches_regex` is the native 0.4 Object selector spelling. `pattern_match` is
kept only in the source/migration vocabulary and is not accepted as a native
Object property. Hive source case-insensitive equality is crosswalked to the
canonical `equals` enum operation; the generic case switch is intentionally not
exposed for hive.

The input contract is `schema/native-selector-contracts.json`; the deterministic
output is `schema/native-selector.schema.json`, checked by
`tools/generate_native_selector_schema.py --check`. The canonical
`assessment-language.schema.json` applies the generated definitions only when
the Test capability is one of the reviewed capabilities. This candidate changes
schema acceptance and editor completion for those selectors, but does not claim
scanner implementation coverage or prove lossless conversion of the unresolved
65-benchmark corpus. Existing examples, manual Assessments, proofs and published
artifacts were not rewritten or deleted.

| Audit boundary | Value |
| --- | --- |
| Prior approved 0.4.0 JSON family | `c6414084677c061d205c2f4010ac915dc466adcc`, `ab1933f2d9171ee0af70c0fab855b00f5faf78bf59ad4924fbf24b402ac4072a` |
| Candidate JSON family | 145 files, 35 root schemas, 296 `$ref` occurrences, `2de36b96ccf3771ee2d849ee73cf905a11db936064fb7b6b9458fd985e902156` |
| Selector audit | 141 supported selector fields: 4 resolved, 137 unresolved |

This is a draft PR candidate for owner review. It must not be merged as a
compatibility-breaking schema amendment without owner approval. The editor
handoff is the exact commit containing this candidate schema family and
`native-selector-audit.json`; no `.external/editor-pack` or VS Code repository
changes are included here.

## Issue #14 selector batch 01 — 2026-11-04

The first follow-on batch is documented in `docs/ISSUE14-SELECTOR-BATCH-FILESYSTEM.md`. It resolves 15 high-usage Linux filesystem and Windows selector contracts. The prior candidate digest above remains recorded for provenance; this batch candidate has 503 `$ref` occurrences and family digest `770bd3d2aa9ef0cea57be66c3f02e9fd7aba83bbbebf4fae830c4499b4d4abbe`. The generated inventory now reconciles to 141 total, 19 resolved, and 122 explicitly unresolved; the generator and tests reject batch-count drift. This remains a draft and requires owner approval before any merge.

## Issue #19 retained variable-function documentation — 2026-11-04

This draft documents the retained native Variable forms against the pinned OVAL
5.12.3 XSD and records the broader function disposition in
`docs/metadata/variable-function-audit.json`. It enriches schema hover/help,
including nested `concat`, `regex_capture.value`, `merge.values`, and literal
value sites. It makes no compiler, interpreter, scanner, or runtime claim and
introduces no semantic implementation change. The exact schema commit for an
editor-pack repin is the documentation PR commit; no `.external/editor-pack`
or VS Code files are changed.

## Current coordinated selector/function draft — 2026-11-04

The latest unmerged owner-review candidate is the filesystem-mapping A branch,
based on the selector and Variable-function draft chain (#15–#21). The owner
approved the established OVAL names `filepath`, `path`, and `filename`; no
aliases are introduced.

| Audit boundary | Value |
| --- | --- |
| Candidate source commit | pending final mapping-branch commit |
| Flat JSON family | 145 files |
| Root schemas | 35 |
| Root schema `$ref` occurrences | 658 |
| Aggregate SHA-256 | `0590d688edfe9f6bfcb0b3a849706dc7b2ce3e5eefbc9421c7fbb0caf0087a71` |
| Editor candidate pack manifest | pending tools/VS Code regeneration |

The earlier 143-file, 34-root, 242-reference values above remain historical
pre-selector/amendment boundaries and are not relabeled. The nine filesystem
mapping mismatches are resolved in the canonical mapping candidate. A separate
scap-ng-tools PR updates its snapshot and generated semantic pack; the VS Code
editor must pin the final combined commit and regenerated manifest only after
that PR and the generated-file conflicts from PR #16 are accepted.
