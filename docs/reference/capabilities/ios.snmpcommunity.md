# ios.snmpcommunity

Proposed documentation; frozen 0.4.0 validation is unchanged.

The snmpcommunity test is used to check the properties of specific output lines from an SNMP configuration.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/ios.snmpcommunity.md) retain the validated encodings and any broader schema acceptance.

## Object

An snmpcommunity object consists of a community name field to be tested.

The Object is used by an snmpcommunity test to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object/properties/filters) |
| `name` | string | 0..1 | The SNMP community name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores information about an SNMP community configuration in IOS.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | The SNMP community name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/name) |
| `view` | string | 0..1 | The view that restricts the OIDs of this community. | [/$defs/meanings/properties/view](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/view) |
| `mode` | string | 0..1 | The read-write privileges of the community. | [/$defs/meanings/properties/mode](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/mode) |
| `ipv4_acl` | string | 0..1 | The IPv4 ACL name applied to the community. | [/$defs/meanings/properties/ipv4_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv4_acl) |
| `ipv6_acl` | string | 0..1 | The IPv6 ACL name applied to the community. | [/$defs/meanings/properties/ipv6_acl](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json#/$defs/meanings/properties/ipv6_acl) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the community name and the corresponding options.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/ios.snmpcommunity.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/ios.snmpcommunity.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `ios-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
