# independent.yamlfilecontent — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#): The `independent.yamlfilecontent` element is used to explore the contents of an YAML file.

This test allows specific pieces of an YAML document specified using YAML Path to be tested.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/full_path) | {} | source-derived |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/full_path): Absolute path for a file on the machine.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/directory) | {} | source-derived |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/directory): Directory component of the absolute path to a file on the machine.

`directory` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/name): Name of the file.

`name` specifies the name of the file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/content](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/content) | {} | source-derived |

[/$defs/meanings/properties/content](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/content): YAML document body.

`content` specifies the YAML document body.

It also could reference a variable containing the document using var_ref attribute.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/yamlpath](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/yamlpath) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/yamlpath](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/yamlpath): YAML Path expression selecting values from the document.

Specifies an YAML Path expression to evaluate against the YAML file specified by the filename field.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/value) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/meanings/properties/value): Values selected by the YAML Path expression.

`value` holds the target(s) of the specified YAML Path.

A single scalar value or a list of scalar values (where there is no key to associate) would have the name attribute of the field element set to '#'.

`value` specifies how to test objects in the value set of the specified YAML Path.

To define tests for a single scalar value or a list of scalar values (where there is no key to associate), set the name attribute of the field element to '#'.

The check is entirely controlled by operator attributes of the field element.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object): The Object is used by a YAML file content test to define the specific piece of an YAML file(s) to be evaluated.

The set of files to be evaluated may be identified with either a complete filepath or a path and filename.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object/properties/full_path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object/properties/directory) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/content](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object/properties/content) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/yamlpath](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/object/properties/yamlpath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/independent.yamlfilecontent.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
