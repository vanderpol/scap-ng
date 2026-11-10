# aix.fileset — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#): The `aix.fileset` is used to check information associated with different filesets installed on the system.

The information used by this test is modeled after the /usr/bin/lslpp -l command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/flstinst) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/flstinst): Fileset name.

Represents the name of the fileset being checked.

`flstinst` represents the fileset name we want to check.

Represents the name of a fileset.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/level](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/level) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/level](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/level): Fileset maintenance level.

Maintenance level (also known as version in Solaris or Linux) of the fileset.

Maintenance level (also known as version in Solaris or Linux) of a fileset.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/state](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/state) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/state](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/state): Installation state of the fileset.

This gives the state of the fileset being checked.

See the manpage of the 'lslpp' command more information.

This gives the state of a fileset.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/description) | {} | source-derived |

[/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/description): Short description of a fileset.

Short description of the fileset being checked.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object): An Object consists of a single flstinst field that identifies the fileset to be used.

The Object is used by `aix.fileset` to define the fileset to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object/properties/flstinst) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/item): Output of /usr/bin/lslpp -l FilesetName.

See lslpp manpage for specific fields.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
