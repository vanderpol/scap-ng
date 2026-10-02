# Capability Schema Mapping Sources

These files are the reviewed source-to-native design inputs for generated
SCAP-NG Assessment capability schemas.

They are **not** runtime schemas and they are **not** mechanical OVAL-to-JSON
translations.

## Clean-break rule

SCAP-NG capability mappings preserve legacy **semantics**, not legacy schema
shape.

Pinned OVAL 5.12.3 XSD/Schematron is used to prove migration coverage and to
identify source behavior, hidden defaults, deprecated constructs and source
defects. Native names, structure, enums and validation rules are designed
independently.

A native capability SHOULD answer:

> Would we design it this way if the OVAL XML schema had never existed?

If not, the mapping translates the source construct into a clearer native form
or records an explicit migration error.

## Ownership model

For each supported capability:

1. `source` identifies the pinned legacy Test/Object/State family used as
   migration evidence.
2. `native` defines the native capability shape consumed by
   `tools/generate_capability_schema.py`.
3. `migration_crosswalk` records how source constructs map into native NG and
   which legacy constructs are deliberately removed.
4. `semantic_validator_rules` records graph/cross-field requirements that do
   not belong in local JSON Schema.
5. Generated capability schemas are disposable build artifacts. They SHALL be
   regenerated from the mapping + shared native schema primitives.
6. A capability is not considered covered merely because a JSON Schema exists;
   focused semantic fixtures and corpus validation are also required.

Exact source names include historical OVAL version suffixes. Owner
clarification, 2026-10-02: `wmi57` identifies the OVAL 5.7 revision and
`textfilecontent54` the OVAL 5.4 revision. A native name may be simplified only
with an explicit mapping; do not silently strip suffixes across the inventory
or accept a deprecated predecessor. The
[reviewed crosswalk](../../../specification/migration/oval-5.12.3-capability-crosswalk.md#reviewed-native-mappings-override-the-provisional-inventory)
links each current mapping and distinguishes unmapped candidates.

## Supported native mapping patterns

### Selector-driven Object

Use `selector_map` and `object_selector_alternatives` when the Object is
defined by predicates over system identity fields.

Examples:

- `unix.file`
- `windows.file`
- `windows.registry`

Selectors use shared comparison/entity semantics. Capability mappings SHOULD
not duplicate operation, datatype, Variable or quantifier definitions.

### Collector-driven Object

Use `collection_parameters` when values are inputs to collection rather than
predicates over an already collected object.

Examples:

- `file.hash.collect.algorithm`
- `windows.wmi.query.collect.namespace`
- `windows.wmi.query.collect.query`

A required collection parameter applies to direct collection only. A Set-based
Object combines referenced Objects and SHALL NOT inherit unrelated direct
collector parameters.

Collection parameters MAY allow named Variable references when the source
semantics permit a runtime-supplied value.

### Direct Test source

A Test MAY reference a non-Object source directly when an Object adds no native
meaning.

Example:

- `variable.value` references a named Variable directly and does not create a
  fake `variable_object`.

Automated Assessments therefore do not require empty Object or State sections
when a capability does not use them.

### Scalar State

Scalar predicates use shared native entity semantics:

- explicit comparison operation;
- explicit native datatype;
- explicit mask/redaction intent;
- match quantifier;
- existence requirement;
- Variable references where permitted.

Behavior-affecting legacy defaults are materialized by importers rather than
hidden in authored native content.

### Record State

Record-producing capabilities use the shared native record predicate.

A record is a map keyed by field name, which makes field uniqueness structural
instead of an external XML uniqueness constraint.

Record fields may contain:

- scalar predicates;
- nested record predicates;
- list predicates.

This intentionally removes the OVAL record limitation that forced WMI57 and
similar capabilities to simple datatypes only.

Example:

- `windows.wmi.query`

SQL, cmdlet and other record-producing capabilities SHOULD reuse the same
record model unless they have a genuinely different semantic need.

### Shared traversal

File-family capabilities use the shared downward-only file traversal primitive.

It replaces legacy `max_depth=-1`, `recurse`,
`recurse_direction=none/down/up` and duplicated file-system-scope behavior
with:

- explicit non-negative/null depth;
- explicit symlink following;
- explicit filesystem scope.

Upward recursion is intentionally absent.

Registry and other hierarchical stores use a separate shared hierarchy
traversal primitive when filesystem semantics do not apply.

### Sets and filters

Set expression, operands and State filters are shared native concepts.
Capability mappings SHALL NOT redefine them.

Direct collection and Set composition are separate Object modes.

## Review rules

A mapping change SHOULD state whether it:

- preserves source semantics;
- fixes a legacy design flaw;
- simplifies/removes a legacy serialization artifact;
- changes native terminology;
- moves a rule to shared schema or semantic validation;
- rejects a deprecated construct;
- introduces a migration diagnostic.

Removal of a legacy feature that could affect supported content SHALL also be
tracked in the migration disposition documentation.

## Current reviewed capability status

The content-backed OVAL 5.12.3 migration surface is now reviewed across the current Independent, Linux, Unix, macOS, Solaris, and Windows tranche used by production content and/or SCAP Self-Assertion / validation content.

The authoritative per-capability inventory, source Test names, evidence counts, reviewed native names, and deferred schema-only candidates are maintained in the [OVAL 5.12.3 capability crosswalk](../../../specification/migration/oval-5.12.3-capability-crosswalk.md).

Important checkpoints:

- production-heavy capabilities are complete;
- lower-frequency production mappings are complete;
- content-backed Windows mappings are complete;
- reviewed native renames such as `filehash58 → file.hash`, `variable → variable.value`, and `wmi57 → windows.wmi.query` count as covered migration surface;
- schema-only candidates without concrete content evidence remain intentionally deferred;
- every reviewed capability mapping is covered by the maintained State/Item parity and generated-schema gates.

The project has now entered the repository-wide validation phase. Current fresh native content is validated structurally with JSON Schema, then by Assessment semantic-graph validation, then by cross-document package-graph validation. The same gates run again after normalization so normalization cannot preserve local schema validity while breaking references or capability semantics.

Historical/example artifacts are audited separately from the normative current-content gate and are triaged before any schema or content change.

## Windows schema verification note

The approved Windows OVAL families are present in the authoritative OVAL-Community v5.12.3 Windows definitions schema and in the checked-in SCAP-NG copy. During review, the GitHub connector's normal file-content endpoint returned an empty payload for the large (~1.17 MB) XSD, which initially created a false appearance that these definitions were missing.

Verification by Git blob SHA/content confirmed the checked-in Windows definitions XSD matches the authoritative OVAL-Community v5.12.3 blob and contains the approved families. This was a retrieval/tooling artifact, not a SCAP 1.4 schema defect.

The only currently known SCC/NIWC custom Test/Object/State family in this workstream is `independent:sqlext`.


## Content-backed standard checkpoint — 2026-10-02

The reviewed mapping directory now covers every currently inventoried **standard OVAL 5.12.3 capability candidate with concrete production, Self-Assertion, validation, or other checked-in content evidence**.

This checkpoint intentionally does not bulk-complete schema-only candidates. Those remain inventoried and deferred until concrete usage evidence or a higher-priority standards requirement appears.

Remaining Windows content-backed names that lack official OVAL-Community v5.12.3 Test/Object/State definitions are tracked as publisher-extension provenance work rather than mislabeled as standard OVAL mappings.

The mapping files in this directory are the authoritative reviewed capability registry; historical crosswalk tables may lag while documentation is regenerated.
