# panos.version

Proposed documentation; frozen 0.4.1 validation is unchanged.

Inspects version information represented by a PAN-OS XML API response. The XML response payload is rooted with a `response` element and includes device-specific information.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/panos.version.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `panos.version` to define the different version information associated with an PANOS system.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item holds information about the version of a PAN-OS system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `major_version` | integer | 0..1 | Used to check the major version piece of the version string. | [/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/major_version) |
| `minor_version` | integer | 0..1 | Used to check the minor version piece of the version string. | [/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/minor_version) |
| `release` | integer | 0..1 | Used to check the release piece of the version string. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/release) |
| `hotfix` | integer | 0..1 | Used to check the hotfix piece of the version string. | [/$defs/meanings/properties/hotfix](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/hotfix) |
| `version_string` | 12 declared types; see details | 0..1 | Used to check the sw-version raw string output of a PAN-OS XML API request. | [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/version_string) |
| `model_name` | string | 0..1 | Used to check the model string output of a PAN-OS XML API request. | [/$defs/meanings/properties/model_name](../../../proposed-schema/documentation/capabilities/panos.version.schema.json#/$defs/meanings/properties/model_name) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the version information held within a PANOS Release.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/panos.version.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`version_string` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/panos.version.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `panos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
