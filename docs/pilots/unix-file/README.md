# Schema-description pilot: `unix.file`

Issue [#38](https://github.com/vanderpol/scap-ng/issues/38). **Proposed annotation placement, for owner review; not an installed schema pack.** Single-capability demonstration only.

Read the [generated reference](reference.md), [advanced constraints](constraints.md), and [concrete canonical integration proposal](CANONICAL-INTEGRATION.md). Its field meanings come from JSON Schema `description` properties in [the proposed overlay](unix-file.annotations.schema.json), not a Markdown template or descriptive metadata sidecar. The renderer supplies layout and labels; pinned JSON Schemas supply types, enumerations, defaults and structural relationships. Capability metadata is used only to audit field identity and provenance; its datatype lists and selector alternatives do not drive the reference. Examples also live in standard JSON Schema `examples` annotations. The source map contains locations, hashes and review dispositions, not a second copy of the field descriptions.

## Reproduce

From the repository root, with `requirements-dev.txt` installed:

```sh
python tools/generate_unix_file_reference.py
python tools/generate_unix_file_reference.py --check
python tools/generate_unix_file_reference.py --hover object.traversal.max_depth
python tools/generate_unix_file_reference.py --hover item.fields.owner_uid
python tools/generate_unix_file_reference.py --hover require.fields.owner_uid
python -m unittest discover -s tests -v
```

The last two hover requests return the **same description and schema pointer**: `/$defs/field_meanings/properties/owner_uid`. The source-level harness resolves local schema references offline. It demonstrates description availability for a proposed role-selected pack; it does not execute VS Code or prove live completion/hover coverage. It fails on unknown paths. No editor repository or production pack is modified.

## Proposed placement and explicit design gap

| Role | Proposed schema node | Existing structural authority |
| --- | --- | --- |
| Object | `/$defs/object/properties/<name>`; nested `traversal/properties/<child>` | Frozen `native-selector.schema.json#/$defs/unix_file_object` |
| Item field meanings | `/$defs/field_meanings/properties/<native field>` | Frozen generic typed-value/array shape; capability field names audited against the native mapping |
| Collected Item | `/$defs/item/properties/fields` references those field meanings | Frozen `collected-item.schema.json` |
| Require field meanings | `/$defs/require/properties/fields` references the same meanings | Frozen `assessment-language.schema.json#/$defs/canonical_all_items_requirement` |
| Shared requirement controls | `/$defs/require/properties/item_requirement` and `field_requirement` | Frozen Item/field cardinality grammar |

The frozen collected Item and Require field maps use `additionalProperties`; they have no capability-specific property nodes at which to attach the 23 meanings. Putting UNIX descriptions directly on those generic maps would misdescribe other capabilities. This proposal therefore adds named, **description-only properties in a capability-scoped schema overlay**, shared through a local `$ref` by Item and Require. It adds no `type`, `required`, `enum`, default, field whitelist or semantic assertion. Existing role schemas remain the validation authority through their exact `$ref` identities. The proposal root is a container: consumers must explicitly select `#/$defs/object`, `#/$defs/item` or `#/$defs/require` in a `unix.file` context.

This is an explicit schema mechanism for review, not an accepted new grammar or hidden documentation metadata platform. Frozen files under `schema/` are byte-identical to base commit `7354a24cdbfe18321153ccaef5d772801a10cd71`; all 145 JSON file hashes are checked before rendering.

The [canonical integration proposal](CANONICAL-INTEGRATION.md) now supplies executable next-pack capability, Assessment-dispatch and Item-dispatch schemas. It recommends moving descriptions and datatype contracts into those canonical nodes after approval, retiring the transitional overlay. The exact validation tightening and remaining integration routes are documented separately; no candidate is installed in the frozen pack.

## Comparison with PR #37

Presentation baseline: PR #37 head `5e6c49d0a34b3b5380d753fa0142037e494275bd`; its exact page hash is in [source-map.json](source-map.json). Latest [owner feedback](https://github.com/vanderpol/scap-ng/pull/37#issuecomment-6714957457) is incorporated without changing that PR.

| Baseline feature | Generated pilot |
| --- | --- |
| Five resource/control rows | Short meanings; technical choices and shared predicate links moved to advanced constraints |
| Nested traversal | One parent row, two child rows, exact required children and vocabulary |
| 23 Item fields | Same field set and order; generic typed-value/array details accessible in advanced constraints |
| Require | One shared-grammar statement/link; shared control descriptions available to the harness |
| Behavior | Short table; neutral unresolved-runtime notes; historical rules not promoted |
| Illustration | One nested YAML excerpt generated from schema `examples`; examples and displayed fragments validate; no scan |
| Historical attribution | One concise attribution at the end; detailed mappings remain in research records |

Source-name translations and historical defaults no longer clutter the user reference. Unit/resolution, file-kind labels, directory-only name representation, unsupported ACLs and error propagation remain explicitly unspecified. Historical source restrictions such as absolute-only paths and empty filename prohibitions are not invented as native schema restrictions. The source mapping's traversal rules still use collected names (`full_path`/`directory`); their binding to authored selectors remains a contract gap, not a new validation rule in this pilot. Broader Sets/filters/operator documentation is linked through the existing native sources rather than reimplemented.


### Frozen-schema structural gaps

The canonical Object schema does not encode the metadata's `filepath` versus `path` + `filename` selector pairing as a schema alternative. Its actual `oneOf` is Object reference versus inline Object. The advanced reference shows that actual hierarchy rather than presenting a metadata relationship as schema structure.

Similarly, the collected Item schema permits a typed value or an array of typed values for every field, with a free-form string datatype tag. It does not encode capability-specific datatype constraints. The advanced reference shows the generic field-value shape and links its canonical definition. The separate next-schema proposal demonstrates named datatype constraints for review; they do not alter frozen grammar. Selector pairing remains a separate gap.

The renderer follows native `$ref` and `allOf` for the small scalar/control definitions it renders and retains `oneOf`/`anyOf` boundaries. Complex shared selector/predicate definitions remain canonical schema links rather than being flattened into a partial operator grammar. This is a bounded renderer, not a complete JSON Schema documentation engine. All capabilities beyond `unix.file` remain out of scope.

## Evidence and limits

Four additional next-schema tests check all 23 canonical bindings, deterministic candidate generation, capability dispatch and the proposed acceptance delta. They do not qualify new grammar as approved.

- Seven focused reference tests cover the annotation-only structural invariant, 35 independent valid/invalid acceptance vectors, shared Item/Require hover origins, all 23 rendered fields, minimal YAML shape, exact-byte regeneration, drift rejection and fail-closed mapping/pin checks.
- Both frozen and proposed validators receive the same vectors and expected results. One intentionally counterintuitive vector records existing acceptance of an integer-tagged Item field with a string value: datatype/value consistency is outside that frozen structural check. Named annotation properties also preserve acceptance of future/unknown Item and Require field names.
- Synthetic schema-keyword and example mutations drive the corresponding output. A re-pinned metadata-only datatype/alternative mutation leaves output unchanged, demonstrating that there is no parallel documentation model. A description mutation changes generated text; missing/unknown mappings and missing provenance cause explicit errors. CI discovers the focused tests through the existing workflow; no new upload workflow is introduced.
- No runtime, scanner equivalence, compiler/converter or release-readiness claim. Role selection in a real editor and adoption of any semantic interpretation require separate review.

The [source map](source-map.json) pins the historical XSD commit and full-file hashes, exact element/attribute lookup paths, hashes of normalized annotation text, native mapping pointers and review dispositions. Original annotations were inspected at that pin; only original paraphrases are published, with source notices retained at their linked origin. Annotation hashes use UTF-8 SHA-256 of joined direct `xsd:annotation/xsd:documentation` text (`itertext().strip()`, documents joined with a newline). Regeneration needs no external source checkout or network.

**Stop after this pilot for owner review of content, schema placement and output. No expansion or merge.**
