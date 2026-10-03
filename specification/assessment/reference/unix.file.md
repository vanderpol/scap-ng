# Unix file assessment — `unix.file`

**Status:** working 0.1.0 capability contract with draft 0.2.0 result-only names
and reporting controls. Field/reference validation is tested; this repository
does not yet establish a conforming live Unix collector.

## Purpose and source

Use this capability to select Unix filesystem entries and compare identity,
numeric ownership, file mode bits, times, size, or extended-ACL presence. It
does not read file contents or establish effective access for an arbitrary user.
The Test references an Object; referenced States and filter States must use
`unix.file` too. Variables can extract fields from a typed Object through the
shared dataflow model.

[Native mapping](../../../schema/v0.1.0/capability-mappings/unix.file.json)
adapts the vendored OVAL 5.12.3 `file_test`, `file_object`, `file_state`, and
`file_item` contracts. [Shared assessment behavior](shared-behavior.md) defines
quantifier order, collection statuses, and result propagation.

## Object selection and filesystem scope

| Selector | Datatype | Meaning and valid combination |
| --- | --- | --- |
| `full_path` | string predicate | Absolute file pathname; exclusive alternative to `directory`/`name`. A directory is selected through the directory alternative. |
| `directory` | string predicate | Directory component of the pathname; requires `name`. |
| `name` | string predicate or null | Filename within `directory`. Null selects the directory itself. |

Predicates declare `datatype`, `operation`, and `value`; values may reference
Variables. Shared Set/filter Object forms are available. `filesystem` is required
for direct selection and is independent of recursion:

| `filesystem` | Meaning |
| --- | --- |
| `any` | Search without the local/same filesystem restriction. |
| `local` | Restrict to local filesystems. |
| `same` | Restrict to the filesystem defined by the selected starting path. |

These map the inherited `all`, `local`, and `defined` filesystem scopes. Exact
path selection still carries filesystem scope; it is not ignored just because
the Object has no traversal. Platform-specific filesystem classification and
live mount behavior require collector conformance cases.

Optional `traversal` uses shared [file traversal primitives](../../../schema/v0.1.0/capability-common.schema.json).
It declares `max_depth` (nonnegative integer or null for unbounded) and `recurse`
(`directories`, `symlinks`, or `symlinks_and_directories`). Omit traversal for no
recursion. The native form retains the supported Unix recursion choices and
does not expose an upward direction. Traversal is invalid with `full_path` or
with non-equality directory selection. These restrictions require semantic checks
in addition to structural validation; do not assume a generic JSON Schema check
has resolved filter compatibility or every traversal combination.

## Comparable and collected fields

The following fields are available for State comparison and canonical Item
evidence. Each collected field has a typed status-bearing value; absence,
collection failure, and redaction are not ordinary successful literal values.
These scalar fields do not acquire extra multiplicity merely because an Object
returns multiple Items.

| Native field | Datatype | Meaning and units | OVAL field |
| --- | --- | --- | --- |
| `full_path` | string | Absolute file pathname. | `filepath` |
| `directory` | string | Directory component of the absolute pathname. | `path` |
| `name` | string | Filename; directory-selection null semantics belong to the Object selector and corresponding source Item identity. | `filename` |
| `type` | string | File type, such as regular file, directory, FIFO, symbolic link, socket, or block special. Examples are not an additional native enum restriction. | `type` |
| `owner_gid` | integer | Numeric group owner. | `group_id` |
| `owner_uid` | integer | Numeric user owner. | `user_id` |
| `access_time` | integer | Last access time in seconds since the Unix epoch. | `a_time` |
| `change_time` | integer | Last inode/status change time in seconds since the Unix epoch; not creation time. | `c_time` |
| `modify_time` | integer | Last content modification time in seconds since the Unix epoch. | `m_time` |
| `size` | integer | Size in bytes. | `size` |
| `setuid` | boolean | Set-user-ID mode bit. | `suid` |
| `setgid` | boolean | Set-group-ID mode bit. | `sgid` |
| `sticky` | boolean | Sticky mode bit. | `sticky` |
| `owner_read` | boolean | Owner read mode bit. | `uread` |
| `owner_write` | boolean | Owner write mode bit. | `uwrite` |
| `owner_execute` | boolean | Owner execute/search mode bit. | `uexec` |
| `group_read` | boolean | Group read mode bit. | `gread` |
| `group_write` | boolean | Group write mode bit. | `gwrite` |
| `group_execute` | boolean | Group execute/search mode bit. | `gexec` |
| `other_read` | boolean | Other-user read mode bit. | `oread` |
| `other_write` | boolean | Other-user write mode bit. | `owrite` |
| `other_execute` | boolean | Other-user execute/search mode bit. | `oexec` |
| `has_extended_acl` | boolean | Presence of an ACL extending ordinary Unix permissions; see status distinction below. | `has_extended_acl` |

