# linux.systemdunitproperty

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.systemdunitproperty` is used to retrieve information about systemd units in form of properties.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.systemdunitproperty.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `linux.systemdunitproperty` to define the specific unit and property combination to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/set) |
| `unit` | string | 0..1 | Full systemd unit name, including its type suffix. | [/$defs/object/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/unit) |
| `property` | string | 0..1 | Systemd unit property name. | [/$defs/object/properties/property](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/object/properties/property) |

Validation shape: [/$defs/linux_systemdunitproperty_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitproperty_object/oneOf/1).

## Item

This item stores the properties and values of a systemd unit.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `unit` | string | 0..1 | Full systemd unit name, including its type suffix. | [/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/unit) |
| `property` | string | 0..1 | Systemd unit property name. | [/$defs/meanings/properties/property](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/property) |
| `value` | 12 declared types; see details | 0..1 | Value of the unit property. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json#/$defs/meanings/properties/value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields holds information about properties of a specific systemd unit.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.systemdunitproperty.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.systemdunitproperty.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
