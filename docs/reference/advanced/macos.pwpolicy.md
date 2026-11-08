# macos.pwpolicy — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/username) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/username): User whose password policy is queried.

`username` specifies the user whose password policy information was collected.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator) | {} | source-derived |

[/$defs/meanings/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator): Username of the authenticator.

`authenticator` specifies the username of the authenticator.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator_password) | {} | source-derived |

[/$defs/meanings/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator_password): Password of the authenticator as specified by the authenticator field.

`authenticator_password` specifies the password of the authenticator as specified by the authenticator element.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/directory_node) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/directory_node): Directory-service node queried for password policy.

`directory_node` specifies the directory node that the password policy information was collected from.

`directory_node` specifies the directory node that you would like to retrieve the password policy information from.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/xpath) | {} | source-derived |

[/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/xpath): An XPath expression describing the text node(s) or attribute(s) to look at.

Specifies an XPath 1.0 expression to evaluate against the XML representation of the plist file specified by the filename or app_id field.

The intention is that the text values be drawn from instances of a single, uniquely named element or attribute.

Specifies an XPath expression describing the text node(s) or attribute(s) to look at.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/value_of) | {} | source-derived |

[/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/value_of): The value of the preference key.

`value_of` checks the value(s) of the text node(s) or attribute(s) found.

How this is used is entirely controlled by operator attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/username) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator_password) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator_password): Password of the authenticator as specified by the username field.

`authenticator_password` specifies the password of the authenticator as specified by the username element.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/directory_node) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/xpath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/xpath): An XPath 1.0 expression to evaluate against the XML representation of the output generated from the pwpolicy -getaccountinfo command.

Specifies an XPath 1.0 expression to evaluate against the XML representation of the output generated from the pwpolicy -getaccountinfo command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
