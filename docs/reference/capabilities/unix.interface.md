# unix.interface

Proposed documentation; frozen 0.4.0 validation is unchanged.

The interface test enumerates various attributes about the interfaces on a system.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.interface.md) retain the validated encodings and any broader schema acceptance.

## Object

An interface object consists of a single name field that identifies which interface is being specified.

The Object is used by an interface test to define the specific interfaces(s) to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/set) |
| `name` | string | 0..1 | Interface (eth0, eth1, fw0, etc.) name to check. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/unix_interface_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_interface_object/oneOf/1).

## Item

The interface item holds information about the interfaces on a system.

Each interface item contains name and address information as well as any associated flags.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | Interface (eth0, eth1, fw0, etc.) name to check. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/name) |
| `type` | string | 0..1 | Type of interface. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/type) |
| `hardware_addr` | string | 0..1 | Hardware or MAC address of the physical network card. | [/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/hardware_addr) |
| `inet_addr` | string | 0..1 | The IP address of the interface. | [/$defs/meanings/properties/inet_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/inet_addr) |
| `broadcast_addr` | string | 0..1 | The broadcast IP address for this interface's network. | [/$defs/meanings/properties/broadcast_addr](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/broadcast_addr) |
| `netmask` | string | 0..1 | The bitmask used to calculate the interface's IP network. | [/$defs/meanings/properties/netmask](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/netmask) |
| `flag` | string | 0..1 | Interface flag line, which generally contains flags like "UP" to denote an active interface, "PROMISC" to note that the interface is listening for Ethernet frames not specifically addressed to it, and others. | [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json#/$defs/meanings/properties/flag) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields enumerates the different properties associate with a Unix interface.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.interface.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.interface.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
