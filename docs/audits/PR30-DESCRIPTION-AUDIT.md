# PR #30 description ownership and editor-access audit

**Finding: complete useful field help is not established.** The shared model is
a suitable working architecture, but its generated guides are not an editor
help integration. No capability can currently be certified as having complete,
useful Object, collected Item and Require help through the inspected paths.
This does not mean all editor help is absent. The model's `verified` status
concerns source projections/references, not complete useful field descriptions
or successful editor presentation.

Audit input: canonical PR #30 at `d7c6af21c323c972a095a97d381983899045933b`;
all 145 frozen JSON files retain aggregate SHA-256
`63a61b3eb0ca95790721699f5e63b6f5a16b146660b9545a437519b508351db5`.
The [complete per-capability ledger](pr30-description-coverage.json) covers
100 supported and four experimental capabilities. Counts below are field
occurrences per capability, not unique names. Labels, prompts, type lists and
nonempty generic text are not counted as useful field definitions.

## Where descriptions live

| Location | Existing information | Editor connection |
| --- | --- | --- |
| JSON Schemas | Shared Object structure, selector/comparison operators, cardinalities, requirements, variable/Input references, traversal and result envelopes; 28 resolved selector notes | Schema resolver/hover can consume descriptions in the active pinned pack; not proof of complete capability-specific help |
| Frozen capability mappings | 45 collection-parameter descriptions; six selector case descriptions; 17 field descriptions in four experimental ESX mappings; datatypes/enums/rules elsewhere | Pack manifest has mapping URIs. Parameter prose can be projected by the Tools pack generator; most mapping prose has no general field-help consumer |
| Frozen `authoring-vocabulary.en.json` | Shared term/operation explanations; Registry selector labels/prompts; two Registry Require-field descriptions (`type`, `value`) | Editor YAML help explicitly looks up capability selectors and state fields plus shared vocabulary scopes |
| Proposed `docs/metadata/schema-documentation-pilot.json` | 11 Object-field author descriptions, plus separate implementer facts/questions/lineage/status | Read by the guide generator; not loaded by the inspected editor or supported offline-pack builder |
| `docs/metadata/windows.ntuser-source-notes.json` | 15 legacy field interpretations, separately pending native-equivalence review | Rendered in the NTUSER research guide; not native field-help coverage or an editor lookup source |
| Generated Markdown | Per-platform structural tables and pilot notes | Regenerable output; not an editor help source |
| Handwritten Markdown | Common boundaries, pilot source review, annotation proposal and plan | Human review/research context; no automatic editor ingestion |

The 17 experimental field descriptions are a material exception: they already
have a reusable metadata home in `native.field_documentation`. PR #30's documentation
projection and rendered field tables omit that home. The existing pack builder
exports supported capabilities only, so these four capabilities are also
outside that editor-pack path. Experimental scope must remain explicit.

## Complete field census

| Surface | Inventory | Description coverage and qualification |
| --- | --- | --- |
| Object selectors | 145 (141 supported, four experimental) | 28 have resolved schema contract notes; 117 lack those notes. Notes often explain source conversion/operator constraints rather than the field's meaning |
| Object collection parameters | 45 | All have mapping descriptions; none has a direct description on the frozen closed-overlay property. Derived pack generation can supply parameter descriptions |
| Proposed author help | 11 Object fields across three pilots | All remain external to canonical schema/editor resource loading; overlap with existing parameter and selector prose needs consolidation |
| Collected Item fields | 711 (694 supported, 17 experimental) | 17 experimental metadata descriptions; no capability-specific Item-property descriptions in the frozen generic Item schema |
| Require field conditions | Same 711 field-name inventory, with separate comparison datatypes where recorded | 17 metadata descriptions could be reused; two Registry fields have vocabulary descriptions. Shared operator/cardinality prose does not define the remaining fields |
| Result-only field extensions | Eight across five capabilities | Name-resolution/result lineage exists; field-specific help is not established. These are not Require fields |
| Legacy Item notes | 15 NTUSER field notes | Research candidates only; excluded from native field-description coverage |

