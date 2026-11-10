# `unix.file` schema-driven documentation pilot

[Basic reference](reference.md) · [Advanced constraints](constraints.md) · [Short parity/gap checklist](PARITY-CHECKLIST.md) · [Canonical integration proposal](CANONICAL-INTEGRATION.md)

Implements the [consolidated owner review](https://github.com/vanderpol/scap-ng/pull/39#issuecomment-6715466923) for issue #38. PR #37 supplies the presentation baseline. This is one capability and an unapproved next-version proposal; it is not an installed schema pack.

## After a schema change

Edit the proposed [canonical capability schema](schema-next/capabilities/unix.file.schema.json), then run **one command** from the repository root:

```sh
python tools/generate_unix_file_reference.py
```

It regenerates the basic page, advanced page and parity checklist together. Do not edit generated Markdown. CI runs the matching read-only check:

```sh
python tools/generate_unix_file_reference.py --check
```

A stale/missing output fails the check. Both commands use only local, pinned sources; no web download, source checkout, editor or scanner is needed. Existing `requirements-dev.txt` supplies the dependencies. Run the repository tests before pushing:

```sh
python -m unittest discover -s tests -v
```

## One authoritative source

Descriptions, types, datatype tags, occurrence constraints, enums/defaults and examples now live in the proposed canonical JSON Schemas. The transitional annotation overlay and metadata-to-schema migration script have been retired. The renderer does not import datatype lists or selector alternatives from capability metadata. The source map audits historical identity/coverage; it is not another field-description model.

The current `schema/` directory remains byte-identical to base `7354a24cdbfe18321153ccaef5d772801a10cd71`: all 145 frozen JSON hashes are verified before regeneration. Proposed `schema-next/` files are directly maintained review sources outside that directory. They reference frozen primitives to isolate the proposal's explicit datatype changes; `next` is an unassigned placeholder.

## Types and occurrences

The four-column reference distinguishes property/map-key occurrence, total map entries, repeated typed wrappers and inner payload presence. Optional traversal has required children only when present. Comparison and existence-only Require branches retain separate contexts; no selector-pairing `oneOf` is fabricated.

The renderer follows local `$ref`/`allOf`, preserves branch boundaries, and evaluates `if` branches only with an explicit instance context. Required/minimum/maximum bounds are read in that context. Unknown dependent/conditional constraints are reported as `conditional` or `unspecified`; unsupported inspected shapes fail rather than being filled from historical conventions. This is a bounded pilot renderer, not a complete JSON Schema analysis engine. Shared operators/record/status grammars remain links.

For offline editor-oriented description resolution:

```sh
python tools/generate_unix_file_reference.py --hover item.fields.owner_uid
python tools/generate_unix_file_reference.py --hover require.fields.owner_uid
```

Both return `/$defs/field_meanings/properties/owner_uid` in the canonical capability schema. This source-level harness does not claim live VS Code coverage.

## Parity and evidence

The [checklist](PARITY-CHECKLIST.md) covers all 23 collected Item rows, Object controls, all four historical behavior attributes, useful choices/defaults, conditional behavior and inheritance links. Each entry is `present`, `native-undecided` or `intentionally shared/link-only`. Historical size/time units, file-kind labels, ACL status rules and directory access semantics are kept in the review records instead of being asserted as native requirements.

[source-map.json](source-map.json) records the exact PR #37 baseline, pinned XSD commit/files, per-description locations/hashes and both fetched 5.12.3 Read the Docs pages (full HTML, section and per-row hashes). Those URLs are mutable; hashes identify reviewed bytes, not an immutable RTD revision. No original annotation prose is copied into the schema. CI does not fetch the web pages.

Tests include independent bound witnesses and mutations of schema types, required properties, arrays/maps, enums/defaults and contextual branches. They distinguish forbidden values from forbidden properties and absent map keys from status-dependent payloads. A metadata-only mutation leaves all three generated outputs unchanged. Datatype acceptance changes remain separately identified in the integration packet and tests; no schema test establishes scanner-runtime equivalence.

**Stop for Jack's review.** No merge, pack installation, other capability expansion or changes to PR #30/#37, scanner/compiler/converter, editor or prior proofs.
