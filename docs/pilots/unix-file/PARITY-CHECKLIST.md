# `unix.file`: parity and exact-pointer gaps

<!-- Generated checklist; historical rows are coverage evidence, never native assertions. -->

Compared row-by-row with both fetched 5.12.3 Read the Docs pages and pinned XSDs. Status denotes coverage in the proposal, not acceptance of new runtime semantics. URLs are mutable; [source hashes](source-map.json) identify reviewed bytes. Regeneration is offline.

| Coverage | Status | Native location / gap |
| --- | --- | --- |
| Object `filepath` | present | /$defs/object/properties/filepath; traversal children retain their parent |
| Object `path` | present | /$defs/object/properties/path; traversal children retain their parent |
| Object `filename` | present | /$defs/object/properties/filename; traversal children retain their parent |
| Object `filesystem` | present | /$defs/object/properties/filesystem; traversal children retain their parent |
| Object `traversal` | present | /$defs/object/properties/traversal; traversal children retain their parent |
| Behavior `max_depth` | present | /$defs/object/properties/traversal/properties/max_depth; source defaults/deprecated values not imported |
| Behavior `recurse` | present | /$defs/object/properties/traversal/properties/recurse; source defaults/deprecated values not imported |
| Behavior `recurse_direction` | native-undecided | /$defs/object/properties/traversal; downward construct exists, selector eligibility unresolved |
| Behavior `recurse_file_system` | present | /$defs/object/properties/filesystem; source defaults/deprecated values not imported |
| Object behaviors/filter inheritance | intentionally shared/link-only | behaviors split into traversal/filesystem; filters and Set shapes stay in native-selector.schema.json#/$defs/unix_file_object |
| Item `filepath` → `full_path` | present | meaning/type/key/value bounds present (`/$defs/value_full_path/properties/value`) |
| Item `path` → `directory` | present | meaning/type/key/value bounds present (`/$defs/value_directory/properties/value`) |
| Item `filename` → `name` | native-undecided | directory-only representation unspecified (`/$defs/value_name/properties/value`) |
| Item `type` → `type` | native-undecided | file-kind labels/enum unspecified (`/$defs/value_type/properties/value`) |
| Item `group_id` → `owner_gid` | present | meaning/type/key/value bounds present (`/$defs/value_owner_gid/properties/value`) |
| Item `user_id` → `owner_uid` | present | meaning/type/key/value bounds present (`/$defs/value_owner_uid/properties/value`) |
| Item `a_time` → `access_time` | native-undecided | time unit/resolution unspecified (`/$defs/value_access_time/properties/value`) |
| Item `c_time` → `change_time` | native-undecided | time unit/resolution unspecified (`/$defs/value_change_time/properties/value`) |
| Item `m_time` → `modify_time` | native-undecided | time unit/resolution unspecified (`/$defs/value_modify_time/properties/value`) |
| Item `size` → `size` | native-undecided | unit unspecified (`/$defs/value_size/properties/value`) |
| Item `suid` → `setuid` | present | meaning/type/key/value bounds present (`/$defs/value_setuid/properties/value`) |
| Item `sgid` → `setgid` | present | meaning/type/key/value bounds present (`/$defs/value_setgid/properties/value`) |
| Item `sticky` → `sticky` | present | meaning/type/key/value bounds present (`/$defs/value_sticky/properties/value`) |
| Item `uread` → `owner_read` | present | meaning/type/key/value bounds present (`/$defs/value_owner_read/properties/value`) |
| Item `uwrite` → `owner_write` | present | meaning/type/key/value bounds present (`/$defs/value_owner_write/properties/value`) |
| Item `uexec` → `owner_execute` | present | meaning/type/key/value bounds present (`/$defs/value_owner_execute/properties/value`) |
| Item `gread` → `group_read` | present | meaning/type/key/value bounds present (`/$defs/value_group_read/properties/value`) |
| Item `gwrite` → `group_write` | present | meaning/type/key/value bounds present (`/$defs/value_group_write/properties/value`) |
| Item `gexec` → `group_execute` | present | meaning/type/key/value bounds present (`/$defs/value_group_execute/properties/value`) |
| Item `oread` → `other_read` | present | meaning/type/key/value bounds present (`/$defs/value_other_read/properties/value`) |
| Item `owrite` → `other_write` | present | meaning/type/key/value bounds present (`/$defs/value_other_write/properties/value`) |
| Item `oexec` → `other_execute` | present | meaning/type/key/value bounds present (`/$defs/value_other_execute/properties/value`) |
| Item `has_extended_acl` → `has_extended_acl` | native-undecided | unsupported-ACL/status mapping unspecified (`/$defs/value_has_extended_acl/properties/value`) |
| Selector pairing | native-undecided | /$defs/object → native-selector.schema.json#/$defs/unix_file_object/oneOf/1: no pairing assertion; examples show selection forms only |
| Traversal eligibility | native-undecided | /$defs/object/properties/traversal; mapping rules use collected names full_path/directory, so authored-selector binding remains unresolved |
| Directory permissions | native-undecided | /$defs/value_owner_read/description: bit flags do not establish directory effective-access/search semantics |
| Links / filesystem classification | native-undecided | /$defs/object/properties/filesystem: link/target, cycles and local/same classification unresolved |
| Units | native-undecided | /$defs/value_size/properties/value; /$defs/value_access_time/properties/value; /$defs/value_change_time/properties/value; /$defs/value_modify_time/properties/value lack units |
| Absence / partial errors | native-undecided | /$defs/item/description: no synthetic missing Item; detailed propagation remains unspecified |
| Inherited Object/Item/Test/predicates | intentionally shared/link-only | /$defs/object, /$defs/item, /$defs/test and /$defs/require reference canonical shared definitions |
| Require named fields and groups | present | /$defs/require_fields and /$defs/condition: generic map plus known optional keys; not a new whitelist |
| Defaults | present | shared file_traversal_base/max_depth, file_traversal/recurse and filesystem_scope: explicit new-authoring suggestions, not runtime fallbacks |

## Historical differences (not native requirements)

| Topic | Reviewed difference |
| --- | --- |
| File-kind labels | RTD file_item/type describes regular, directory, fifo, symbolic link, socket and block special; this is not a closed XSD enumeration. String payload; no adopted native label enum. |
| Size / timestamps | Size is bytes; a_time/c_time/m_time are seconds since the Unix epoch. Integer payloads; native unit and resolution contracts remain unspecified. |
| Directory-only filename | RTD file_item/filename documents nil for the directory identified by path. Directory-only collected name representation remains unspecified. |
| Unsupported ACLs | RTD file_item/has_extended_acl uses does not exist when ACLs are unsupported, rather than false. Typed statuses exist, but the capability-specific unsupported-ACL mapping remains unspecified. |
| Collection defaults | FileBehaviors documents depth -1, recurse symlinks and directories, direction none and filesystem all. Downward construct; unlimited/symlinks_and_directories/local are explicit editor suggestions, not runtime fallbacks. |

RTD selector occurrences are branch-local; singular optional Item entities do not establish native map/value counts. The datatype tightening is separate and covered by [compatibility vectors](CANONICAL-INTEGRATION.md).
