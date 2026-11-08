# linux.rpminfo — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/package_name) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/architecture](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/architecture) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/epoch) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/release) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/version) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/evr) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/signature_key_id](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/signature_key_id) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/extended_name) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/full_path) | {} | native-mapping-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/package_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/include_file_paths](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/include_file_paths) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
