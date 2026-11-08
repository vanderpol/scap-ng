# iosxe.interface

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/filters) |
| `name` | object | 0..1 | The interface name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
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

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |


Validation shape: [/$defs/canonical_all_items_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.interface.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.interface.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
