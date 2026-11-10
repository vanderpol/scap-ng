# aix.fix — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#): The fix test is used to check information associated with different fixes installed on the system.

The information being tested is based off the /usr/sbin/instfix -iavk command.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/apar_number) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/apar_number): Authorized Program Analysis Report (APAR) identifier.

APAR is the short for 'Authorized Program Analysis Report'.

APAR identifies and describes a software product defect.

An example of an apar_number is 'IY78751', it includes two alphabetic characters and a 5-digit integer.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/abstract](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/abstract) | {} | source-derived |

[/$defs/meanings/properties/abstract](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/abstract): The abstract of an APAR.

The abstract of the APAR being checked.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/symptom](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/symptom) | {} | source-derived |

[/$defs/meanings/properties/symptom](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/symptom): The symptom text related to an APAR.

The symptom text related to the APAR being checked.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/installation_status](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/installation_status) | {} | source-derived |

[/$defs/meanings/properties/installation_status](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/installation_status): The installation status of files associated with the APAR.

The last line of the output is 'All filesets for XXXXXXX were found', or 'Not all filesets for XXXXXXX were found' or 'No filesets which have fixes for XXXXXXX are currently installed.'.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object): A fix object consists of a single apar_number field that identifies the fix to be used.

The Object is used by a fix test to define the specific fix to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object/properties/apar_number) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-meaning-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/item): From /usr/sbin/instfix -iavk APARNum Command.

See instfix manpage for specific fields.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
