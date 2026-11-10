# iosxe.interface

Proposed documentation; frozen 0.4.0 validation is unchanged.

The interface test is used to check for the existence of a particular interface on the Cisco IOS-XE device.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/iosxe.interface.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `iosxe.interface` to define the object to be evaluated.

An Object consists of a name field that is the name of the IOS-XE interface to be tested.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/filters) |
| `name` | object | 0..1 | The interface name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item represents an IOS-XE interface and its configuration options.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | array, object | 0..1 | The interface name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/name) |
| `ip_directed_broadcast` | array, object | 0..1 | Directed broadcast command enabled on the interface. | [/$defs/meanings/properties/ip_directed_broadcast](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ip_directed_broadcast) |
| `proxy_arp` | array, object | 0..1 | Proxy arp enabled on the interface. | [/$defs/meanings/properties/proxy_arp](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/proxy_arp) |
| `shutdown` | array, object | 0..1 | Interface is shut down. | [/$defs/meanings/properties/shutdown](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/shutdown) |
| `hardware_addr` | array, object | 0..1 | The interface hardware (MAC) address. | [/$defs/meanings/properties/hardware_addr](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/hardware_addr) |
| `ipv4_address` | array, object | 0..1 | The interface IPv4 address and mask. | [/$defs/meanings/properties/ipv4_address](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv4_address) |
| `ipv6_address` | array, object | 0..1 | The interface IPv6 address and mask. | [/$defs/meanings/properties/ipv6_address](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv6_address) |
| `ipv4_access_list` | array, object | 0..1 | The ingress or egress IPv4 ACL name applied on the interface. | [/$defs/meanings/properties/ipv4_access_list](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv4_access_list) |
| `ipv6_access_list` | array, object | 0..1 | The ingress or egress IPv6 ACL name applied on the interface. | [/$defs/meanings/properties/ipv6_access_list](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv6_access_list) |
| `crypto_map` | array, object | 0..1 | The crypto map name applied to the interface. | [/$defs/meanings/properties/crypto_map](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/crypto_map) |
| `ipv4_urpf_command` | array, object | 0..1 | The IPv4 uRPF command under the interface. | [/$defs/meanings/properties/ipv4_urpf_command](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv4_urpf_command) |
| `ipv6_urpf_command` | array, object | 0..1 | The IPv6 uRPF command under the interface. | [/$defs/meanings/properties/ipv6_urpf_command](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/ipv6_urpf_command) |
| `switchport_trunk_encapsulation` | array, object | 0..1 | The switchport trunk encapsulation option configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_trunk_encapsulation](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_trunk_encapsulation) |
| `switchport_mode` | array, object | 0..1 | The switchport mode option configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_mode](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_mode) |
| `switchport_native_vlan` | array, object | 0..1 | The trunk native vlan configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_native_vlan](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_native_vlan) |
| `switchport_access_vlan` | array, object | 0..1 | The access vlan configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_access_vlan](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_access_vlan) |
| `switchport_trunked_vlans` | array, object | 0..1 | The vlans that are trunked configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_trunked_vlans](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_trunked_vlans) |
| `switchport_pruned_vlans` | array, object | 0..1 | The vlans that are pruned from the trunk (if applicable). | [/$defs/meanings/properties/switchport_pruned_vlans](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_pruned_vlans) |
| `switchport_port_security` | array, object | 0..1 | The switchport port-security commands configured on the interface (if applicable). | [/$defs/meanings/properties/switchport_port_security](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/meanings/properties/switchport_port_security) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the name, status, and address information about the interface.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.interface.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
