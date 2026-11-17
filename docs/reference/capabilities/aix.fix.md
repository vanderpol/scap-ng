# aix.fix

Proposed documentation; frozen 0.4.1 validation is unchanged.

The fix test is used to check information associated with different fixes installed on the system.

The information being tested is based off the /usr/sbin/instfix -iavk command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/aix.fix.md) retain the validated encodings and any broader schema acceptance.

## Object

A fix object consists of a single apar_number field that identifies the fix to be used.

The Object is used by a fix test to define the specific fix to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object/properties/filters) |
| `apar_number` | string | 0..1 | Authorized Program Analysis Report (APAR) identifier. | [/$defs/object/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/object/properties/apar_number) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

From /usr/sbin/instfix -iavk APARNum Command.

See instfix manpage for specific fields.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `apar_number` | string | 0..1 | Authorized Program Analysis Report (APAR) identifier. | [/$defs/meanings/properties/apar_number](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/apar_number) |
| `abstract` | string | 0..1 | The abstract of an APAR. | [/$defs/meanings/properties/abstract](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/abstract) |
| `symptom` | string | 0..1 | The symptom text related to an APAR. | [/$defs/meanings/properties/symptom](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/symptom) |
| `installation_status` | string | 0..1 | The installation status of files associated with the APAR. | [/$defs/meanings/properties/installation_status](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json#/$defs/meanings/properties/installation_status) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with a specific fix installed on the system.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/aix.fix.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/aix.fix.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `aix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
