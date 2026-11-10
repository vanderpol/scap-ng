# macos.plist — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/app_id](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/app_id) | {} | source-derived |
| [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/filepath) | {} | source-derived |

[/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/filepath): The absolute path to a plist file (e.g. ~/Library/Preferences/com.apple.Safari.plist).

The absolute path to a plist file (e.g. /Library/Preferences/com.apple.TimeMachine.plist).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/xpath) | {} | source-derived |

[/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/xpath): An XPath expression describing the text node(s) or attribute(s) to look at.

Specifies an XPath 1.0 expression to evaluate against the XML representation of the plist file specified by the filename or app_id field.

The intention is that the text values be drawn from instances of a single, uniquely named element or attribute.

Specifies an XPath expression describing the text node(s) or attribute(s) to look at.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/value_of) | {} | source-derived |

[/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/value_of): The value of the preference key.

`value_of` checks the value(s) of the text node(s) or attribute(s) found.

How this is used is entirely controlled by operator attributes.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/app_id](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/app_id) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/filepath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/xpath) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
