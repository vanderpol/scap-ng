# iosxe.snmphost

Proposed documentation; frozen 0.4.1 validation is unchanged.

The snmphost test is used to check the properties of specific output lines from an SNMP configuration.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/iosxe.snmphost.md) retain the validated encodings and any broader schema acceptance.

## Object

A snmphost object consists of a host field that is the host of the 'snmp host' IOS-XE command to be tested.

The Object is used by an snmphost test to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object/properties/filters) |
| `host` | string | 0..1 | The SNMP host address or hostname. | [/$defs/object/properties/host](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/object/properties/host) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores information about the SNMP host configuration in IOS.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `host` | string | 0..1 | The SNMP host address or hostname. | [/$defs/meanings/properties/host](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/host) |
| `community_or_user` | string | 0..1 | The community string or SNMPv3 user configured for the host. | [/$defs/meanings/properties/community_or_user](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/community_or_user) |
| `version` | string | 0..1 | The SNMP version. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/version) |
| `snmpv3_sec_level` | string | 0..1 | The SNMPv3 security configured for the host. | [/$defs/meanings/properties/snmpv3_sec_level](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/snmpv3_sec_level) |
| `traps` | string | 0..1 | The SNMP traps configured. | [/$defs/meanings/properties/traps](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json#/$defs/meanings/properties/traps) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the host and the corresponding options.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/iosxe.snmphost.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/iosxe.snmphost.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `iosxe-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
