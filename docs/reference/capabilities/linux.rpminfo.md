# linux.rpminfo

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `linux.rpminfo` is used to check the RPM header information for a given RPM package.

**Contract status: unresolved.** Package database failures, duplicate package instances and requested-file-path result granularity require native runtime evidence.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/linux.rpminfo.md) retain the validated encodings and any broader schema acceptance.

## Object

A rpm info object consists of a single name field that identifies the package being checked.

The Object is used by a rpm info test to define the object to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/filters) |
| `package_name` | string | 0..1 | Installed RPM package name. | [/$defs/object/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/package_name) |
| `include_file_paths` | boolean | 0..1 | Whether to request the paths of files owned by the package. | [/$defs/object/properties/include_file_paths](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/object/properties/include_file_paths) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores rpm info.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `package_name` | string | 0..1 | Installed RPM package name. | [/$defs/meanings/properties/package_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/package_name) |
| `architecture` | string | 0..1 | Package architecture. | [/$defs/meanings/properties/architecture](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/architecture) |
| `epoch` | integer, string | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/epoch) |
| `release` | string, version | 0..1 | Package release component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/release) |
| `version` | string, version | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/version) |
| `evr` | rpm_evr | 0..1 | Combined epoch, version, and release. | [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/evr) |
| `signature_key_id` | string | 0..1 | Identifier of the package signing key. | [/$defs/meanings/properties/signature_key_id](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/signature_key_id) |
| `extended_name` | string | 0..1 | Package name including epoch, version, release, and architecture. | [/$defs/meanings/properties/extended_name](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/extended_name) |
| `full_path` | string | 0..1 | Path of a file owned by the package. | [/$defs/meanings/properties/full_path](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json#/$defs/meanings/properties/full_path) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/linux.rpminfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`include_file_paths` | {"required": true, "type": "boolean"} | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.rpminfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
