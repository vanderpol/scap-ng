# independent.environmentvariable

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `independent.environmentvariable` element is used to check an environment variable for the specified process, which is identified by its process ID, on the system .

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/independent.environmentvariable.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `independent.environmentvariable` to define the specific environment variable(s) and process IDs to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/object/properties/filters) |
| `pid` | integer | 0..1 | Process identifier for the environment being inspected. | [/$defs/object/properties/pid](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/object/properties/pid) |
| `name` | string | 0..1 | Environment variable name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores information about an environment variable, the process ID of the process from which it was retrieved, and its corresponding value.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `pid` | integer | 0..1 | Process identifier for the environment being inspected. | [/$defs/meanings/properties/pid](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/meanings/properties/pid) |
| `name` | string | 0..1 | Environment variable name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/meanings/properties/name) |
| `value` | 12 declared types; see details | 0..1 | Environment variable value. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json#/$defs/meanings/properties/value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain three entities that are used to check the name of the specified environment variable, the process ID of the process from which the environment variable was retrieved, and the value associated with the environment variable.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/independent.environmentvariable.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/independent.environmentvariable.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `independent-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
