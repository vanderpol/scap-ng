# linux.rpminfo — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/package_name) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/package_name): Installed RPM package name.

This is the pakage name to check.

This is the package name to check.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/architecture](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/architecture) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/architecture](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/architecture): Package architecture.

This is the architecture for which the RPM was built, like : i386, ppc, sparc, noarch.

In the case of an apache rpm named httpd-2.0.40-21.11.4.i686.rpm, this value would be i686.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/epoch) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/release) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/release): Package release component.

This is the release number of the build.

This is the release number of the build, changed by the vendor/builder.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/version) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/version): Package version component.

This is the version number of the build, changed by the vendor/builder.

In the case of an apache rpm named httpd-2.0.40-21.11.4.i686.rpm, this value would be 2.0.40.

This is the version number of the build.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/evr) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/signature_key_id](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/signature_key_id) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/signature_key_id](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/signature_key_id): Identifier of the package signing key.

This field contains the PGP key ID that the RPM issuer (generally the original operating system vendor) uses to sign the key.

PGP is used to verify the authenticity and integrity of the RPM being considered.

Software packages and patches are signed cryptographically to allow administrators to allay concerns that the distribution mechanism has been compromised, whether that mechanism is web site, FTP server, or even a mirror controlled by a hostile party.

This field contains the 64-bit PGP key ID that the RPM issuer (generally the original operating system vendor) uses to sign the key.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/extended_name) | {} | native-mapping-reviewed |
| [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/full_path) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/full_path): Path of a file owned by the package.

This field contains the absolute path of a file or directory included in the rpm.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object): A rpm info object consists of a single name field that identifies the package being checked.

The Object is used by a rpm info test to define the object to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/package_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/object/properties/include_file_paths](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/include_file_paths) | {"declaration_only": {"type": "boolean", "required": true}} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
