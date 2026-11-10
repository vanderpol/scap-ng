# `unix.file`: Linux basic collection prototype

**STOP/GO prototype for [#35](https://github.com/vanderpol/scap-ng/issues/35).**
Hand-authored and source-checked; Jack's review is pending. This is an acquisition
recipe for an experimental adapter, **not** a qualified native collector.
[N] below identifies a recorded native contract. [P] is an implementation
suggestion or unadopted mapping. No OVAL rule becomes native by implication.
The [comparison ledger](unix-file-comparison.json) gives every claim ID's exact
pinned native/OVAL source and platform API reference. The
[reviewer sheet](unix-file-review.md) records **FAIL** for demonstrated overall
superiority and recommends stopping expansion.

## Input and supported subset

[N] Author the selectors as `filepath`, or `path` plus `filename`. Returned
names are `full_path`, `directory`, `name`; do not feed these returned names
back into the closed Object grammar. `filename: null` selects the directory
itself; it is not an empty filename or a wildcard. The resolved contract also
supports other string operations and value references. **This prototype handles
only scalar `equals` selecting an existing regular file**, using either form:

```yaml
# Form A
{filepath: {equals: /fixture/config}, filesystem: all}
# Form B — same selected identity in this prototype
{path: {equals: /fixture}, filename: {equals: config}, filesystem: all}
```

[P] The profile requires an absolute, non-root file path with nonempty final
name, no embedded NUL, no `.`/`..`, repeated separators or trailing separator.
These restrictions bound the prototype; they are **not new native validation
rules**. Work in the explicitly selected local Linux filesystem namespace, not
an assumed guest/container/remote namespace. Keep the selected lexical identity;
do not replace it with `realpath()` or a pathname reconstructed from an inode.
Claims: `selector-filepath`, `selector-path`, `selector-filename`,
`selector-operators`, `directory-null`, `scope`.

Only 21 core fields are covered below. Non-regular types, directory Objects,
arrays/references, non-equality matching, discovery, Sets/Filters, traversal,
`filesystem: local/same`, size and ACL acquisition are outside this recipe.
Report unsupported coverage rather than pretending that the full capability
was collected. In particular, do not infer `has_extended_acl: false` from a
successful metadata query. Claims: `traversal`, `excluded`.

## Collection path

[P] Suggested Linux calls; include `<fcntl.h>` and `<sys/stat.h>`. On glibc,
define `_GNU_SOURCE` before the headers to expose `O_PATH`. Select an ABI whose
metadata types represent the observed values; no 32-bit range/time guarantee is
made. These are implementation choices, not additions to SCAP-NG:

1. Resolve the bounded input into `parent` and a **single-component** `leaf`.
   Form B already supplies both. Retain the selected strings for the Item.
2. Open the parent using `open(parent, O_PATH | O_DIRECTORY | O_CLOEXEC)`.
   `O_PATH` is Linux-specific; a different POSIX implementation needs its own
   reviewed directory-descriptor strategy. No file-content read is needed.
3. Call `fstatat(parent_fd, leaf, &st, AT_SYMLINK_NOFOLLOW)`. Save `errno`
   immediately on failure; do not inspect an uninitialized `struct stat`.
   Closing the parent descriptor belongs on every exit path.
4. On success, test `S_ISREG(st.st_mode)`. Only then apply this profile's field
   table. A symlink result is **outside the profile**, not proof that its target
   is absent. Do not retry it with `stat()` and silently substitute target data.
5. Build the illustrative typed fields from this observation; record which
   query and target namespace supplied them. Do not claim an atomic snapshot:
   Linux can return fields observed at different moments even in one `stat`
   call. A parent descriptor limits some pathname races but does not prevent
   ancestor symlinks, enforce mount containment or pin the leaf after the call.
6. Keep acquisition independent of Require evaluation. This guide emits no
   Test/Assessment truth value. The compatible evaluation kernel owns that step.

The metadata query does not require read permission on the file itself. Search
permission on path components still matters; file mode `000` is therefore not
a reliable denial fixture. A privileged process may also bypass a mode denial.
Use the errno table rather than checking `access()` before querying.
Claims: `acquire`, `races`, `status-denied`.

Sources: [Linux `stat(2)`](https://man7.org/linux/man-pages/man2/stat.2.html#DESCRIPTION),
[`open(2)`](https://man7.org/linux/man-pages/man2/open.2.html#DESCRIPTION), and
[POSIX.1-2017 `fstatat`](https://man7.org/linux/man-pages/man3/fstatat.3p.html#DESCRIPTION).
The latter is a licensed POSIX reproduction; it is not a claim that all UNIX
systems expose the Linux-specific flags above.

## Field-to-acquisition map

[N] Field names and datatypes are frozen. [P] Acquisition and interpretation
below are the prototype choices. Read all three timestamps and every mode flag
from the **same returned structure**, not separate shell commands. The ledger
has one `field-<native-name>` record per row/field with native JSON pointers and
exact OVAL Item and State documentation lines.

| Native Item field ← authored/source name | Query / extraction | Units and normalization | Remaining decision / error |
| --- | --- | --- | --- |
| `full_path` ← `filepath` | Selected path, no filesystem query | String, retained lexical identity | D-scope: general normalization/alias identity; do not invent it from `realpath` |
| `directory` ← `path` | Selected parent | String, `/fixture` in the example | D-scope; pathname bytes/encoding beyond this ASCII profile remain open |
| `name` ← `filename` | Selected leaf | String, `config` | D-scope; directory/null form is excluded |
| `type` ← `type` | `S_ISREG(st_mode)` | [P] string `regular` | D-type: native mapping has no type-token enum; source spelling is proposed |
| `owner_uid` ← `user_id` | `st_uid` | Exact integer ID in the selected namespace, no account lookup | Preserve numeric width; query failure supplies no value |
| `owner_gid` ← `group_id` | `st_gid` | Exact integer group ID, no name lookup | Same constraint; do not narrow through signed/float casts |
| `owner_read`, `owner_write`, `owner_execute` ← `uread/uwrite/uexec` | `(st_mode & S_IRUSR/S_IWUSR/S_IXUSR) != 0`, separately | Three booleans | D-permissions: raw bits proposed, not effective access |
| `group_read`, `group_write`, `group_execute` ← `gread/gwrite/gexec` | `S_IRGRP/S_IWGRP/S_IXGRP`, separately | Three booleans | Same; retain all three flags |
| `other_read`, `other_write`, `other_execute` ← `oread/owrite/oexec` | `S_IROTH/S_IWOTH/S_IXOTH`, separately | Three booleans | Same; ACLs may give different effective rights |
| `setuid` ← `suid` | `(st_mode & S_ISUID) != 0` | Boolean | D-permissions: a set bit does not prove a privilege transition |
| `setgid` ← `sgid` | `(st_mode & S_ISGID) != 0` | Boolean | Same; mount/execution policy is not queried |
| `sticky` ← `sticky` | `(st_mode & S_ISVTX) != 0` | Boolean bit observation only | D-permissions: POSIX restricted deletion concerns directories; no regular-file deletion-right claim |
| `access_time` ← `a_time` | `st_atim.tv_sec`, retain `tv_nsec` separately | [P] integer seconds since Unix epoch | D-time: native epoch/unit/precision unadopted; avoid floating conversion |
| `change_time` ← `c_time` | `st_ctim.tv_sec`, retain `tv_nsec` | [P] epoch seconds, inode/status change, **not creation** | Same; do not substitute birth time |
| `modify_time` ← `m_time` | `st_mtim.tv_sec`, retain `tv_nsec` | [P] epoch seconds, data modification | Same; returned `tv_sec` avoids inventing negative-time rounding |

The nine ordinary permission flags plus three special flags are twelve separate
fields. Store typed booleans, not an octal string. Preserve raw nanoseconds in
implementation evidence if the proposed integer-second example is used; this
does not approve loss of precision for native comparisons. `ctime`, owner IDs
and mode bits can change independently of file contents.
[POSIX `sys/stat.h`](https://man7.org/linux/man-pages/man0/sys_stat.h.0p.html#DESCRIPTION)
defines the members/macros; [Linux `stat(3type)`](https://man7.org/linux/man-pages/man3/stat.3type.html#SYNOPSIS)
shows the timestamp members. POSIX does not guarantee ordinary permission bits
on symlinks as if they were regular files; this prototype makes no such claim.

## Failure and status path

[N] A native collected Item has `exists`, `error` or `not_collected` status;
**do not create a `does_not_exist` Item**. Native typed fields have a separate
status, including `does_not_exist`; an error/non-collected/absent typed field
must not carry a `value`. Collection status is not a Boolean. `error` and
`incomplete` collection records require nonempty `stop_reason` and diagnostics;
`incomplete` also requires `population_complete: false`.
Claims: `status-item`, `status-field`, `status-collection`.

[P] The following **errno-to-native mappings are not adopted**. The OS error
meaning is sourced; the suggested native record is a review proposal:

| Observation | Proposed handling in this profile | What must not be inferred |
| --- | --- | --- |
| Parent and query succeed; regular file | One `exists` Item; collection `complete` under the controlled-fixture assumptions | Full `unix.file` support or an atomic system snapshot |
| Parent pinned; final no-follow leaf query returns `ENOENT` | Only if the fixture independently establishes absence: zero Items; collection `does_not_exist` | `ENOENT` alone does not prove global absence; controls can hide existence |
| Parent open or query reports `EACCES` | Zero fabricated Items; collection `error`, population unknown/incomplete, diagnostic | Successful absence, or failure because the **file's** read bit is clear |
| `ENOTDIR`, `ELOOP`, `EOVERFLOW`, `EIO`, or other errno | Record the query failure; do not serialize failed-buffer fields or retry until success | Missing leaf, rounded IDs/times, or valid partial fields from a failed query |
| Query succeeds but leaf is a symlink/other type | Stop this profile; diagnose unsupported coverage | Target metadata, empty successful collection, or native-invalid content |

Also retain `EBADF`/`EINVAL` as query/setup faults, and resource/name-length
failures as diagnostics; the four named errors above are not an exhaustive errno
list. D-errors remains open: the exact error/unsupported/partial-field mapping and
Test propagation require native review. OVAL's ItemType already describes
entity-level versus Item-level errors; it also permits optional diagnostic
missing Items. Its FlagEnumeration has a Test-result chart. Those rules cannot
be copied as native evaluation policy. Claims: `status-missing`, `status-denied`,
`status-other-errors`, `races`.

## Worked paths (illustrative, not scanner output)

All three cases use the Form A Object above. The machine-readable
[examples](unix-file-examples.json) contain the complete proposed Collection and
Item fragments; schema checks confirm shape only. No collector or evaluator was
implemented or executed for these examples.

**A — existing regular file.** The declared fixture returns `st_mode=0100640`,
UID/GID `1000`, and `st_atim/st_ctim/st_mtim={tv_sec:1700000000,tv_nsec:0}`.
Parent/query succeed; `S_ISREG` is true. Proposed collection: `complete`, one Item.
The Item status is `exists`, with 21 typed fields. Its path fields are
`/fixture/config`, `/fixture`, `config`; type is proposed `regular`; owner/group
are integer `1000`; owner read/write and group read are true; every other mode
flag is false. The three timestamp values are proposed integer `1700000000`.
D-type, D-time, D-permissions and D-errors prevent treating that payload as an
approved native serialization. Claim: `example-regular`.

**B — asserted missing leaf.** The parent descriptor is valid; the fixture
states the final leaf is absent, with no known race or existence-hiding control;
the no-follow query returns `ENOENT`. Proposed collection:
`{status: does_not_exist, item_refs: [], population_complete: true}`; Items: `[]`.
There is no placeholder Item with a missing filename. This is not an automatic
conversion of every `ENOENT` into complete absence. Claim: `example-missing`.

**C — inaccessible parent.** The fixture's parent open fails with `EACCES`.
Proposed collection: `error`, empty Item refs, `population_complete: false`,
`stop_reason: prototype_lookup_denied`, and a `PROTOTYPE_EACCES` diagnostic.
Items: `[]`. Neither file mode `000` nor running a denial test as root establishes
this fixture. `PROTOTYPE_EACCES` is an illustrative code, not a new native error
vocabulary. No false/true/unknown Assessment result is asserted.
Claim: `example-denied`.

## Review boundary

D-type, D-time, D-permissions and D-errors are needed to adopt the basic emitted
values/statuses; D-links, D-scope and D-acl block wider coverage. See
[existing issue #33](https://github.com/vanderpol/scap-ng/issues/33). OVAL explains
more file types, size, ACL presence and traversal than this subset covers.
An engineer can code the **proposed Linux adapter** from this recipe without
reading OVAL, but cannot claim a complete, approved `unix.file` collector from it.

**Gate result: FAIL — overall superiority for an approved scanner implementation
has not been demonstrated.** Stop this documentation approach/expansion here;
Jack alone decides GO after reviewing the prototype and the six-criterion sheet.
No other capability, schema, converter, editor or runtime change follows.
