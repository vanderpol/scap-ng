# asa.version

Proposed documentation; frozen 0.4.1 validation is unchanged.

The version test is used to check the version of the ASA operating system.

It is based off of the SHOW VERSION command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/asa.version.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a version test to define the different version information associated with a ASA system.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Stores the version information held within a Cisco ASA software release.

The asa_major_release, asa_minor_release and asa_build elements specify seperated parts of ASA software version information.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `asa_release` | string | 0..1 | Whole ASA version information. | [/$defs/meanings/properties/asa_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_release) |
| `asa_major_release` | version | 0..1 | Major-release component of the ASA version. | [/$defs/meanings/properties/asa_major_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_major_release) |
| `asa_minor_release` | version | 0..1 | Minor-release component of the ASA version. | [/$defs/meanings/properties/asa_minor_release](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_minor_release) |
| `asa_build` | integer | 0..1 | ASA build number. | [/$defs/meanings/properties/asa_build](../../../proposed-schema/documentation/capabilities/asa.version.schema.json#/$defs/meanings/properties/asa_build) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the version information held within a Cisco ASA software release.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/asa.version.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/asa.version.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `asa-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
