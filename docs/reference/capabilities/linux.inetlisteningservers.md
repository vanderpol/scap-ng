# linux.inetlisteningservers

Proposed documentation; frozen 0.4.1 validation is unchanged.

The inet listening servers test is used to check what applications are listening on the network.

This is limited to applications that are listening for connections that use the TCP or UDP protocols and have addresses represented as IPv4 or IPv6 addresses (AF_INET or AF_INET6).

It is generally using the parsed output of running the command netstat -tuwlnpe with root privilege.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.inetlisteningservers.md) retain the validated encodings and any broader schema acceptance.

## Object

An inet listening servers object consists of three entities.

The first identifies a specific IP address.

While the third identifies the protocol.

The Object is used by an inet listening servers test to define the specific protocol-address-port to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/filters) |
| `protocol` | string | 0..1 | Certain transport-layer protocol, in lowercase: tcp or udp. | [/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/protocol) |
| `local_address` | string | 0..1 | The IP address of the network interface on which an application listens. | [/$defs/object/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_address) |
| `local_port` | integer | 0..1 | The TCP or UDP port on which an application would listen. | [/$defs/object/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/object/properties/local_port) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

An inet listening server item stores the results of checking for network servers currently active on a system.

It holds information pertaining to a specific protocol-address-port combination.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `protocol` | string | 0..1 | Specific transport-layer protocol, in lowercase: tcp or udp, associated with the inet listening server. | [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/protocol) |
| `local_address` | string | 0..1 | The IP address of the network interface on which the program listens. | [/$defs/meanings/properties/local_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_address) |
| `local_port` | integer | 0..1 | The TCP or UDP port number associated with the inet listening server. | [/$defs/meanings/properties/local_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_port) |
| `local_full_address` | string | 0..1 | The IP address and network port number associated with the inet listening server, equivalent to local_address:local_port. | [/$defs/meanings/properties/local_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/local_full_address) |
| `program_name` | string | 0..1 | The name of the communicating program. | [/$defs/meanings/properties/program_name](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/program_name) |
| `foreign_address` | string | 0..1 | The IP address with which the program is communicating, or with which it will communicate, in the case of a listening server. | [/$defs/meanings/properties/foreign_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_address) |
| `foreign_port` | integer | 0..1 | The TCP or UDP port to which the program communicates. | [/$defs/meanings/properties/foreign_port](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_port) |
| `foreign_full_address` | string | 0..1 | The IP address and network port to which the program is communicating or will accept communications from, equivalent to foreign_address:foreign_port. | [/$defs/meanings/properties/foreign_full_address](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/foreign_full_address) |
| `pid` | integer | 0..1 | The pid is the process ID of a specific process. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/pid) |
| `user_id` | integer | 0..1 | Numeric user identifier associated with the listening program. | [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json#/$defs/meanings/properties/user_id) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the local address, foreign address, port information, and process id.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.inetlisteningservers.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.inetlisteningservers.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
