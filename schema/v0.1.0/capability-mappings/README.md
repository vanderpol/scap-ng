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

## Current reviewed capabilities

The capability-schema design now includes the original diverse proof cases plus
the production-first translation tranche. Each listed capability has a reviewed
mapping; focused regression coverage is maintained in `tools/test_generate_*.py`
or a grouped capability regression.

- `unix.file` — native file metadata and shared Unix/Independent file traversal;
- `file.hash` — shared file selection plus required collection parameter;
- `windows.file` — Windows file selection with junction-aware traversal;
- `windows.registry` — hierarchical non-filesystem traversal and typed values;
- `variable.value` — direct Test source with no fake Object;
- `windows.wmi.query` — collector-driven query plus structured record State;
- `linux.rpminfo` — package metadata and explicit source-default materialization;
- `independent.textfilecontent54` — file traversal, regex match/instance selection, and explicit regex/item-creation behaviors;
- `windows.auditeventpolicysubcategories` — singleton system source with deprecated state entity excluded;
- `windows.userright` — user-right enumeration with trustee name/SID state;
- `independent.shellcommand` — command-oriented collection with trust/security guardrails;
- `unix.sysctl` — kernel parameter collection;
- `linux.partition` — mounted partition metadata and effective mount options;
- `linux.systemdunitproperty` — unit/property collection;
- `windows.fileeffectiverights53` — trustee-SID effective rights with shared Windows traversal;
- `windows.cmdlet` — structured record-valued PowerShell invocation and result predicates;
- `unix.symlink` — canonical symbolic-link target resolution;
- `windows.lockoutpolicy` — singleton system lockout policy;
- `windows.passwordpolicy` — singleton system password policy;
- `unix.password` — UNIX passwd account metadata with existing OVAL field terminology preserved;
- `unix.shadow` — shadow password-aging metadata using the shared canonical State/Item field model;
- `linux.selinuxsecuritycontext` — file/process SELinux context collection with shared file traversal and PID selection;
- `unix.interface` — interface metadata including multi-valued flags.

The next tranche covers lower-frequency production candidates and then the
remaining supported Self-Assertion language-conformance surface. Capabilities
SHOULD continue to reuse shared primitives and SHALL NOT be bulk-generated from
XSD names without semantic review.

## Source-governance caveat for Windows extension families

Some current Windows-native mappings were prototyped from production/SCC semantics and system-characteristics Item shapes even though the corresponding Test/Object/State family is absent from the official OVAL-Community v5.12.3 Windows definitions schema. These mappings SHALL NOT be described as standard OVAL 5.12.3 migration mappings until their exact publisher-extension provenance is identified and recorded. Native SCAP-NG design work may continue, but the standard migration crosswalk must distinguish standard OVAL from publisher extensions.


## Content-backed standard checkpoint — 2026-10-02

The reviewed mapping directory now covers every currently inventoried **standard OVAL 5.12.3 capability candidate with concrete production, Self-Assertion, validation, or other checked-in content evidence**.

This checkpoint intentionally does not bulk-complete schema-only candidates. Those remain inventoried and deferred until concrete usage evidence or a higher-priority standards requirement appears.

Remaining Windows content-backed names that lack official OVAL-Community v5.12.3 Test/Object/State definitions are tracked as publisher-extension provenance work rather than mislabeled as standard OVAL mappings.

The mapping files in this directory are the authoritative reviewed capability registry; historical crosswalk tables may lag while documentation is regenerated.
