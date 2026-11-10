# windows.wmi.query — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/namespace](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/namespace) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/namespace](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/namespace): WMI namespace for the query.

The WMI namespaces of the specific object.

Specifies which WMI namespace to look under.

Each WMI provider normally registers its own WMI namespace and then all its classes within that namespace.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/query](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/query) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/query](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/query): WQL query text.

A valid WQL query used to identify the object(s) to test against.

However, SELECT * FROM ... is not valid.

A WQL query used to identify the object(s) specified.

Any valid WQL query is allowed with one exception, at most one field is allowed in the SELECT portion of the query.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/result) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/meanings/properties/result): Values returned by the WQL query.

`result` holds the results of the specified WQL statement.

`result` specifies how to test objects in the result set of the specified WQL statement.

`result` specifies how to test items in the result set of the specified WQL statement.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/namespace](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object/properties/namespace) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/object/properties/query](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/object/properties/query) | {"declaration_only": {"type": "string", "required": true, "allow_variable": true}} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.wmi.query.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
