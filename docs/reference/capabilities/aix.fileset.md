# aix.fileset

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `aix.fileset` is used to check information associated with different filesets installed on the system.

The information used by this test is modeled after the /usr/bin/lslpp -l command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/aix.fileset.md) retain the validated encodings and any broader schema acceptance.

## Object

An Object consists of a single flstinst field that identifies the fileset to be used.

The Object is used by `aix.fileset` to define the fileset to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object/properties/filters) |
| `flstinst` | string | 0..1 | Fileset name. | [/$defs/object/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/object/properties/flstinst) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Output of /usr/bin/lslpp -l FilesetName.

See lslpp manpage for specific fields.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `flstinst` | string | 0..1 | Fileset name. | [/$defs/meanings/properties/flstinst](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/flstinst) |
| `level` | version | 0..1 | Fileset maintenance level. | [/$defs/meanings/properties/level](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/level) |
| `state` | string | 0..1 | Installation state of the fileset. | [/$defs/meanings/properties/state](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/state) |
| `description` | string | 0..1 | Short description of a fileset. | [/$defs/meanings/properties/description](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json#/$defs/meanings/properties/description) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with filesets installed on the system.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/aix.fileset.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/aix.fileset.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `aix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
