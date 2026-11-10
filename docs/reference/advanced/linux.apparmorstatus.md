# linux.apparmorstatus — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/loaded_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/loaded_profiles_count) | {} | source-derived |
| [/$defs/meanings/properties/enforce_mode_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/enforce_mode_profiles_count) | {} | source-derived |
| [/$defs/meanings/properties/complain_mode_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/complain_mode_profiles_count) | {} | source-derived |
| [/$defs/meanings/properties/processes_with_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/processes_with_profiles_count) | {} | source-derived |
| [/$defs/meanings/properties/enforce_mode_processes_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/enforce_mode_processes_count) | {} | source-derived |
| [/$defs/meanings/properties/complain_mode_processes_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/complain_mode_processes_count) | {} | source-derived |
| [/$defs/meanings/properties/unconfined_processes_with_profiles_count](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/meanings/properties/unconfined_processes_with_profiles_count) | {} | source-derived |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/object): The Object is used by an apparmorstatus test to define the different information about the current AppArmor polciy.

Therefore, there are no child entities defined.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/item): The AppArmor Status Item displays various information about the current AppArmor policy.

This item maps the counts of profiles and processes as per the results of the "apparmor_status" or "aa-status" command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.apparmorstatus.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
