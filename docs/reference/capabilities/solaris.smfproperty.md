# solaris.smfproperty

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `solaris.smfproperty` is used to check the value of properties associated with SMF services.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/solaris.smfproperty.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a SMF property test to define the SMF property items to be evaluated based on the specified states.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/filters) |
| `service` | string | 0..1 | The SMF service on the system. | [/$defs/object/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/service) |
| `instance` | string | 0..1 | The instance of an SMF service which represents a specific configuration of a service. | [/$defs/object/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/instance) |
| `property` | string | 0..1 | The name of the property associated with an SMF service. | [/$defs/object/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/object/properties/property) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores the properties and values of an SMF service.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `service` | string | 0..1 | The SMF service on the system. | [/$defs/meanings/properties/service](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/service) |
| `instance` | string | 0..1 | The instance of an SMF service which represents a specific configuration of a service. | [/$defs/meanings/properties/instance](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/instance) |
| `property` | string | 0..1 | The name of the property associated with an SMF service. | [/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/property) |
| `fmri` | string | 0..1 | The Fault Management Resource Identifier (FMRI) of the SMF service which uniquely identifies the service on the system. | [/$defs/meanings/properties/fmri](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/fmri) |
| `value` | 12 declared types; see details | 0..1 | The value of the property associated with an SMF service. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json#/$defs/meanings/properties/value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields specifies the values of properties associated with SMF services.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/solaris.smfproperty.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/solaris.smfproperty.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `solaris-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
