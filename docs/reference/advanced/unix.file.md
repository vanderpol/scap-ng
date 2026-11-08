# unix.file — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/full_path) | {} | editorially-approved |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/directory) | {} | editorially-approved |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/name) | {} | editorially-approved |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/type) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_gid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_gid) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_uid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_uid) | {} | editorially-approved |
| [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/access_time) | {} | editorially-approved |
| [/$defs/meanings/properties/change_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/change_time) | {} | editorially-approved |
| [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/modify_time) | {} | editorially-approved |
| [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/size) | {} | editorially-approved |
| [/$defs/meanings/properties/setuid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setuid) | {} | editorially-approved |
| [/$defs/meanings/properties/setgid](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/setgid) | {} | editorially-approved |
| [/$defs/meanings/properties/sticky](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/sticky) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_read) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_write) | {} | editorially-approved |
| [/$defs/meanings/properties/owner_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/owner_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/group_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_read) | {} | editorially-approved |
| [/$defs/meanings/properties/group_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_write) | {} | editorially-approved |
| [/$defs/meanings/properties/group_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/group_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/other_read](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_read) | {} | editorially-approved |
| [/$defs/meanings/properties/other_write](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_write) | {} | editorially-approved |
| [/$defs/meanings/properties/other_execute](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/other_execute) | {} | editorially-approved |
| [/$defs/meanings/properties/has_extended_acl](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/meanings/properties/has_extended_acl) | {} | editorially-approved |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filepath", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/path", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/filename) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/filename", "type_alternatives": ["null", "object"]} | source-derived |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/unix_file_object/oneOf/1/properties/traversal", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.file.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
