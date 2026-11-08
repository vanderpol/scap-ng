# linux.dpkginfo — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/name) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/name): Installed package name.

This is the pakage name to check.

This is the package name to check.

This is the DPKG package name to check.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/arch) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/arch): Package architecture.

This is the architecture for which the DPKG was built, like : i386, ppc, sparc, noarch.

This is the architecture for which the package was built, like : i386, ppc, sparc, noarch.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/epoch) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/release) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/release): Package revision component.

This is the release number of the build.

This is the release number of the build, changed by the vendor/builder.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/version) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/version): Package version component.

This is the version number of the build, changed by the vendor/builder.

This is the version number of the build.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/evr) | {} | source-meaning-reviewed |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object): A dpkginfo object consists of a single name field that identifies the package being checked.

The Object is used by a dpkginfo test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object/properties/name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1/properties/name", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
