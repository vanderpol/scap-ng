# iosxe.snmpgroup

Proposed documentation; frozen 0.4.1 validation is unchanged.

The snmpgroup test is used to check the properties of specific output lines from an SNMP group configuration.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/iosxe.snmpgroup.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by an snmpgroup test to define the object to be evaluated.

A snmpgroup object consists of a name field that is the name of the SNMP group to be tested.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object/properties/filters) |
| `name` | string | 0..1 | The SNMP group name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores information about an SNMP group configuration in IOS.

That information includes the group name, the SNMP version, the IPv4 or IPv6 ACL it is applied toand the read, write and/or notify views applied to the group.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | The SNMP group name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/name) |
| `version` | string | 0..1 | The SNMP version of the group. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/version) |
| `snmpv3_sec_level` | string | 0..1 | The SNMPv3 security configured for the group. | [/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/snmpv3_sec_level) |
| `ipv4_acl` | string | 0..1 | The IPv4 ACL name applied to the group. | [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv4_acl) |
| `ipv6_acl` | string | 0..1 | The IPv6 ACL name applied to the group. | [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/ipv6_acl) |
| `read_view` | string | 0..1 | The SNMP read view applied to the group. | [/$defs/meanings/properties/read_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/read_view) |
| `write_view` | string | 0..1 | The SNMP write view applied to the group. | [/$defs/meanings/properties/write_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/write_view) |
| `notify_view` | string | 0..1 | The SNMP notify view applied to the group. | [/$defs/meanings/properties/notify_view](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json#/$defs/meanings/properties/notify_view) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the user name and the corresponding options.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.snmpgroup.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.snmpgroup.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
