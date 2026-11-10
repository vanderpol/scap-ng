# solaris.package — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#): The package test is used to check information associated with different SVR4 packages installed on the system.

Image Packaging System (IPS) packages are not supported by this test.

The information used by this test is modeled after the /usr/bin/pkginfo command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/pkginst) | {} | source-derived |

[/$defs/meanings/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/pkginst): String that represents a package designation by its instance.

`pkginst` is a string that represents a package designation by its instance.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/name) | {} | source-derived |

[/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/name): Text string that specifies a full package name.

`name` is a text string that specifies a full package name.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/category) | {} | source-derived |

[/$defs/meanings/properties/category](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/category): String in the form of a comma-separated list of categories under which a package may be displayed.

`category` is a string in the form of a comma-separated list of categories under which a package may be displayed.

Each category is limited in length to 16 characters.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/version) | {} | source-derived |

[/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/version): Text string that specifies the current version associated with the software package.

`version` is a text string that specifies the current version associated with the software package.

Current Solaris software practice is to assign this parameter monotonically increasing Dewey decimal values of the form: major_revision.minor_revision[.micro_revision] where all the revision fields are integers.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/vendor](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/vendor) | {} | source-derived |

[/$defs/meanings/properties/vendor](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/vendor): String used to identify the vendor that holds the software copyright (maximum length of 256 ASCII characters).

`vendor` is a string used to identify the vendor that holds the software copyright (maximum length of 256 ASCII characters).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/description) | {} | source-derived |

[/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/meanings/properties/description): String that represents a more in-depth description of a package.

`description` is a string that represents a more in-depth description of a package.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object): The Object is used by a package test to define the SVR4 packages to be evaluated.

A package object consists of a single pkginst field that identifies the package to be used.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/pkginst](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/object/properties/pkginst) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/item): The Item holds information about installed SVR4 packages.

Output of /usr/bin/pkginfo.

See pkginfo(1).

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/solaris.package.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
