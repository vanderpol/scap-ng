# solaris.package — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/pkginst) | {} | source-derived |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/name) | {} | source-derived |
| [/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/category) | {} | source-derived |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/version) | {} | source-derived |
| [/$defs/meanings/properties/vendor](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/vendor) | {} | source-derived |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/description) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object/properties/pkginst) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
