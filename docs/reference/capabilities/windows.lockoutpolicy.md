# windows.lockoutpolicy

Proposed documentation; frozen 0.4.0 validation is unchanged.

The lockout policy test enumerates various attributes associated with lockout information for users and global groups in the security database.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.lockoutpolicy.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a lockout policy test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The lockoutpolicy item enumerates various attributes associated with lockout information for users and global groups in the security database.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `force_logoff` | integer | 0..1 | Delay between the end of valid logon time and forced network logoff. | [/$defs/meanings/properties/force_logoff](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/force_logoff) |
| `lockout_duration` | integer | 0..1 | Duration of account lockout. | [/$defs/meanings/properties/lockout_duration](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_duration) |
| `lockout_observation_window` | integer | 0..1 | Interval over which failed logon attempts are counted. | [/$defs/meanings/properties/lockout_observation_window](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_observation_window) |
| `lockout_threshold` | integer | 0..1 | Number of invalid password authentications that triggers account lockout. | [/$defs/meanings/properties/lockout_threshold](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json#/$defs/meanings/properties/lockout_threshold) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.lockoutpolicy.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.lockoutpolicy.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