Zero direct Object-property descriptions is a narrow census of the frozen
native selector overlay's selector/parameter property nodes. It does **not**
exclude inherited descriptions, shared controls or descriptions added to
external generated capability schemas. The ledger lists closed-overlay
collection controls separately. The inventory includes `windows.wuaupdatesearcher.source_path`, a native-added
field omitted by PR #30's `state_field_map`-only projection: that projection shows
710 fields while the complete known inventory has 711. Six record wrappers across
four capabilities also allow record children whose field-specific descriptions
are not established. Their generic record grammar does not certify help for
every possible dynamic child. Datatype and enum inventories are structural
facts, not substitutes for prose explaining acquisition and interpretation.

The frozen collected Item uses `fields.additionalProperties`, not per-capability
named property definitions. Require fields similarly use shared predicate
schemas. Consequently, schema validation and generic hover can work while a
field's meaning, units, cardinality or unavailable/error interpretation remains
undocumented. An empty help string is not the only failure mode: generic
comparison help can be displayed where field semantics are needed.

## Editor source trace and limits

Read-only inspection used [VS Code PR #36 at
`86cd7f60d01253a788b0a046f8cf7d286f0336b8`](https://github.com/vanderpol/scap-ng-vscode/pull/36).
No Editor PR or files were modified.

- [`MetadataPack.describe`](https://github.com/vanderpol/scap-ng-vscode/blob/86cd7f60d01253a788b0a046f8cf7d286f0336b8/src/metadata.ts) combines schema `$ref`/`allOf` descriptions and authoring annotations. The loader accepts schema, mapping and vocabulary resources, not the pilot sidecar or Markdown.
- [`yaml-help.ts`](https://github.com/vanderpol/scap-ng-vscode/blob/86cd7f60d01253a788b0a046f8cf7d286f0336b8/src/yaml-help.ts) resolves capability Object/state-predicate schema paths. It prefers capability vocabulary descriptions, then schema descriptions, and otherwise displays an explicit missing-description message. It also consumes selector case semantics from mappings. The two Registry Require-field vocabulary entries therefore have an implemented lookup path; this is source-level evidence, not a live-hover certification.
- [`GuidedCatalog`](https://github.com/vanderpol/scap-ng-vscode/blob/86cd7f60d01253a788b0a046f8cf7d286f0336b8/src/guided.ts) obtains Object descriptions from generated capability properties. Require/result-field descriptions come from generated state-predicate properties or their schema references. It does not merge `native.field_documentation` or the new pilot sidecar. Graphical and YAML help do not have the same complete field-description lookup path.
- [`schema-profile.json`](https://github.com/vanderpol/scap-ng-vscode/blob/86cd7f60d01253a788b0a046f8cf7d286f0336b8/schema-profile.json) pins source commit `7b9b61108aa30a601828268576308e510477094e` and manifest `b156e978c2655fa6231c5d8b86d54e873e78ee344b606dd3cdc7e1702830269f`, not PR #30. Availability of new guide files in GitHub does not update that immutable pack.

The [public Tools pack builder](https://github.com/vanderpol/scap-ng-tools/blob/c0bab54de413fb80305d2ac6b47e46a70c9ce3ff/scripts/build_v04_editor_metadata_pack.py)
links each supported capability's generated `schema_uri` and `mapping_uri` and
exports schemas/mappings/vocabulary. Its
[capability generator](https://github.com/vanderpol/scap-ng-tools/blob/c0bab54de413fb80305d2ac6b47e46a70c9ce3ff/scripts/_v04_generation/generate_capability_schema_v04.py)
can inject parameter and generic control descriptions. Selector fallback text
such as “native Object selector … type checked” is not a field definition;
state predicates receive datatype restrictions without field descriptions.
This generator is supporting pipeline evidence, not a claim that its output
is the exact pack installed by a user.

No exact-profile VS Code UI/hover execution was performed in this audit. The
inspected profile's exact pack was not available locally. Full accessibility
requires testing that pack, both YAML and Graphical paths, and collected Item
editing separately; the current custom YAML provider targets Assessment files,
not every result/Item document.

## Duplication and missing links

The ledger records **58 exact duplicate groups** among **828 frozen description
occurrences**. Mechanical repetition is distinct from competing prose authority:

- The selector-operator explanation occurs 141 times in the editor default policy;
  the set-operator explanation occurs 81 times. These should derive from shared
  templates; deleting individual frozen copies would violate the freeze.
- Several comparison explanations occur 13 times across generated predicate
  branches. Shared operator help should remain reusable rather than become
  handwritten capability text.
- A UNIX selector paragraph is repeated for all three file selectors; the Windows
  counterpart repeats for its three selectors. The text explains common
  crosswalk rules but does not separately define each field.
- The shell error flags have mapping descriptions and separately authored pilot
  descriptions of the same behavior. The guide chooses the pilot version,
  while existing pack generation chooses the mapping version. This is a real
  two-authority maintenance risk even when the wording is not identical.
- The pilot review Markdown repeats Registry null/default identity, UNIX
  selector/result names and shell stdout/comparison distinctions already stated
  in metadata or schema notes. Keep research conclusions/provenance handwritten;
  generate the stable fact portions from their single source.

Missing connections, in priority order:

1. Schema/property and capability-role identities do not resolve to a common
   field-description record. `selector_map` and `state_field_map` relate names;
   they are not field-help links. Reviewed native names and migrated names also
   differ (`filepath`/`full_path`, `name`/`package_name`), so matching by spelling
   alone is unsafe.
2. The pilot's `contract_refs` go **from prose to native facts**. There is no
   reverse schema-to-proposed-help link, exported documentation resource, or
   editor lookup of that sidecar. `x-generated-from` records generator lineage,
   not a field-level help binding.
3. Existing `native.field_documentation` and the native-added `source_path` field are not projected by the guide model,
   and has no general Require/Item editor-help consumer. Result-only extensions
   also need explicit role-specific documentation bindings.
4. Vocabulary field help is only sparsely populated and is consumed differently
   by YAML and Graphical paths. A manifest `mapping_uri` makes a mapping
   addressable; it does not automatically surface its prose.
5. Current documentation tests check drift, field-reference validity and broad
   annotation hygiene. They do not require every capability-role field to have
   useful prose or demonstrate that prose in editor controls/hover.

## Recommended changes — proposal only

1. **Inventory first:** use this ledger to define an explicit coverage matrix for
   each capability's Object selector/parameter/control, Item field, Require field
   and result-only field. Record shared generic help separately from field meaning.
2. **One prose authority:** extend the accepted external working model with
   role-specific field descriptions and stable source pointers. Reuse existing
   mapping prose and vocabulary; move competing pilot wording into one reviewed
   source. Separate author meaning, collector obligations and comparison notes.
   Preserve native/legacy provenance and documentation status independently of
   runtime qualification.
3. **Generate all consumers:** derive platform tables, exported editor help and
   future schema annotations from that one model. Keep all 0.4.0 schema bytes
   unchanged. Any documentation overlay/resource or pack-format change needs a
   reviewed, pinned integration contract; do not silently merge unversioned prose.
4. **Repair links before claiming coverage:** resolve source/native field aliases
   through reviewed crosswalks; bind schema URI + pointer + capability + role to
   a documentation record. Preserve experimental exclusions unless explicitly
   enabled. Do not treat scanner research notes as normative author descriptions.
5. **Add meaningful acceptance tests after review:** require descriptions that
   explain field meaning rather than repeat its name/type; exercise parameter
   help, Item fields, Require conditions, nested records, aliases and result-only
   extensions. Test the same expected source text through YAML hover and
   Graphical controls using the exact offline pack, with negative missing-link
   and pin-mismatch cases. Keep grammar acceptance/rejection unchanged.

No schema, editor, pack, field-help integration or semantic fix is implemented by
this audit. The Phase 2 research remains separately preserved and uncommitted;
these recommendations are reported before implementing description changes.

Reproduce the canonical census: `python tools/audit_documentation_coverage.py --check`.
