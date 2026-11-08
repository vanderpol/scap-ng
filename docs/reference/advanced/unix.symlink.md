# unix.symlink — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/full_path): The filepath used to create the object.

Specifies the filepath to the subject symbolic link file, specified by the Object.

Specifies the filepath used to create the object.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/canonical_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/canonical_path) | {} | source-derived |

[/$defs/meanings/properties/canonical_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/canonical_path): The canonical path for the target of a symbolic link file specified by the filepath.

Specifies the canonical path for the target of the symbolic link file specified by the filepath.

Specifies the canonical path for the target of a symbolic link file specified by the filepath.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object): The Object is used by `unix.symlink` to define the object to be evaluated.

An Object consists of a filepath field that contains the path to a symbolic link file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object/properties/full_path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object/properties/full_path): The filepath for the symbolic link.

Specifies the filepath for the symbolic link.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
