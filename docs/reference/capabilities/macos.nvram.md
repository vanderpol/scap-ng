# macos.nvram

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `macos.nvram` is used to check the binary values of firmware variables, via the command 'nvram -x -p' or 'nvram -x <variable_name>'.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.nvram.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `macos.nvram` to define the service domain to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json#/$defs/object/properties/filters) |
| `variable` | string | 0..1 | The name of the firmware variable being queried. | [/$defs/object/properties/variable](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json#/$defs/object/properties/variable) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking a firmware variable via an Object.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `variable` | string | 0..1 | The name of the firmware variable that was queried. | [/$defs/meanings/properties/variable](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json#/$defs/meanings/properties/variable) |
| `value` | binary | 0..1 | The binary value of the firmware variable. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json#/$defs/meanings/properties/value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define a value used to evaluate the result of a specific Object item.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.nvram.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.nvram.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
