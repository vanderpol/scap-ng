# unix.symlink

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `unix.symlink` is used to obtain canonical path information for symbolic links.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.symlink.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `unix.symlink` to define the object to be evaluated.

An Object consists of a filepath field that contains the path to a symbolic link file.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object/properties/filters) |
| `full_path` | string | 0..1 | The filepath for the symbolic link. | [/$defs/object/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/object/properties/full_path) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `full_path` | string | 0..1 | The filepath used to create the object. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/full_path) |
| `canonical_path` | string | 0..1 | The canonical path for the target of a symbolic link file specified by the filepath. | [/$defs/meanings/properties/canonical_path](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json#/$defs/meanings/properties/canonical_path) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define a value used to evaluate the result of a specific Object item.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.symlink.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.symlink.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
