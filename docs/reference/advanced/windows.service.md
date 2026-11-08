# windows.service — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#) | {} | source-derived-proposal |
| [/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_name) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/service_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_name): Internal service name.

`service_name` specifies the name of the service as specified in the Service Control Manager (SCM) database.

`service_name` specifies the service name as stored in the Service Control Manager (SCM) database on the system.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/display_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/display_name) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/display_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/display_name): Service display name.

`display_name` specifies the name of the service as specified in tools such as Control Panel->Administrative Tools->Services.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/description) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/description): Service description.

`description` specifies the description of the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/service_type](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_type) | {"declared_values_not_new_validation_restrictions": ["SERVICE_FILE_SYSTEM_DRIVER", "SERVICE_KERNEL_DRIVER", "SERVICE_WIN32_OWN_PROCESS", "SERVICE_WIN32_SHARE_PROCESS", "SERVICE_INTERACTIVE_PROCESS"]} | native-mapping-reviewed |

[/$defs/meanings/properties/service_type](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_type): Service type.

`service_type` specifies the type of the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/start_type](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/start_type) | {"declared_values_not_new_validation_restrictions": ["SERVICE_AUTO_START", "SERVICE_BOOT_START", "SERVICE_DEMAND_START", "SERVICE_DISABLED", "SERVICE_SYSTEM_START"]} | native-mapping-reviewed |
| [/$defs/meanings/properties/current_state](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/current_state) | {"declared_values_not_new_validation_restrictions": ["SERVICE_CONTINUE_PENDING", "SERVICE_PAUSE_PENDING", "SERVICE_PAUSED", "SERVICE_RUNNING", "SERVICE_START_PENDING", "SERVICE_STOP_PENDING", "SERVICE_STOPPED"]} | native-mapping-reviewed |
| [/$defs/meanings/properties/controls_accepted](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/controls_accepted) | {"declared_values_not_new_validation_restrictions": ["SERVICE_ACCEPT_NETBINDCHANGE", "SERVICE_ACCEPT_PARAMCHANGE", "SERVICE_ACCEPT_PAUSE_CONTINUE", "SERVICE_ACCEPT_PRESHUTDOWN", "SERVICE_ACCEPT_SHUTDOWN", "SERVICE_ACCEPT_STOP", "SERVICE_ACCEPT_HARDWAREPROFILECHANGE", "SERVICE_ACCEPT_POWEREVENT", "SERVICE_ACCEPT_SESSIONCHANGE", "SERVICE_ACCEPT_TIMECHANGE", "SERVICE_ACCEPT_TRIGGEREVENT"]} | source-derived |
| [/$defs/meanings/properties/start_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/start_name) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/path](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/path) | {} | native-mapping-reviewed |

[/$defs/meanings/properties/path](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/path): Service executable path.

`path` specifies the path to the binary of the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |

[/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/pid): Process ID of the service.

`pid` specifies the process ID of the service.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/service_flag](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/service_flag) | {} | source-meaning-reviewed |
| [/$defs/meanings/properties/dependencies](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/dependencies) | {} | source-derived |

[/$defs/meanings/properties/dependencies](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/meanings/properties/dependencies): Dependencies of this service on other services.

`dependencies` specifies the dependencies of this service on other services.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1", "type_alternatives": ["object"]} | existing-native |
| [/$defs/object/properties/service_name](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/object/properties/service_name) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/native-selector.schema.json#/$defs/windows_service_object/oneOf/1/properties/service_name", "type_alternatives": ["object"]} | native-mapping-reviewed |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |

[/$defs/require](../../../proposed-schema/documentation/capabilities/windows.service.schema.json#/$defs/require): The comparison fields define the different metadata associated with a Windows service.

This includes the service name, display name, description, type, start type, current state, controls accepted, start name, path, pid, service flag, and dependencies.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
