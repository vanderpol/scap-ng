# macos.installhistory

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `macos.installhistory` is used to inspect the install history (SPInstallHistoryDataType) section of the system_profiler command output.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.installhistory.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object/properties/filters) |
| `name` | string | 0..1 | Installed software title. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item stores information retrieved from the system_profiler about installed software on the device.

Information is collected from the target endpoint using the "system_profiler SPInstallHistoryDataType" command and output values are parsed from the XML output.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | string | 0..1 | Installed software title. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/name) |
| `install_version` | version | 0..1 | Version of an installed software item. | [/$defs/meanings/properties/install_version](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_version) |
| `install_date` | integer | 0..1 | Date that a software item was installed on the system. | [/$defs/meanings/properties/install_date](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/install_date) |
| `package_source` | string | 0..1 | Source type of an installed software item. | [/$defs/meanings/properties/package_source](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json#/$defs/meanings/properties/package_source) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields contain entities that are used to check against installed software.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.installhistory.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.installhistory.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