The Unix epoch is 1970-01-01 00:00:00 UTC. Read/write/execute fields describe
mode bits, not a complete access-control decision incorporating ACLs, privileges,
mount options, or mandatory access controls. Likewise, the presence of set-ID or
sticky bits does not by itself prove an operating system will grant a particular
effective privilege or permit deletion.

For `has_extended_acl`, the inherited source distinguishes three cases: supported
ACL facility with an extended ACL is `exists`/true; supported facility without an
extended ACL, or one matching ordinary Unix permissions, is `exists`/false;
unsupported ACL facility is `does_not_exist`. Do not report false merely because
ACL support is unavailable. State-entity existence and status propagation apply
before value comparison.

## Draft 0.2.0 result-only fields

| Native field | Datatype | Meaning | Required numeric relationship |
| --- | --- | --- | --- |
| `owner_user_name` | string | Optional resolved display name for the numeric user owner. | `owner_uid` |
| `owner_group_name` | string | Optional resolved display name for the numeric group owner. | `owner_gid` |

Names are optional evidence, never Object selectors or State predicates. They
must not replace numeric identity or change a numeric comparison. Name resolution
has [lookup provenance and status requirements](../../../tests/collected-items-0.2.0/README.md);
failure to resolve a name is not proof that the file or numeric owner is absent.
Unavailable/redacted numeric identity must not be indirectly disclosed through
a resolved-name value. The approved relationships are recorded in
[result field extensions](../../../schema/v0.2.0/result-field-extensions.json).

## Tests, reports, and known results

A file Test declares `object`, `existence`, and `match`. It may reference States
and use `states_match` to combine them. Missing resources, failed collection,
incomplete population, and unavailable fields use the [shared semantic rules](shared-behavior.md),
not a capability-specific conversion to false or empty collection.

[Ownership Assessment](../../../tests/reported-elements-0.2.0/ownership.assessment.yaml)
selects `/fixture/config`, requires numeric UID 0, and requests
`reported_elements: [owner_uid, owner_user_name]`. The controlled [recorded
observations](../../../tests/assessment-results-0.2.0/ownership-observations.json)
have UID 1001, so the ownership comparison is false regardless of the display
name. The result fixture records that comparison; the result helper validates
its consistency and does not independently acquire the file or recompute every
comparison.

[Expected report selections](../../../tests/reported-elements-0.2.0/expected-results/field-selections.json)
demonstrate omitted/default `all`, explicit `all`, `compared`, selected owner/name,
an empty array, and a known unavailable field. `compared` retains `full_path` and
`owner_uid` in this fixture. An explicit empty list still retains those required
identity/decisive fields. Canonical evidence remains intact; redaction remains
binding even when a field is requested.

From the repository root, run:

```sh
python tools/test_generate_capability_schema.py
python tools/test_validate_generated_capability_semantics.py
python tools/test_reported_elements.py
python tools/test_assessment_results_v02.py
```

These checks cover field/selector validity, semantic restrictions, derived
reporting, and synthetic result consistency. They do not prove live Unix
acquisition, traversal, ACL interpretation, symlink behavior, or name resolution.
Broader zero/one/many, denied-access, mount, permission, ACL, and time boundary
target cases remain in #128/#131.

## Provenance and remaining work

Adapted field descriptions come from the pinned vendored
[Unix definition schema](../../../third_party/scap-1.4-schemas/oval_5.12.3/unix-definitions-schema.xsd)
and [Unix Item schema](../../../third_party/scap-1.4-schemas/oval_5.12.3/unix-system-characteristics-schema.xsd),
using the `file_object`, `file_state`, and `file_item` element documentation.
Native naming, traversal, resolved names, and reporting differences follow the
reviewed mappings and owner working decisions. [Source ledger](sources.json)
pins the inspected bytes and the NG checkpoint. Complete target-level behavior
and independent vendor equivalence remain unproven.
