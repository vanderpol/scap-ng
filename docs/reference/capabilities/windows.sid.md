# windows.sid

Proposed documentation; frozen 0.4.0 validation is unchanged.

The SID test is used to check properties associated with the specified SID.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.sid.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `windows.sid` to define the object set, in this case a set of SIDs (identified by name), to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/filters) |
| `trustee_name` | string | 0..1 | Unique name that associated a particular SID. | [/$defs/object/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/trustee_name) |
| `include_group` | boolean | 0..1 | Whether matching groups are included. | [/$defs/object/properties/include_group](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/include_group) |
| `resolve_group` | boolean | 0..1 | Whether group membership is recursively resolved. | [/$defs/object/properties/resolve_group](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/object/properties/resolve_group) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `trustee_name` | string | 0..1 | The trustee name associated with a particular SID. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_name) |
| `trustee_sid` | string | 0..1 | The security identifier (SID) of the specified trustee name. | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_sid) |
| `trustee_domain` | string | 0..1 | The domain of the specified trustee name. | [/$defs/meanings/properties/trustee_domain](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json#/$defs/meanings/properties/trustee_domain) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a Windows trustee (identified by name).

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.sid.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`include_group` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`resolve_group` | {"required": true, "type": "boolean"} | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.sid.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
