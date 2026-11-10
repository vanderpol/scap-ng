# Approved annotation integration receipt

Owner authorization: [PR #41 handoff](https://github.com/vanderpol/scap-ng/pull/41#issuecomment-6721723400).
This is an isolated next-version proposal, not installation into an approved release.

## Editorial receipt

[Batch 1](../../research/issue40/EDITORIAL-REVIEW.md) retains 21 editorial acceptances,
six semantic holds and withheld foreach. [Batch 2](../../research/issue40/EDITORIAL-REVIEW-2.md)
records 22 accepted-as-written cases, the exact approved replacements for 06, 18 and
19, and three semantic holds (07, 16, 17). Both JSON worksheets retain the reviewed
sentences, original Codex drafts, engineering notes, exact pointers and approval links.
Reconstructing each pre-review dossier must match its pinned digest. Acceptance of
wording does not approve runtime semantics or production installation.

## Eight-description demonstration

[Generated reference](REFERENCE.md) · [Offline help output](offline-help.json) ·
[Exact old/new pointer map](source-map.json) · [Bounded selection](selection.json).

The selection contains eight editorial-approved descriptions across five source
schemas: shared Input reference, Input cardinality and required flag, shared field
predicate, else_if, declared not_evaluated, technical outcome and value redaction.
No held description is installed. No other description is changed.

The five [proposal schemas](schema-next/) contain the complete corresponding native
schema structures with only the eight approved description additions/replacements and
reversible resource-identity/reference routing. Existing descriptions elsewhere in
these copies remain untouched. The sixth schema, [offline-help.schema.json](schema-next/offline-help.schema.json),
is an annotation-free set of lookup aliases; it neither owns prose nor changes the
Assessment grammar. Shared Input/field meanings each have one description owner;
existing reference consumers reach it rather than receiving copied annotations.

The unpublished `https://scap-ng.dev/schema/proposals/issue40/` namespace isolates
this exercise from PR #39's existing `schema/next/assessment.schema.json` proposal.
It is not a chosen release version or a deployed URI. Original version/specification
constraints and annotations remain 0.4.0 snapshots. This is an annotation/routing
prototype, not an independently usable future language version. References outside
these five resources continue to use the pinned frozen pack; all resolve locally.

Only the explicit materialization command reads accepted worksheet text to build
proposal schemas. Reference rendering and offline lookup then read the actual JSON
Schema `description` nodes. The generated map records old/new description pointers,
old wording/presence, approved case IDs, approval links, fixture paths and resource
routes. It contains no independently maintained replacement prose. Types and enum
options use PR #39's shared `schema_documentation` inspector. Full assertions remain
in the schemas rather than being repeated in the basic table.

## Verification and limits

- All 145 frozen JSON inputs match the pinned Phase 1 manifest. Frozen-family byte
  integrity is also checked by the existing tests; no frozen file is written.
- Restoring the eight previous descriptions and reversing proposal URI routing
  reconstructs the original schema trees after normalizing relative `$ref` URIs
  to absolute targets, including every validation assertion and all unselected
  annotations. This compares resolved routing, not byte equality of URI spellings.
- **17 pinned positive/negative structural witnesses** from the selected cases have
  the same expected validity before and after. Witnesses include parent-context
  guards/cardinality and status/redaction constraints. These do not execute a scanner
  or establish runtime equivalence.
- Every proposal `$ref` resolves within the local pack. Generated reference sentences
  and offline help record their exact `description` origins. Tests mutate a schema
  sentence and observe both outputs change; missing descriptions fail lookup.
- The gate rejects missing/stale schema descriptions, unapproved edits, assertion
  changes, held selections and stale generated reference/help/map bytes. `--check`
  is read-only and tested as such.

**Offline source lookup is not live VS Code UI verification.** The CLI selects an
explicit schema-node alias; it does not test YAML instance/caret association, JSON
language-server annotation merging, extension packaging, or the live hover UI. No
editor repository, schema association, pack version or repin is changed.

## Reproduce after an approved annotation change

```sh
# Explicitly rebuild only the isolated next-version schema fixtures:
python tools/generate_approved_annotation_pilot.py --materialize
# Regenerate reference/help from those actual fixtures:
python tools/generate_approved_annotation_pilot.py
# Read-only drift, source, approval and validation gate:
python tools/generate_approved_annotation_pilot.py --check
# Example local lookup, with exact annotation pointer and reference chain:
python tools/generate_approved_annotation_pilot.py --hover input-reference
python tools/audit_schema_documentation.py --check
python -m unittest discover -s tests -v
```

The existing portable CI runs these gates without artifact uploads. Future selected
annotation edits require editorial approval first; regeneration does not approve them.
The 1,580-finding research baseline/crosswalk/bulk patch remain unchanged.

## Decisions before canonical placement and editor routing

| Decision | Recommendation | Current boundary |
| --- | --- | --- |
| Canonical annotation placement | Keep the eight exact structural owners shown in the pointer map; reuse the existing shared Input-reference and field-predicate definitions. | Demonstrated only in proposal fixtures; no canonical installation. |
| Next-version identity and stacked integration | Choose the version/URI once and reconcile these annotations with PR #39's proposal in one coordinated schema tree. Preserve this exercise's annotation-only assertion parity. | Isolated namespace avoids shadowing PR #39; no merge of its proposed validation changes. |
| Production editor-pack routing | Package the same canonical schemas used by reference generation; explicitly route next-version Assessment/result consumers to the corresponding shared resources. | Lookup aliases are test scaffolding, not production editor associations. |
| Editor proof | After placement/routing approval, test actual supported editor associations and live hovers, including shared `$ref` owners and branch-selected fields. | Offline evidence cannot substitute for that UI/package verification. |
| Held semantics | Resolve the nine held descriptions separately; keep foreach unadvertised until placement is approved. | No holds, runtime decisions, bulk application of 46 acceptances, merge or release. |

**STOP for Jack/ChatGPT review.**
