# windows.passwordpolicy

Proposed documentation; frozen 0.4.1 validation is unchanged.

The password policy test is used to check specific policy associated with passwords.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.passwordpolicy.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a password policy test to define those objects to evaluated based on a specified state.

Therefore, there are no child entities defined.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/object/properties/filters) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

Specific policy items associated with passwords.

It is important to note that these policies are specific to certain versions of Windows.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_passwd_age` | integer | 0..1 | Maximum password age. | [/$defs/meanings/properties/max_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/max_passwd_age) |
| `min_passwd_age` | integer | 0..1 | Minimum password age. | [/$defs/meanings/properties/min_passwd_age](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_age) |
| `min_passwd_len` | integer | 0..1 | Minimum password length. | [/$defs/meanings/properties/min_passwd_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/min_passwd_len) |
| `password_hist_len` | integer | 0..1 | Number of previous passwords retained in password history. | [/$defs/meanings/properties/password_hist_len](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/password_hist_len) |
| `password_complexity` | boolean | 0..1 | Whether the operating-system password complexity policy is enabled. | [/$defs/meanings/properties/password_complexity](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/password_complexity) |
| `reversible_encryption` | boolean | 0..1 | Whether reversible password encryption is enabled. | [/$defs/meanings/properties/reversible_encryption](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/reversible_encryption) |
| `anonymous_name_lookup` | boolean | 0..1 | Whether anonymous SID/name translation is allowed. | [/$defs/meanings/properties/anonymous_name_lookup](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json#/$defs/meanings/properties/anonymous_name_lookup) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.passwordpolicy.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.passwordpolicy.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
