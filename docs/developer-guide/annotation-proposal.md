# Proposed annotation authority

**Owner review required; no canonical grammar change in this PR.** Retain all
0.4.0 schema bytes. Trial documentation annotations outside `schema/`; consider
migration only in a future schema version. Annotation approval does not approve
new collection semantics or confer scanner qualification.

## Ownership

| Information | Current authority | Generated consumers |
| --- | --- | --- |
| Structure, references, required properties | JSON Schemas | Shared structural reference, fixture validation |
| Capability selectors, parameters, evidence types, semantic rules | Capability mappings; resolved native selector contracts override source-conversion operator spellings | Author and scanner columns in each platform guide |
| Reviewed explanatory prose | `docs/metadata/schema-documentation-pilot.json` | Both audiences, through one documentation model |
| Legacy provenance | `docs/metadata/developer-guide-oval-audit.json` | Pilot review, reproducible source audit |
| Runtime qualification evidence | `scanner-guidance-status.json` | Existing scanner coverage catalog; no new qualified record |

Do not maintain separate author and scanner copies of datatype lists, enums or
required flags. The generator reads them from contracts. `description` serves
author help; an implementer extension supplies only details not derivable from
structure. Source-conversion labels such as `pattern_match` are not native
selector operators; use the resolved contract's `matches_regex`.

## Proposed field annotation shape

The version-2 trial sidecar demonstrates this minimal extension. Mapping-relative
RFC 6901 pointers must resolve; unknown capabilities, platform mismatches,
orphan fields, missing facts/questions and qualification upgrades fail generation.

```json
{
  "description": "Select a canonical registry hive.",
  "x-scap-ng-scanner": {
    "documentation_status": "partially_documented",
    "known_contract": "The hive uses the canonical enum.",
    "contract_refs": ["/native/selector_value_enums/hive"],
    "open_question": "How are unavailable hives represented?",
    "source_lineage": [{
      "audit_node": "windows.registry/registry_object",
      "disposition": "legacy_candidate"
    }],
    "qualification_status": "not_established"
  }
}
```

These are documentation keys, not authored Assessment properties. Current
sidecar `properties` addresses Object selectors and collection parameters.
Collected fields and comparison fields are separate roles in the generated
model: `field_datatypes` describes collected evidence;
`state_field_datatypes` supplies comparison overrides. They must never be
collapsed into one datatype list.

For expansion, recommend extending this same vocabulary to explicit role maps
(`selectors`, `collection_parameters`, `collected_fields`, `comparison_fields`)
with capability-level `source_lineage`, `open_questions`, and `qualification`.
Each lineage record should contain source URI at an immutable revision, file
hash, element pointer, paraphrase, and disposition (`native_contract_reference`,
`legacy_candidate`, or `rejected`). Qualification should reference test evidence
and reviewer approval separately from documentation status. Do not encode
unresolved questions as defaults or assertions. This role-map expansion is a
proposal, not a second implemented annotation format.

## Migration decision

Recommend approving the ownership model and trial vocabulary now, then reviewing
the role-map extension against five more capabilities before adopting it in a
future-version canonical schema-generation pipeline. That pipeline should emit
both schema annotations and guides from one source, then remove the temporary
sidecar. Alternatives are keeping the sidecar permanently (simpler migration,
but weaker co-location) or manually authoring two guides (creates duplicate
authority; not recommended). No option requires rewriting frozen 0.4.0.

## Required shared-model sections

Every capability exposes all five sections, including explicitly unresolved ones:

| Section | Contents |
| --- | --- |
| Authoring contract | Selectors, native operators, literal datatypes, scoped variable/Input references, collection parameters and closed-overlay controls |
| Collection contract | Selection reference, returned fields, datatypes/enums, acquisition contract or explicit gap |
| Evaluation contract | Shared requirements, comparisons and cardinalities; datatype overrides and native rules; missing/error decision-table coverage |
| Provenance | Native contract references and separately classified legacy audit nodes, with scope and legacy-review status |
| Documentation status | `verified`, `partially_documented`, or `unresolved`, independent of runtime qualification |

`verified` identifies mechanically checked source projections/references, not
scanner equivalence. A capability can have verified variable syntax and source
references while acquisition and error mappings remain unresolved; its overall
status stays partially documented. Existing source-backed rules remain in force
when the complete decision table is missing. The model never promotes legacy
OVAL prose to native behavior to fill a gap.

The generated [shared contract reference](../generated/developer-guide-contract-model.md)
resolves the actual schema definitions; platform pages and the machine ledger
show section status. This is documentation structure only, outside frozen grammar.
