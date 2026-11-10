# linux.rpmverifypackage — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#): The `linux.rpmverifypackage` is used to verify the integrity of installed RPMs.

This test aligns with the rpm -V command for verifying RPMs.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/name): Package name.

This is the package name to check.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/epoch) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/version) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/version): Package version component.

This is the version number of the build.

In the case of an apache rpm named httpd-2.0.40-21.11.4.i686.rpm, this value would be 2.0.40.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/release) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/release): Package release component.

This is the release number of the build, changed by the vendor/builder.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/arch) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/arch): Package architecture.

This is the architecture for which the RPM was built, like : i386, ppc, sparc, noarch.

In the case of an apache rpm named httpd-2.0.40-21.11.4.i686.rpm, this value would be i686.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/extended_name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/dependency_check_passed](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/dependency_check_passed) | {} | source-derived |

[/$defs/meanings/properties/dependency_check_passed](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/dependency_check_passed): The dependency_check_passed field indicates whether or not the dependency check passed.

`dependency_check_passed` indicates whether or not the dependency check passed.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/verification_script_successful](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/verification_script_successful) | {} | source-derived |

[/$defs/meanings/properties/verification_script_successful](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/verification_script_successful): The verification_script_successful field indicates whether or not the verification script executed successfully.

`verification_script_successful` indicates whether or not the verification script executed successfully.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/epoch) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/version) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/release) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/arch) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/object/properties/skip_dependencies](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/skip_dependencies) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/object/properties/skip_scripts](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/skip_scripts) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
