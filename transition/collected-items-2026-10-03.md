# Collected Item 0.2.0 implementation checkpoint

Status: **bounded experimental result contract**, not a released 0.2.0 schema,
collector implementation, or proof of target-runtime equivalence. Owner requested
completion of the remaining readability review on 2026-10-03 and explicitly
excluded registry view because its deprecation was intentional.

## Disposition of the complete inventory

All 100 current mappings were reviewed; 99 produce Items and
`independent.unknown` has no observation contract. The complete pinned inventory
is in `research/iterations/003/evidence/collected-item-fields-2026-10-03.json.gz`.
The prototype consumes the current 0.1.0 mappings; it does not modify them or
add Object selectors/State predicates. The owner reconfirmed that these additions
do not warrant Object inclusion without a good reason; no such use case is
established here.

| Existing capability | Optional result-only fields | Authoritative source fields |
| --- | --- | --- |
| `unix.file` | `owner_user_name`, `owner_group_name` | `owner_uid`, `owner_gid` |
| `unix.process58` | `user_name`, `real_user_name`, `login_user_name` | `user_id`, `ruid`, `loginuid` |
| `linux.inetlisteningservers` | `user_name` | `user_id` |
| `unix.password` | `primary_group_name` | `group_id`; username already present |
| `macos.accountinfo` | `primary_group_name` | `gid`; username already present |

Shared optional `context.locators` supplies text, structured-source, and
record/property locations without copying resource names and selectors into
new capability fields. Locator applicability is determined by the actual source,
not an arbitrary platform allowlist.

Windows file `owner` already means `DOMAIN\username` in the pinned
`windows-system-characteristics-schema.xsd`, `file_item/owner`. Existing Windows
SID/name pairs need no duplicate name field. A new Windows file owner SID remains
deferred until acquisition and use cases justify it. Service labels, package
identifiers, filesystem/device/interface identities generally already exist;
no blanket additions are justified. Unix mode strings and date/unit presentations
belong in rendering derived from authoritative fields, with accurate units and
ACL qualification. Detailed AppArmor populations and extra service lookups remain
deferred pending demonstrated need and evidence limits. Registry view is excluded.

## Shared contract

Item IDs are local to the consuming Assessment Result. They are not durable
cross-scan resource identities. Existing `provenance` retains target, acquisition,
effective binding and execution context through the surrounding result graph;
this slice does not invent a new mandatory provenance vocabulary. Consumers must
resolve those relationships to the correct target and invocation.

Item/entity status is `exists`, `does_not_exist`, `error`, or `not_collected`,
following the pinned OVAL system-characteristics StatusEnumeration with native
underscore spelling. This is distinct from collection flags (including complete,
incomplete and not_applicable) and the six Test outcomes. Root Item status is
explicit. Entity status may be omitted for the existing observed-value convention.
An unavailable entity has no `value`, including no null placeholder. Redacted
values also have no `value`; redaction is not nonexistence. Missing/error record
entities have no record payload. Observed records retain recursively typed fields
and multiplicity. A partly nonexistent Item can retain successfully observed
fields, such as its directory; successful fields are not erased by Item status.

Resolved names are optional and never replace numeric identities. Each emitted
name, including an unsuccessful lookup, has `context.name_resolution.<field>`:
`source_field`, `target_context_ref`, `source_ref`, and `observed_at`. These identify
the numeric field, assessed target identity namespace, lookup source/snapshot,
and lookup time. A name value requires available, unredacted numeric identity.
Unmapped identity uses `does_not_exist`; failed lookup uses `error`; lookup not
attempted/unavailable uses `not_collected`, or the optional field is omitted.
Names are resolved against the assessed target, including container/chroot/domain
context, never substituted from a scanner host. Aliases and renames reflect the
identity provider's answer at lookup time, not a claim of permanent uniqueness.
Special process IDs such as an unset login UID must not be resolved as accounts.
Lookup failures do not change numeric ownership or numeric comparison truth.
Name predicates require a separate future authoring/acquisition contract.

Locators use `source_ref` for the exact observed source/snapshot. Text `line` and
optional `column` are one-based; columns count decoded Unicode code points,
not bytes or UTF-16 units. Do not emit a column if the collector cannot determine
it in those units. Structured locations carry `path_language` and a concrete
`path`, not merely the query selector. Paths use that language's escaping and
namespace conventions; root locations may be omitted when no useful nonempty
path is available. Record `index` is zero-based within the identified acquired
source result, not a database key or stable cross-scan identity. Optional `field`
references an emitted Item field, `value_index` selects an emitted repeated
typed value, and `property` selects a named property of its record payload.
Indices, properties and types preserve row correlation. Sources that supply no
reliable position omit the locator. A config location explains the declaration
actually observed; it does not assert effective configuration or precedence.

Imported Items retain full observations and original lookup context locally so
the consuming Assessment Result remains understandable. `imported: true` requires
`context.origin` with `result_ref` and `item_ref` pointing to the original result
and Item. These are provenance links; they do not replace locally required data
with a dependency on another Assessment Result. Importing must not silently
re-resolve identities. Source references and locators are subject to the same
redaction and evidence constraints as fields; sensitive paths, queries or identity
sources must not leak through metadata.

`reported_elements` remains tracked in #125. Its default is all available fields,
subject to redaction and caps. Compared/explicit projections must preserve
decisive evidence, identity and required context and cannot change collection or
evaluation. This prototype validates the canonical Item before projection; it
does not choose the authored placement, precedence or completeness semantics of
the future reporting control. Projection must adjust/remove locators to omitted
fields and must not leave names detached from their required numeric identity.

## Reproduction and known results

Baseline: `ab6e9fb1b291fab389157990e5a66f4d29ed1a97` (merged PR #124).
Source annotations and cardinalities are read from the vendored OVAL 5.12.3
schemas through the maintained capability generator. New names are native
enrichment proposals, not fields asserted to exist in the upstream schema.

```
PYTHONPATH=tools python tools/test_collected_item_contract_v02.py
python tools/collected_item_contract_v02.py --output work/collected-items-0.2.0
```

The generator emits 99 capability Item schemas and two shared experimental
schemas, all meta-validated by the tests. Fourteen focused test methods cover the
eight added name fields across four statuses, closed field vocabularies,
result-only isolation, missing/incorrect provenance, numeric-source requirements,
redaction, absence, all Item statuses, invalid collection/Test statuses,
locators and import provenance. Nine committed cases publish expected structural
and relationship validity in `tests/collected-items-0.2.0/cases.json`.

Structural validation must be followed by `context_errors(item)` for relationships
that JSON Schema cannot express. Passing these cases proves representation and
validation behavior only. It does not prove a collector used the correct target,
lookup time, record association or configuration interpretation. Target tests
for aliases, namespace collisions, renames, identity-service failures and remote
collection remain required before promotion. The complete vendor corpus (#128)
should incorporate these cases and those target scenarios. No reference scanner
or automatic normalizer conversion was added.

Validation: 77 tests passed with `PYTHONPATH=tools python -m unittest tools.test_collected_item_contract_v02 tools.test_schema_issue_regressions tools.test_generate_capability_schema tools.test_generate_windows_file_capability_schema tools.test_generate_windows_registry_capability_schema tools.test_generate_windows_wmi_query_capability_schema`. All 99 experimental Item contracts generated successfully; `git diff --check` passed. No authored Assessment review output was generated, so the authoring-contract checker has no new source tree to inspect.
