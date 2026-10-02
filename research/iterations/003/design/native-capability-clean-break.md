# Native Assessment capability design: clean-break rules

Status: **iteration-003 pre-alpha design direction**

SCAP-NG Assessment capabilities are a clean native design. OVAL 5.12.3,
XCCDF, OCIL and SCAP 1.4 are migration/conformance evidence, not native schema
templates.

## Design rule

When importing legacy content, preserve its **effective meaning**. Do not
preserve a legacy spelling, type hierarchy, hidden default, deprecated value,
serialization workaround, or schema artifact unless that artifact itself has
meaning required by supported content.

The test for a native construct is:

> Would we design it this way if SCAP 1.4/OVAL XML had never existed?

If no, redesign it and make the importer perform the translation.

## Shared native semantics

Cross-capability concepts SHALL be defined once and reused.

Native comparison operations use concise machine-friendly names such as
`equal`, `not_equal`, `equal_ci`, `not_equal_ci`,
`greater_than`, `greater_or_equal`, `less_than`, `less_or_equal`,
`bit_and`, `bit_or`, `match`, `subset`, and `superset`.
Legacy OVAL spellings remain importer vocabulary only.

Native match quantifiers are `all`, `any`, `one`, and `none`.
Deprecated legacy values such as OVAL `none exist` do not become native
quantifiers.

Existence is distinct from matching. Native existence requirements are:
`all`, `some`, `none`, `one`, and `optional`. Collection errors,
unknown/not-collected states, and completeness are evaluated separately rather
than overloaded into existence enum names.

Native authored content SHALL NOT rely on hidden behavior-affecting defaults.
The importer materializes legacy defaults explicitly while preserving
source-explicit/source-implicit provenance outside the native runtime schema.

Variables, Sets, filters, comparison semantics, existence semantics, and
result/evidence semantics are shared Assessment concepts, not capability-local
copies.

## Deprecated legacy features

Deprecated legacy constructs do not enter the native schema merely to ease
conversion. The importer SHALL translate a deprecated construct only when a
semantically equivalent supported native construct exists; otherwise it SHALL
return a migration diagnostic.

## Structural versus semantic validation

JSON Schema validates local structure and values. A versioned semantic validator
handles graph constraints such as Object/State/Variable references, capability
compatibility, Set/filter reference compatibility, datatype compatibility, and
cross-field rules. SCAP-NG SHALL NOT recreate Schematron/XPath graph validation
inside capability JSON Schemas.

## unix.file first stabilization

`unix.file` is the first capability used to prove the clean native model.

### Selectors

Native selectors are:

- `full_path`, or
- `directory` + `name`.

Importer mapping:

- OVAL `filepath` -> `full_path`
- OVAL `path` -> `directory`
- OVAL `filename` -> `name`

### Traversal

Do not reproduce OVAL `FileBehaviors`.

Traversal is downward only. OVAL 5.12.3 explicitly deprecates
`recurse_direction="up"` because it was unused and added unnecessary
interpreter complexity. Native SCAP-NG therefore has no recurse-direction field.

A native traversal object is intentionally small:

```yaml
traversal:
  max_depth: null       # null = unlimited; 0 = starting directory only
  follow_symlinks: true
  filesystem: local     # any | local | same
```

Requirements:

- `max_depth` is a non-negative integer or null; no magic `-1`.
- `follow_symlinks` is boolean.
- `filesystem` is `any`, `local`, or `same`.
- traversal is invalid with `full_path`.
- traversal fields are explicit; there are no hidden behavior defaults.

Legacy OVAL mappings are importer concerns. Deprecated `recurse` values
(`files`, `files and directories`, `none`) and upward traversal do not
become native enum values.

The exact legacy symlink-recursion mappings SHALL be proven with conversion
fixtures before being called final.

### Field naming

Native field names MAY be cleaned up where clarity improves materially.
Candidates for the first slice include:

- `user_id` -> `owner_uid`
- `group_id` -> `owner_gid`
- `suid` -> `setuid`
- `sgid` -> `setgid`

Permission representation should be reconsidered rather than blindly retaining
the legacy collection of individual boolean entities. Any redesign must retain
lossless conversion semantics and have explicit fixtures.

## No OVAL metadata in runtime schemas

Legacy-to-native crosswalks belong in importer mappings, audit reports, and
conversion tests. Generated native capability schemas SHALL NOT expose
`x-oval-*` metadata as part of the runtime contract.

## Change tolerance

This is pre-alpha. Common definitions are centralized, capability mappings are
small reviewed inputs, generated schemas are disposable, and semantic
conversion tests are the safety net. Current OVAL schema structure is not a
compatibility commitment.


## unix.file permission representation decision

For the first stabilized native `unix.file` capability, permissions remain
individually addressable boolean State fields, using descriptive native names:

- `owner_read`, `owner_write`, `owner_execute`
- `group_read`, `group_write`, `group_execute`
- `other_read`, `other_write`, `other_execute`
- `setuid`, `setgid`, and `sticky`

SCAP-NG deliberately does **not** carry forward the terse OVAL names
(`uread`, `gwrite`, etc.).

A single octal mode/bitmask was considered but is not the current design. It
would combine independently testable policy facts into one encoded value and
would complicate partial comparison, Variables, and human-readable result
evidence. The explicit booleans are therefore the simpler semantic model even
though they use more field names.

This decision MAY be revisited based on real author/scanner experience, but any
future grouping SHALL preserve independently addressable permission semantics
and lossless conversion.
