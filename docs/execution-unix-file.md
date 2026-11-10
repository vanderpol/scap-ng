# Native 0.4 `unix.file` execution mapping

This note accompanies the RI Issue #43 first execution slice. It documents an
implementation subset; it does not modify a frozen schema.

## Native mapping

The canonical `unix.file` Object is defined by
[`native-selector.schema.json`](../schema/native-selector.schema.json) and the
shared Object rules in
[`capability-common.schema.json`](../schema/capability-common.schema.json).
A `filepath` selector is a typed Object selector, independent of the Test
`require` predicates. The RI slice supports the exact absolute-file form:

```json
{"filepath":{"equals":"/etc/passwd"}}
```

An Assessment-scoped `shared_objects` entry resolves to the same logical
Object shape. Object titles are presentation metadata and are not part of the
selector digest. A collector may share a compatible physical observation, but
each Test retains its own Object digest, projection, Binding, Filter/Set
context, and logical population.

The selected fields are native collected Item fields. `owner_uid` and
`owner_gid` are Unix metadata; `size`, `type`, `directory`, `name`, and
`full_path` are materialized observations. Authored `path`/`filename` selectors
are outside this exact-file slice. No missing Item is fabricated.

## OVAL 5.12.3 correspondence

The source-pinned OVAL independent file definition remains the compatibility
reference, not an equivalence claim. In particular:

* `filepath` corresponds to the OVAL file object's exact filepath entity;
* `recurse_file_system` is a source semantic, not an RI default override;
* the canonical schema records the OVAL declaration and source digest for the
  filesystem-scope vocabulary;
* this slice does not implement recursive search, the OVAL `path` + `filename`
  population, symlink traversal, or a complete absence/error precedence table.

The unresolved choices are intentionally surfaced as result diagnostics:
missing file, denied access, unsupported operation, and incomplete evidence
are not converted to a technical `false`.

## Result safety

The RI emits the frozen 0.4 result shape with decisive summaries, counts,
completeness, opaque per-execution evidence references, and acquisition
interval/provenance. It omits collected paths and values from emitted Results.
The memory evidence backend owns the actual Item during the run; the existing
SQLite Source/Store contracts are not changed.

## RI Issue #43 qualification note

The linked RI qualification establishes an important execution boundary: a
successful non-root `lstat` is acquisition success, not proof of complete
collection or authoritative evidence. Root is the intended production mode for
the exact-file lane, scoped to the current mount namespace. Non-root execution
records its privilege and visibility limitations; an observed decisive failure
may remain `false`, while an apparent pass is `unknown` when population
completeness cannot be established.

The RI currently uses the frozen Result booleans and free-form `evidence`
provenance member to report acquisition, completeness, and trust separately.
Internally, the RI carries these facts as a typed acquisition receipt through
its existing Source boundary; the receipt is not a new native Result member.
The RI evidence entry uses the documented keys `acquisition_status`, `collection_ref`, `collector`,
`authority`, `acquired_at`, `completed_at`, `duration_ns`, `privilege_mode`,
`observation_scope`, `trust`, and `limitations`; these remain implementation
metadata, not native Result members.
The frozen canonical schemas do not yet define a portable privilege,
observation-scope, or evidence-trust vocabulary. That is a contract gap for a
future coordinated canonical change; this documentation increment does not
alter schemas, generated outputs, or goldens.

For symlinks, the RI uses `lstat`, rejects a final symlink as
`unsupported_operation`, and never silently follows it. Canonical SCAP-NG and
pinned OVAL 5.12.3 references do not by themselves authorize an RI-specific
final-link, recursive-link, mount-boundary, or race-resistance policy. Future
implementation must be coordinated before traversal or symlink collection is
enabled.

The RI branch also includes a runnable RHEL-style sample Assessment and
redacted Result qualification examples for normal-user and root execution:
[RI PR #51](https://github.com/vanderpol/scap-ng-ri/pull/51).
