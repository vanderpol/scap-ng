# ios.routingprotocolauthintf

Proposed documentation; frozen 0.4.1 validation is unchanged.

The routing protocol authentication interface test is used to check the properties of routing protocol authentication configured under interfaces in IOS.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/ios.routingprotocolauthintf.md) retain the validated encodings and any broader schema acceptance.

## Object

A routingprotocolauthintf object consists of an interface and the routing protocol that is authenticated field.

The Object is used by a routingprotocolauthintf test to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/filters) |
| `interface` | string | 0..1 | The interface name. | [/$defs/object/properties/interface](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/interface) |
| `protocol` | string | 0..1 | The routing protocol. | [/$defs/object/properties/protocol](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/object/properties/protocol) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores information for routing protocol authentication configured under specific interfaces.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `interface` | string | 0..1 | The interface name. | [/$defs/meanings/properties/interface](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/interface) |
| `protocol` | string | 0..1 | The routing protocol. | [/$defs/meanings/properties/protocol](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/protocol) |
| `id` | integer | 0..1 | The routing protocol id, if applicable. | [/$defs/meanings/properties/id](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/id) |
| `auth_type` | string | 0..1 | The routing protocol authentication type. | [/$defs/meanings/properties/auth_type](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/auth_type) |
| `ospf_area` | integer, ipv4 | 0..1 | The OSPF area that is authenticated, if applicable. | [/$defs/meanings/properties/ospf_area](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/ospf_area) |
| `key_chain` | string | 0..1 | The name of the key chain, if applicable. | [/$defs/meanings/properties/key_chain](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json#/$defs/meanings/properties/key_chain) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the interface, the protocol, the id, the authentication type, the ospf area, the key chain command and the corresponding config lines.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/ios.routingprotocolauthintf.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/ios.routingprotocolauthintf.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `ios-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
