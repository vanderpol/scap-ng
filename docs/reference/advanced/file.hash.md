# file.hash — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/full_path): Absolute path for a file on the machine.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/directory) | {} | source-derived |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/directory): Directory component of the absolute path to a file on the machine.

`directory` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/name): Name of the file.

The name of the file.

`name` specifies the name of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/algorithm](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/algorithm) | {"declared_values_not_new_validation_restrictions": ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]} | source-derived |

[/$defs/meanings/properties/algorithm](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/algorithm): Hash algorithm to use when collecting the hash for each of the specifed files.

Identifier for the hash algorithm used to calculate the hash.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/digest](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/digest) | {} | source-derived |

[/$defs/meanings/properties/digest](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/meanings/properties/digest): Result of applying the hash algorithm to the file.

The result of applying the hash algorithm to the file.

`digest` specifies the result of applying the hash algorithm to the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object): The Object is used by a file hash test to define the specific file(s) to be evaluated.

An Object defines the path and filename of the file(s).

In addition, a number of behaviors may be provided that help guide the collection of objects.

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object/properties/full_path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object/properties/directory) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/algorithm](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/object/properties/algorithm) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"], "declared_values_not_new_validation_restrictions": ["md5", "sha1", "sha224", "sha256", "sha384", "sha512"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/item): This element stores a hash value associated with a specific file.

This element stores the different hash values associated with a specific file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/file.hash.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
