# linux.systemdunitdependency

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.systemdunitdependency` is used to retrieve information about dependencies of a single systemd unit in the form of a list.

This list contains all dependencies, including transitive dependencies.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.systemdunitdependency.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `linux.systemdunitdependency` to define the specific units to check the dependencies of.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object/properties/set) |
| `unit` | string | 0..1 | Full systemd unit name, including its type suffix. | [/$defs/object/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/object/properties/unit) |

Validation shape: [/$defs/linux_systemdunitdependency_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_systemdunitdependency_object/oneOf/1).

## Item

This item stores the dependencies of the systemd unit.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `unit` | string | 0..1 | Full systemd unit name, including its type suffix. | [/$defs/meanings/properties/unit](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/unit) |
| `dependency` | string | 0..1 | Name of a unit on which the selected unit depends. | [/$defs/meanings/properties/dependency](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json#/$defs/meanings/properties/dependency) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields holds dependencies of a specific systemd unit.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.systemdunitdependency.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.systemdunitdependency.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
