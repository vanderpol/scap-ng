# solaris.smfproperty — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/service) | {} | source-derived |

[/$defs/meanings/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/service): The SMF service on the system.

Specifies the SMF service on the system.

This is the service category and name separated by a forward slash ("/").

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/instance) | {} | source-derived |

[/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/instance): The instance of an SMF service which represents a specific configuration of a service.

Specifies the instance of an SMF service which represents a specific configuration of a service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/property) | {} | source-derived |

[/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/property): The name of the property associated with an SMF service.

This is the property category and name separated by a forward slash ("/").

Specifies the name of the property associated with an SMF service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/fmri) | {} | source-derived |
| [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/value) | {} | source-derived |

[/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/value): The value of the property associated with an SMF service.

Specifies the value of the property associated with an SMF service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/service) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/instance) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/property) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
