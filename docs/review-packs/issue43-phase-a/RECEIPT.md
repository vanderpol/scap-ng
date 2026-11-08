# Issue #43 — Phase A integration receipt

**Review only. Stop before Phase B.** No language release, production installation,
VS Code change, repin, live UI evidence, merge or scanner-runtime equivalence claim.

[Basic reference](reference.md) · [Advanced constraints](constraints.md) ·
[Editor metadata](editor-metadata.json) · [Pointer/provenance map](pointer-map.json) ·
[Manifest](manifest.json) · [Immutable manifest lock](pack-lock.json) ·
[Validation evidence](validation-evidence.json).

## Sources and stack

| Input | Inspected exact head | Disposition |
| --- | --- | --- |
| Frozen native 0.4.0 | `7354a24cdbfe18321153ccaef5d772801a10cd71` | All 145 JSON bytes preserved; 35 validation resources mirrored under the review namespace. |
| PR #39 | `f61fff037f18832aa04db140b3e3209dfddf7219` | Import the 42 unix.file description annotations and their provenance; exclude proposed datatype/tag/value tightening. |
| PR #41 | `532fbbfe52a220d2672256ac54d1e117d69cd043` | Import only its eight selected, editorial-approved core examples; preserve both editorial receipts and every hold. |

This purpose-specific branch is stacked on PR #41. Actual parent heads and their
native-to-parent diffs were inspected. Historical PR branches, fixtures and evidence
remain unchanged. [Input pins](input-pins.json) record every consumed source-file hash.
The new witness fixture belongs to this Phase A change, not to a historical commit.

## One pack and one prose authority

The only consumable Phase A pack is this directory. Its 36 resources all use
`https://scap-ng.dev/schema/review/issue43-phase-a/`. This temporary identifier and
`release_version: null` explicitly avoid release assignment; native version and
specification constraints remain 0.4.0 snapshots. Historical `next` and `issue40`
namespaces remain history, never dependencies of this exported pack.

Fifty source annotations map to **49 description owners**: 42 unix.file source
annotations and eight approved core examples. The extra owner-read guidance is
consolidated into its field description, rather than retaining two prose owners.
Existing shared selector/traversal and Require definitions own their text. All 23
Item/Require field pairs refer to one schema description per field. No prose sidecar
or copied datatype metadata drives the reference or help.

Native resource `$id`/`$ref` targets and authoring `condition_schema` pointers are
routed into the same local tree. The pointer map records every changed annotation,
its old text, source pointer, historical lineage and routing changes. The added
unix.file library contains annotation-only applicators. Conditional Test/Item help
routes add no datatype, required-field, cardinality or whitelist assertion.

The exported editor metadata has **68 exact capability/role/field routes**, annotation
pointers, schema-derived types, parent occurrence contexts and short choices. Input
cardinality/provision remain separate. Item and field-value counts remain separate;
`fields` stays conditional, and shared field pairs do not offer standalone absence.
All six technical outcome labels remain in the schema-backed vocabulary.

## Acceptance preservation and evidence

**157 pinned structural witnesses: 106 accepted, 51 rejected**, including the 17
selected core witnesses. [Exact instances](validation-cases.json) and before/after
outcomes are committed. These cover selector/traversal bounds, native string Object
references, complete Assessments, all 23 Item fields, repeated/missing/error/redacted
values, unknown fields, existence-only and comparison Require forms, inherited Boolean
groups and closed-property boundaries. Unknown predicates/groups remain rejected.

For each of the 35 native resources, removing the two documented annotation-only
dispatch branches and restoring old descriptions reconstructs the normalized native
tree exactly. The pointer map records equal per-resource hashes. Relative references
are normalized and review identities routed; this is not byte equality of namespace
spellings. The added annotation library is checked to contain no validation assertions.

In particular, string/fractional/boolean payloads for integer-tagged owner_uid remain
structurally accepted exactly as in 0.4.0, while PR #39's candidate rejects them. Wrong
field datatypes, empty repeated values and future field names retain native acceptance.
The basic reference therefore shows generic typed wrapper/array shapes, not PR #39's
unapproved payload types. Status/redaction prohibitions remain effective.

The standalone offline loader requires an externally supplied manifest digest. It
checks the lock, all resource/documentation/metadata hashes, source pins, namespace,
resource identity, local references and description origins without the source checkout.
Missing resources, stale hashes, wrong manifest pins, unknown capability/role/field
routes and misrouted descriptions are negative-tested. A schema sentence mutation
changes basic, advanced and metadata outputs together. Different Python hash seeds
produce the same bytes. No artifact-upload workflow is added.

Nine semantic proposals and withheld foreach remain excluded from help. Their original
native description nodes are unchanged; carrying frozen grammar dependencies does not
adopt held draft wording or advertise reachable foreach syntax.

## Reproduce

```sh
python tools/generate_review_documentation_pack.py --materialize
python tools/generate_review_documentation_pack.py --check
python tools/generate_review_documentation_pack.py --help-field unix.file object traversal.max_depth
python tools/generate_review_documentation_pack.py --help-field unix.file require fields.owner_uid
python -m unittest discover -s tests -v
```

Normal generation requires existing schema fixtures to match the pinned approved
sources; `--materialize` explicitly rebuilds only this review directory. `--check`
verifies exact output without writing files. After an approved source/schema change,
regenerate the pack and review its new manifest pin. Regeneration grants no approval.
A consumer must pin the manifest digest in `pack-lock.json` from this exact PR commit;
reading an arbitrary local lock is not an external trust pin.

## Remaining dispatch gaps and owner review

- Phase B must inspect the active VS Code worktree, Red Hat YAML associations and
  Graphical metadata loader before making a separate draft change. No editor work was
  performed in Phase A.
- The pack exports Assessment and collected-Item entrypoints and explicit lookup
  routes; these are not proof of actual YAML instance/caret association, branch-aware
  language-server annotation handling or Graphical loader adoption.
- Named Objects use native string references. Resolving a referenced shared Object to
  the consuming capability, including reuse across Tests, needs editor/compiler
  context and is not proved by field lookup. Inline selector descriptions and nested
  traversal are represented; named-reference dispatch is still a separate gate.
- Generic unknown fields retain native validation and receive no invented help. Other
  capabilities receive no unix.file metadata fallback. Recursive Boolean Require help
  is wired as annotations but still needs live editor traversal verification.
- Decide the eventual release identity and coordinated canonical placement later.
  Datatype/value tightening, nine semantic holds, foreach placement, filesystem/link
  semantics and scanner behavior remain separate owner decisions.

**STOP for owner review of Phase A. Do not task the editor to consume this pack yet.**
