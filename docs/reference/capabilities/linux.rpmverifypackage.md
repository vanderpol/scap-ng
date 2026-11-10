# linux.rpmverifypackage

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.rpmverifypackage` is used to verify the integrity of installed RPMs.

This test aligns with the rpm -V command for verifying RPMs.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.rpmverifypackage.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/filters) |
| `name` | string | 0..1 | Package name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/name) |
| `epoch` | integer, string | 0..1 | Package epoch. | [/$defs/object/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/epoch) |
| `version` | string, version | 0..1 | Package version component. | [/$defs/object/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/version) |
| `release` | string, version | 0..1 | Package release component. | [/$defs/object/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/release) |
| `arch` | string | 0..1 | Package architecture. | [/$defs/object/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/arch) |
| `skip_dependencies` | boolean | 0..1 | Whether RPM dependency verification is skipped. | [/$defs/object/properties/skip_dependencies](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/skip_dependencies) |
| `skip_scripts` | boolean | 0..1 | Whether RPM verification scripts are skipped. | [/$defs/object/properties/skip_scripts](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/object/properties/skip_scripts) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores the rpm verification results of an rpm similar to what is produced by the rpm -V command.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | Package name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/name) |
| `epoch` | integer, string | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/epoch) |
| `version` | string, version | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/version) |
| `release` | string, version | 0..1 | Package release component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/release) |
| `arch` | string | 0..1 | Package architecture. | [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/arch) |
| `extended_name` | string | 0..1 | Package name including epoch, version, release, and architecture. | [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/extended_name) |
| `dependency_check_passed` | boolean | 0..1 | The dependency_check_passed field indicates whether or not the dependency check passed. | [/$defs/meanings/properties/dependency_check_passed](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/dependency_check_passed) |
| `verification_script_successful` | boolean | 0..1 | The verification_script_successful field indicates whether or not the verification script executed successfully. | [/$defs/meanings/properties/verification_script_successful](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json#/$defs/meanings/properties/verification_script_successful) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.rpmverifypackage.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`skip_dependencies` | {"required": true, "type": "boolean"} | native-mapping-reviewed |
| Object.`skip_scripts` | {"required": true, "type": "boolean"} | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.rpmverifypackage.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
