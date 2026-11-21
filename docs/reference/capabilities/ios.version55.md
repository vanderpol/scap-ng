# ios.version55

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `ios.version55` capability checks the Cisco IOS operating-system version using the version55 state fields.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/ios.version55.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is a singleton source for the current Cisco IOS software version; it has no child selectors.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item holds the version information collected from the Cisco IOS system.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `version_string` | string | 0..1 | The entire IOS version string, for example, '03.13.02.S'. | [/$defs/meanings/properties/version_string](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/version_string) |
| `major_version` | integer | 0..1 | The major version piece of the version string. | [/$defs/meanings/properties/major_version](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/major_version) |
| `release` | integer | 0..1 | The minor release piece of the version string. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/release) |
| `rebuild` | integer | 0..1 | The rebuild piece of the version string. | [/$defs/meanings/properties/rebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/rebuild) |
| `train_identifier` | string | 0..1 | The train piece of the version string. | [/$defs/meanings/properties/train_identifier](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/train_identifier) |
| `minor_version` | integer | 0..1 | The minor version piece of the IOS version string. | [/$defs/meanings/properties/minor_version](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/minor_version) |
| `subrebuild` | string | 0..1 | The optional alphabetic subrebuild component of the IOS version string. | [/$defs/meanings/properties/subrebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/subrebuild) |
| `mainline_rebuild` | string | 0..1 | The optional mainline rebuild component of the IOS version string. | [/$defs/meanings/properties/mainline_rebuild](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json#/$defs/meanings/properties/mainline_rebuild) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Require compares the typed IOS version fields while preserving each source field datatype.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/ios.version55.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/ios.version55.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `ios-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
