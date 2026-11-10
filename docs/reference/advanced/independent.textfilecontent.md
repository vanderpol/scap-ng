# independent.textfilecontent — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/full_path) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/full_path): Full path of the text file.

`full_path` specifies the absolute path for a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/directory) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/directory](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/directory): Directory component of the file path.

`directory` specifies the directory component of the absolute path to a file on the machine.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/name) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/name): File name without the directory.

`name` specifies the name of the file (without the path) that is being represented.

`name` specifies the name of a file.

`name` represents the name of a file.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/pattern) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/pattern): Regular expression used to extract matching text.

`pattern` represents a regular expression that is used to define a block of text.

Subexpression notation (parenthesis) is used to call out a value(s) to test against.

`pattern` defines a chunk of text in a file and is represented using a regular expression.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/instance) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/instance): Ordinal occurrence of a pattern match.

`instance` calls out which match of the pattern is being represented by this item.

`instance` calls out a specific match of the pattern.

Negative values are used to simplify collection of pattern match occurrences counting backwards from the final match in the targeted file.

To find the final match, use an instance of -1; the penultimate match is found using an instance value of -2, and so on.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/text](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/text) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/text](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/text): Text matched by the pattern.

`text` represents the block of text that matched the specified pattern.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/subexpression) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/subexpression](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/meanings/properties/subexpression): Text captured by a parenthesized group in the pattern.

`subexpression` represents the value of a subexpression in the specified pattern.

`subexpression` represents a value to test against the subexpression in the specified pattern.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/full_path) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/directory](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/directory) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/pattern](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/pattern) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/instance) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/ignore_case](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/ignore_case) | {"declaration_only": {"type": "boolean", "required": true}} | source-meaning-reviewed |
| [/$defs/object/properties/multiline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/multiline) | {"declaration_only": {"type": "boolean", "required": true}} | source-meaning-reviewed |

[/$defs/object/properties/multiline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/multiline): Control for line-anchor matching within the input.

'multiline' enables multiple line semantics in the regular expression provided by the pattern field.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/singleline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/singleline) | {"declaration_only": {"type": "boolean", "required": true}} | source-meaning-reviewed |

[/$defs/object/properties/singleline](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/singleline): Control for whether a dot matches newline characters.

'singleline' enables single line semantics in the regular expression provided by the pattern field.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/item_creation](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/object/properties/item_creation) | {"declaration_only": {"type": "string", "enum": ["all_object_elements_fullfilled", "filepath_exists"], "required": true}} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/independent.textfilecontent.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
