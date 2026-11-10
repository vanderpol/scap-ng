# solaris.smf — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/fmri) | {} | source-derived |

[/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/fmri): The FMRI (Fault Managed Resource Identifier) field describes a possible identifier associated with a service.

The FMRI (Fault Managed Resource Identifier) field holds the identifier associated with a service.

Services managed by SMF are assigned FMRI URIs prefixed with the scheme name "svc".

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_name) | {} | source-derived |

[/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_name): Usually an abbreviated form of the FMRI.

`service_name` is usually an abbreviated form of the FMRI.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/service_state](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/service_state) | {} | source-derived |
| [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/protocol) | {} | source-derived |

[/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/protocol): Possible protocol supported by the service.

`protocol` describes the protocol supported by the service.

`protocol` describes a possible protocol supported by the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/server_executable](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_executable) | {} | source-derived |

[/$defs/meanings/properties/server_executable](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_executable): The field server_executable is a string representing the listening daemon on the server side.

An example being 'svcprop ftp' which might show 'inetd/start/exec astring /usr/sbin/in.ftpd\ -a'

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/server_arguements](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_arguements) | {} | source-derived |

[/$defs/meanings/properties/server_arguements](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/server_arguements): The server_arguments field describes possible parameters that are passed to the service.

The server_arguments field describes the parameters that are passed to the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/exec_as_user](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/exec_as_user) | {} | source-derived |

[/$defs/meanings/properties/exec_as_user](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/meanings/properties/exec_as_user): String pulled from svcprop in the following format: inetd_start/user astring root

`exec_as_user` is a string pulled from svcprop in the following format: inetd_start/user astring root

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object): An Object consists of a fmri field that represents the Fault Management Resource Identifier (FMRI) which uniquely identifies a service.

The Object is used by `solaris.smf` to define the specific service instance to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/object/properties/fmri) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/solaris.smf.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
