# macos.systemprofiler — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/data_type](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/data_type) | {} | source-derived |

[/$defs/meanings/properties/data_type](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/data_type): Datatype value that is desired.

Specifies the data type that was used in collection.

`data_type` provides the datatype value that is desired.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/xpath) | {} | source-derived |

[/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/xpath): An Xpath expression describing the text node(s) or attribute(s) to look at.

Specifies an Xpath expression describing the text node(s) or attribute(s) to look at.

Any valid Xpath 1.0 statement is usable with one exception, at most one field may be identified in the Xpath.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/value_of) | {} | source-derived |

[/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/meanings/properties/value_of): The value_of field checks the value(s) of the text node(s) or attribute(s) found.

`value_of` checks the value(s) of the text node(s) or attribute(s) found.

How this is used is entirely controlled by operator attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/object): The Object is used by `macos.systemprofiler` to define the object to be evaluated.

An Object consists of a data_type field that contains the name of the datatype that was probed by the system_profiler utility.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/data_type](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/object/properties/data_type) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/object/properties/xpath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.systemprofiler.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
