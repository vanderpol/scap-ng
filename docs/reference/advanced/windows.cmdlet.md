# windows.cmdlet — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_name) | {} | source-derived |
| [/$defs/meanings/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_id) | {} | source-derived |
| [/$defs/meanings/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_version) | {} | source-derived |
| [/$defs/meanings/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/verb) | {"declared_values_not_new_validation_restrictions": ["Approve", "Assert", "Compare", "Confirm", "Find", "Get", "Import", "Measure", "Read", "Request", "Resolve", "Search", "Select", "Show", "Test", "Trace", "Watch"]} | source-derived |
| [/$defs/meanings/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/noun) | {} | source-derived |
| [/$defs/meanings/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/parameters) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/parameters): Named parameters supplied to the cmdlet.

A list of properties (name and value pairs) as input to invoke the cmdlet.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/select) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/select): Output properties selected from the cmdlet result.

A list of fields (name and value pairs) used as input to the Select-Object cmdlet to select specific output properties.

Please note that the use of the '*' character, to select all properties, is not permitted.

This is equivalent to piping the output of a cmdlet to the Select-Object cmdlet.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/value) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/value): Output fields returned by the cmdlet.

The expected value represented as a set of fields (name and value pairs).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object): The Object is used by `windows.cmdlet` to identify the set of cmdlets to use and the parameters to provide to them for checking the state of a system.

The NoLanguage mode ensures that scripts that need to be evaluated are not allowed in the runspace.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_name) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_id) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_version) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/verb) | {"declaration_only": {"type": "string", "enum": ["Approve", "Assert", "Compare", "Confirm", "Find", "Get", "Import", "Measure", "Read", "Request", "Resolve", "Search", "Select", "Show", "Test", "Trace", "Watch"], "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/noun) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | native-mapping-reviewed |
| [/$defs/object/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/parameters) | {"declaration_only": {"required": true}} | source-meaning-reviewed |
| [/$defs/object/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/select) | {"declaration_only": {"required": true}} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
