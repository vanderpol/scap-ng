# linux.inetlisteningservers — advanced constraints

Constraints below are local to the exact pointer. Alternatives and parent conditions still apply; literal alternatives are not an unconditional acceptance promise. Defaults are annotations. Array member bounds do not count mapping properties.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [schema](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#) | {} | source-derived-proposal |

[schema](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#): The inet listening servers test is used to check what applications are listening on the network.

This is limited to applications that are listening for connections that use the TCP or UDP protocols and have addresses represented as IPv4 or IPv6 addresses (AF_INET or AF_INET6).

It is generally using the parsed output of running the command netstat -tuwlnpe with root privilege.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/protocol) | {} | source-derived |

[/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/protocol): Specific transport-layer protocol, in lowercase: tcp or udp, associated with the inet listening server.

This is the transport-layer protocol, in lowercase: tcp or udp.

`protocol` defines the specific transport-layer protocol, in lowercase: tcp or udp, associated with the inet listening server.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_address) | {} | source-derived |

[/$defs/meanings/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_address): The IP address of the network interface on which the program listens.

This is the IP address associated with the inet listening server.

This is the IP address of the network interface on which the program listens.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_port) | {} | source-derived |

[/$defs/meanings/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_port): The TCP or UDP port number associated with the inet listening server.

This is the TCP or UDP port on which the program listens.

This is the TCP or UDP port number associated with the inet listening server.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/local_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_full_address) | {} | source-derived |

[/$defs/meanings/properties/local_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_full_address): The IP address and network port number associated with the inet listening server, equivalent to local_address:local_port.

This is the IP address and network port on which the program listens, equivalent to local_address:local_port.

This is the IP address and network port number associated with the inet listening server, equivalent to local_address:local_port.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/program_name](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/program_name) | {} | source-derived |

[/$defs/meanings/properties/program_name](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/program_name): The name of the communicating program.

This is the name of the communicating program.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/foreign_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_address) | {} | source-derived |
| [/$defs/meanings/properties/foreign_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_port) | {} | source-derived |

[/$defs/meanings/properties/foreign_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_port): The TCP or UDP port to which the program communicates.

This is the TCP or UDP port to which the program communicates.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/foreign_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_full_address) | {} | source-derived |
| [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/pid) | {} | source-derived |

[/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/pid): The pid is the process ID of a specific process.

This is the process ID of the process.

The process in question is that of the program communicating on the network.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/user_id) | {} | source-meaning-reviewed |

[/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/user_id): Numeric user identifier associated with the listening program.

The numeric user id, or uid, is the third column of each user's entry in /etc/passwd.

It represents the owner, and thus privilege level, of the specified program.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/capability-common.schema.json#/$defs/inline_object", "type_alternatives": ["object"]} | existing-native |

[/$defs/object](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object): An inet listening servers object consists of three entities.

The first identifies a specific IP address.

While the third identifies the protocol.

The Object is used by an inet listening servers test to define the specific protocol-address-port to be evaluated.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/protocol) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/protocol): Certain transport-layer protocol, in lowercase: tcp or udp.

`protocol` defines a certain transport-layer protocol, in lowercase: tcp or udp.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_address) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_address): The IP address of the network interface on which an application listens.

This is the IP address of the network interface on which an application listens.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/object/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_port) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/object_selector_predicate", "type_alternatives": ["object"]} | source-derived |

[/$defs/object/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_port): The TCP or UDP port on which an application would listen.

This is the TCP or UDP port on which an application would listen.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/item](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/item) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/collected-item.schema.json", "type_alternatives": ["object"]} | existing-native |

[/$defs/item](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/item): An inet listening server item stores the results of checking for network servers currently active on a system.

It holds information pertaining to a specific protocol-address-port combination.

| Pointer | Local constraints | Documentation status |
| --- | --- | --- |
| [/$defs/require](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/require) | {"validation_reference": "https://scap-ng.dev/schema/proposed/documentation/assessment-language.schema.json#/$defs/test/properties/require", "type_alternatives": ["object"]} | existing-native |
