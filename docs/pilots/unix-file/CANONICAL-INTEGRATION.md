# Proposed canonical integration: `unix.file`

**Owner review proposal, not an approved schema change.** The frozen `schema/` directory is untouched. `next` is an unassigned version placeholder, not a release number or publication claim.

The [basic reference](reference.md) keeps PR #37's short tables and nested traversal. The [advanced reference](constraints.md) contains schema alternatives, bounds, patterns, default annotations and links to shared predicates. Both are generated from the same schemas; presentation density does not change the source of authority.

## Concrete next-pack files

These three executable JSON Schemas demonstrate the integration; they are outside the installed pack:

| Proposed canonical path | Review artifact | Integration |
| --- | --- | --- |
| `capabilities/unix.file.schema.json` | [Capability schema](schema-next/capabilities/unix.file.schema.json) | Object, Item and Require definitions; 23 named field meanings and actual datatype/value constraints |
| `assessment.schema.json` | [Assessment entry](schema-next/assessment.schema.json) | Existing Assessment shape plus conditional dispatch at `/properties/assessment/properties/tests/additionalProperties`, when Test capability is `unix.file` |
| `collected-item.schema.json` | [Item entry](schema-next/collected-item.schema.json) | Existing Item shape plus conditional dispatch when Item capability is `unix.file` |

The two entry schemas reference the capability schema's `/$defs/test` and `/$defs/item`. A document for another capability keeps its existing structural acceptance. Dispatch requires an explicit matching capability; omitted capability does not accidentally select the UNIX definitions.

For review isolation, these candidates reuse immutable `v0.4.0` shared primitives by absolute `$ref`. A real next-version publication would rebase the shared pack's IDs/references and specification-version bindings together; that coordinated version migration is not performed here. This is an executable delta, not a complete new-version distribution.

## Exact schema placement

All pointers below are in `capabilities/unix.file.schema.json` unless noted.

| Concern | Exact schema node | Role |
| --- | --- | --- |
| Object meaning | `/$defs/object/description` | Capability introduction |
| Object fields | `/$defs/object/properties/<field>/description` | Selector/control descriptions beside real property names |
| Nested traversal | `/$defs/object/properties/traversal/properties/<child>/description` | Exact hierarchy; structural assertions remain the referenced shared traversal schema |
| Shared field meaning | `/$defs/field_meanings/properties/<field>/description` | Single description node referenced by both Item and Require; no second prose authority |
| Datatype tag | `/$defs/datatype_integer/const` (also string/boolean) | Real JSON Schema assertion, not a documentation keyword |
| Observed value contract | `/$defs/value_owner_uid/properties/datatype/$ref` and `/value/type` | References the integer tag definition and requires an integer when `value` is present |
| Item binding | `/$defs/item_fields/properties/owner_uid` | References its field meaning; `oneOf` selects one typed value or an array of typed values |
| Comparison binding | `/$defs/require_fields/properties/owner_uid` | References the same meaning; an explicitly supplied `datatype` references the same tag definition |
| Grouped comparison | `/$defs/condition` | Extends the existing inherited-condition schema and recursively dispatches `and`/`or`/`one`/`xor` children without requiring a new Item quantifier at every group |

The same value/tag bindings exist for **all 23 fields**. Inferred comparison datatypes remain optional. Item/field cardinalities, absence-only checks, statuses and redaction remain governed by shared native grammar. No `value` is made mandatory by these new field schemas; a missing/error/redacted value remains subject to the existing typed-value rules.

These schemas use ordinary `$defs`, `$ref`, `properties`, `const`, `type`, `oneOf`, `items`, `if` and `then`. There is no custom documentation object or out-of-schema descriptive metadata. A renderer can read the field description through its local reference and the datatype from the value contract; an editor selecting the same capability schema sees the same nodes. Live editor dispatch is not claimed.

## Compatibility and owner decisions

| Case | Frozen 0.4.0 | Proposed next schema |
| --- | --- | --- |
| Correctly typed single or repeated Item value | Accepts | Accepts |
| Integer-tagged `owner_uid` with a string, fractional or boolean `value` | Structurally accepts | Rejects |
| `owner_uid` tagged `string` | Structurally accepts | Rejects |
| Explicit Require datatype incompatible with the named field | Structurally accepts | Rejects, including in inherited condition groups |
| Require datatype omitted for inference | Accepts | Accepts |
| Item-existence-only requirement | Accepts | Accepts |
| Error/absent field with correct tag and no value | Accepts | Accepts |
| Error field carrying a value | Rejects | Rejects |
| Unknown future field name | Generic schema accepts | Remains generic; no new whitelist |
| Other capability | Existing contract | Existing contract |

**Recommendation:** adopt the named capability definitions and enforce their existing mapped datatypes in the next version. This makes the declared contract usable by documentation, editors and validators and exposes inconsistent evidence rather than coercing it. **Alternative:** adopt descriptions and tag annotations first while retaining generic value acceptance; that avoids the validation tightening but leaves datatype/value consistency exclusively to semantic validation. Owner approval is needed before either candidate is installed or treated as normative.

This proposal does not solve every semantic validation task. Inferred literal operand types, typed operation compatibility and reference resolution remain compiler/semantic-validator responsibilities. Named Object references still use the shared reference schema; checking the referred Object against its consuming Test capability requires existing reference resolution or a later reviewed registry dispatch. Result-container entry schemas would similarly need to reference the next Item entry when packaging a complete next-version pack. None of those routes is claimed implemented by this three-file demonstration.

No selector-pairing assertion, source-only restriction, new unit, filesystem rule or error interpretation is added. Those gaps remain visible in the research records. This review concerns canonical placement and explicitly demonstrated datatype tightening only.

## Migration and verification

```sh
python tools/propose_unix_file_schema_integration.py
python tools/propose_unix_file_schema_integration.py --check
python tools/generate_unix_file_reference.py --check
python -m unittest discover -s tests -v
```

The migration demonstration copies descriptions from the current proposed JSON Schema and imports the pinned native field datatype mapping once into actual `const`/`type` nodes. The generated candidate files are marked as proposals. **After adoption, the next canonical schemas would become the directly maintained authority**: retire this one-time migration and the transitional annotation overlay, and point the reference renderer/editor at the canonical capability schema. Do not maintain a metadata-to-documentation synchronization loop or edit generated candidate copies independently.

Tests check exact regeneration of all three candidates, schema validity, all 23 description/type bindings, conditional entry dispatch, existing curated example acceptance, shared absence/error rules and explicit before/after datatype vectors. These are structural schema tests; they establish no scanner-runtime equivalence.

**Stop for owner review.** No merge, pack publication, other capability expansion or frozen-schema modification.
