# `unix.file`

Select filesystem entries and collect their metadata for comparison.
Meanings below paraphrase pinned OVAL 5.12.3 in frozen SCAP-NG 0.4 names; notes distinguish source facts, native differences and undecided behavior.

## Object

Selection form: `filepath` **or** `path` + `filename` ([mapping][mapping]).

| Field | Meaning | Notes / differences |
| --- | --- | --- |
| `filepath` | Full path to a file. | OVAL uses an absolute, non-directory path; alternative to `path` + `filename`. |
| `path` | Directory containing the selected entry. | Used with `filename`. |
| `filename` | Entry name within that directory. | `null` selects the directory itself; neither an empty string nor `.*`. |
| `filesystem` | Filesystem scope of collection. | `all`: any; `local`: non-remote; `same`: starting filesystem (OVAL `defined`). |
| `traversal` | Controls recursive searching through directories and symbolic links. | Optional object; both children below are required when present. |

### `traversal`

| Field | Meaning | Allowed values / requirements |
| --- | --- | --- |
| `max_depth` | Maximum downward recursion depth. | Required: nonnegative integer or `unlimited` (OVAL `-1`); depth `0` includes the starting directory. |
| `recurse` | Which entries recursion follows. | Required: `directories`, `symlinks`, `symlinks_and_directories`. |

New-authoring suggestions are `unlimited` and `symlinks_and_directories`. Serialize both explicitly; these are not runtime fallbacks. Preserve source-effective values.

## Collected Item

| Field | Meaning | Datatype / units |
| --- | --- | --- |
| `full_path` | Full path of the collected entry. | string |
| `directory` | Directory component of its path. | string |
| `name` | Entry name, without the directory. | string; directory form undecided |
| `type` | File kind: regular file, directory, pipe, link, socket or device. | string; native labels undecided |
| `owner_uid` | Numeric user ID of the owner. | integer |
| `owner_gid` | Numeric group ID of the owning group. | integer |
| `size` | File size. | integer; bytes¹ |
| `access_time` | Last data-access time. | integer; seconds¹ |
| `change_time` | Last inode-status change; not creation time. | integer; seconds¹ |
| `modify_time` | Last content-modification time. | integer; seconds¹ |
| `setuid` | Set-user-ID permission flag. | boolean |
| `setgid` | Set-group-ID permission flag. | boolean |
| `sticky` | Sticky/restricted-deletion flag. | boolean |
| `owner_read` | Whether the owner-read permission bit is set. | boolean |
| `owner_write` | Whether the owner-write permission bit is set. | boolean |
| `owner_execute` | Whether the owner-execute/search bit is set. | boolean |
| `group_read` | Whether the group-read permission bit is set. | boolean |
| `group_write` | Whether the group-write permission bit is set. | boolean |
| `group_execute` | Whether the group-execute/search bit is set. | boolean |
| `other_read` | Whether the other-read permission bit is set. | boolean |
| `other_write` | Whether the other-write permission bit is set. | boolean |
| `other_execute` | Whether the other-execute/search bit is set. | boolean |
| `has_extended_acl` | ACL permissions differ from standard UNIX permissions. | boolean; unavailable handling below |

¹ Units are OVAL-established: bytes for size; seconds since the Unix epoch for times. Native unit/resolution rules are undecided.

Renamed source fields: `filepath/path/filename` → `full_path/directory/name`; `user_id/group_id` → `owner_uid/owner_gid`; `a_time/c_time/m_time` → `access_time/change_time/modify_time`; `suid/sgid` → `setuid/setgid`. Source `u/g/o` + `read/write/exec` maps to native `owner/group/other` + `_read/_write/_execute`.

## Require

`require.fields` predicates evaluate the collected fields above, using their declared datatypes and the [shared Item/field cardinality rules][require-schema].

## Important behavior

| Topic | Meaning / caveat |
| --- | --- |
| Selection | OVAL collects all UNIX file types, including directories and symbolic links. Native regex token: `matches_regex`. |
| Traversal | OVAL recurses only for equality-selected `path`, not `filepath`. Native traversal is downward; deprecated source `up` is not represented. Rule binding uses collected names `full_path`/`directory` and remains undecided. |
| Sets / filters | Compose collections before comparison; filter State references must use `unix.file`. |
| Links / boundaries | Native link-versus-target metadata, cycle handling, mount identity and `local`/`same` classification are undecided. |
| Defaults | OVAL omitted filesystem scope means `all`; omitted recursion direction means none. Native editor suggestion `local` is not a runtime default; preserve source-effective values. |
| Permissions | Permission flags are not a complete effective-access or privilege guarantee; native effective-access interpretation is undecided. |
| ACL availability | OVAL reports unsupported ACLs as an absent field, not `false`; the native unsupported-field mapping is undecided. |
| Absence / errors | Native omits nonexistent Items; collection absence/errors and field statuses are separate. Errno, partial-collection and evaluation propagation remain undecided. |

## Illustration

Illustrative Object → collected Item fields excerpt; not an executed scan:

```yaml
object:
  path: {equals: /example}
  filename: {equals: config}
  filesystem: all
  traversal:
    max_depth: 1
    recurse: directories
# → Item fields excerpt:
fields:
  full_path: {datatype: string, status: exists, value: /example/config}
  owner_uid: {datatype: integer, status: exists, value: 1000}
```

## Sources

- OVAL 5.12.3, pinned commit `2f140ee5…`: [file Object and State][oval-def], [file Item][oval-item], [FileBehaviors][oval-behaviors], [shared Item/error documentation][oval-status]. Descriptions are paraphrased; OVAL facts are not automatically native requirements.
- Native [mapping][mapping]: `/native/selector_map`, `/native/state_field_map`, `/native/field_datatypes`, `/semantic_validator_rules`.
- Native [selector contracts][selectors]: `/resolved/unix.file`; [Object schema][object-schema]: `/$defs/unix_file_object`; nested control: `/$defs/unix_file_object/oneOf/1/properties/traversal`.
- Native [file controls][controls]: `/$defs/filesystem_scope`, `/$defs/file_traversal_base`, `/$defs/file_traversal`; [Item][item-schema] and [typed field][field-schema] status shapes.

[oval-def]: https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/unix-definitions-schema.xsd#L167-L462
[oval-item]: https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/unix-system-characteristics-schema.xsd#L59-L270
[oval-behaviors]: https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/unix-definitions-schema.xsd#L463-L572
[oval-status]: https://github.com/OVAL-Community/OVAL/blob/2f140ee5c5dd1ed9606fcd5afc301f6baeb48706/oval-schemas/oval-system-characteristics-schema.xsd#L250-L354
[mapping]: ../../../schema/capability-mappings/supported/unix.file.json
[selectors]: ../../../schema/native-selector-contracts.json
[object-schema]: ../../../schema/native-selector.schema.json
[controls]: ../../../schema/capability-common.schema.json
[item-schema]: ../../../schema/collected-item.schema.json
[field-schema]: ../../../schema/result-types.schema.json
[require-schema]: ../../../schema/assessment-language.schema.json#/$defs/canonical_all_items_requirement
