# panos.config

Proposed documentation; frozen 0.4.0 validation is unchanged.

Inspects configuration information represented by a PAN-OS XML API response. The XML response payload is rooted with a `response` element and includes device-specific information.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/panos.config.md) retain the validated encodings and any broader schema acceptance.

## Object

The response data is assumed to consist of a <response> field, with arbitrary (i.e., vendor-specific) child nodes.

The Object is used by `panos.config` to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/panos.config.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/panos.config.schema.json#/$defs/object/properties/filters) |
| `xpath` | string | 0..1 | An Xpath expression describing the text node(s) or attribute(s) to look at. | [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/panos.config.schema.json#/$defs/object/properties/xpath) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking the contents of an XML configuration.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `xpath` | string | 0..1 | An XPath expression describing the text node(s) or attribute(s) to look at. | [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/panos.config.schema.json#/$defs/meanings/properties/xpath) |
| `value_of` | 12 declared types; see details | 0..1 | The value_of field checks the value(s) of the text node(s) or attribute(s) found. | [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/panos.config.schema.json#/$defs/meanings/properties/value_of) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the XPath used and the value of this XPath.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/panos.config.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value_of` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/panos.config.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `panos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
