# macos.keychain

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `macos.keychain` is used to check the properties of the plist-style XML output from the "security show-keychain-info >keychain<" command, for reading information about keychain settings on MacOSX.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.keychain.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object/properties/filters) |
| `filepath` | string | 0..1 | The filepath of the keychain to be queried. | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/object/properties/filepath) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores results from checking the settings of a keychain.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `filepath` | string | 0..1 | The filepath of the keychain used to create the object. | [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/filepath) |
| `lock_on_sleep` | boolean | 0..1 | Whether the keychain is configured to lock when the computer sleeps. | [/$defs/meanings/properties/lock_on_sleep](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/lock_on_sleep) |
| `timeout` | integer | 0..1 | The inactivity timeout (in seconds) for the keychain, or 0 if there is no timeout. | [/$defs/meanings/properties/timeout](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json#/$defs/meanings/properties/timeout) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define a value used to evaluate the result of a specific Object item.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.keychain.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.keychain.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
