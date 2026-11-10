# windows.file — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/full_path): Absolute path for a file on the machine.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/directory) | {} | source-derived |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/directory): Directory component of the absolute path to a file on the machine.

Specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/name): Name of the file.

The name of the file.

The other items associated with this item would then reflect the values associated with the directory.

`name` specifies the name of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/owner](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/owner) | {} | source-derived |

[/$defs/meanings/properties/owner](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/owner): String that contains the name of the owner.

A string that contains the name of the owner.

`owner` is a string that contains the name of the owner.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/size](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/size) | {} | source-derived |
| [/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/access_time) | {} | source-derived |

[/$defs/meanings/properties/access_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/access_time): Time of last access of file.

Valid on NTFS but not on FAT formatted disk drives.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/creation_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/creation_time) | {} | source-derived |
| [/$defs/meanings/properties/modify_time](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/modify_time) | {} | source-derived |
| [/$defs/meanings/properties/microsoft_checksum](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/microsoft_checksum) | {} | source-derived |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/version) | {} | source-derived |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/version): Delimited version string of the file.

The version of the file.

`version` is the delimited version string of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/type) | {"declared_values_not_new_validation_restrictions": ["directory", "char", "disk", "pipe", "remote", "unknown"]} | source-derived |

[/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/type): The type field marks whether the file is a named pipe, standard file, etc.

The type child element marks whether the file item describes a named pipe, standard file, etc.

`type` marks whether the file is a named pipe, standard file, etc.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/attribute](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/attribute) | {"declared_values_not_new_validation_restrictions": ["archive", "compressed", "device", "directory", "encrypted", "hidden", "integrity_stream", "normal", "not_content_indexed", "no_scrub_data", "offline", "readonly", "reparse_point", "sparse_file", "system", "temporary", "virtual"]} | source-derived |

[/$defs/meanings/properties/attribute](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/attribute): The attribute field marks a Windows file attribute.

The attribute child elements denote the Windows file attributes associated with the file.

`attribute` marks a Windows file attribute.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/development_class](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/development_class) | {} | source-derived |

[/$defs/meanings/properties/development_class](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/development_class): The development_class field allows the distinction to be made between the GDR development environment and the QFE development environment.

`development_class` allows the distinction to be made between the GDR development environment and the QFE development environment.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/company](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/company) | {} | source-derived |

[/$defs/meanings/properties/company](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/company): A company name to be found within the version-information structure.

This field defines the company name held within the version-information structure.

This field defines a company name to be found within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/internal_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/internal_name) | {} | source-derived |

[/$defs/meanings/properties/internal_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/internal_name): An internal name to be found within the version-information structure.

This field defines the internal name held within the version-information structure.

This field defines an internal name to be found within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/language](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/language) | {} | source-derived |

[/$defs/meanings/properties/language](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/language): A language to be found within the version-information structure.

This field defines the language held within the version-information structure.

This field defines a language to be found within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/original_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/original_name) | {} | source-derived |

[/$defs/meanings/properties/original_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/original_name): An original filename to be found within the version-information structure.

This field defines the original filename held within the version-information structure.

This field defines an original filename to be found within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/product_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_name) | {} | source-derived |

[/$defs/meanings/properties/product_name](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_name): A product name to be found within the version-information structure.

This field defines the product name held within the version-information structure.

This field defines a product name to be found within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/product_version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_version) | {} | source-derived |

[/$defs/meanings/properties/product_version](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/meanings/properties/product_version): The product version held within the version-information structure.

This field defines the product version held within the version-information structure.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object): The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

The Object is used by a file test to define the specific file(s) to be evaluated.

A file object defines the path and filename or complete filepath of the file(s).

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filepath", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/path", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/path](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/path): Directory component of the absolute path to a file on the machine.

`path` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filename) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/filename", "type_alternatives": ["null", "object"]} | source-derived |

[/$defs/object/properties/filename](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/filename): Name of a file to evaluate.

`filename` specifies the name of a file to evaluate.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/object/properties/traversal) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_file_object/oneOf/1/properties/traversal", "type_alternatives": ["object"]} | existing-native |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/windows.file.schema.json#/$defs/require): The comparison fields define the different metadata associated with a Windows file.

This includes the path, filename, owner, size, last modified time, version, etc.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
