# windows.wuaupdatesearcher

Proposed documentation; frozen 0.4.1 validation is unchanged.

The `windows.wuaupdatesearcher` is used to evaluate patch level in a Windows environment utilizing the WUA (Windows Update Agent) interface.

The content source is specific to a given system evaluating `windows.wuaupdatesearcher` and thus is not defined by this test.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.wuaupdatesearcher.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `windows.wuaupdatesearcher` to define the specific search criteria to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/filters) |
| `search_criteria` | string | 0..1 | Search criteria to use when generating a search result. | [/$defs/object/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/search_criteria) |
| `include_superseded_updates` | boolean | 0..1 | Whether updates superseded by other matching updates are included. | [/$defs/object/properties/include_superseded_updates](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/object/properties/include_superseded_updates) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This information is related to the current patch level in a Windows environment.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `search_criteria` | string | 0..1 | String to examine the search criteria that was used to generate the object set. | [/$defs/meanings/properties/search_criteria](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/search_criteria) |
| `update_id` | string | 0..1 | The update_id enity specifies a string that represents a revision-independent identifier of an update. | [/$defs/meanings/properties/update_id](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/update_id) |
| `title` | string | 0..1 | Short text provided from Micrsoft related to the update ID | [/$defs/meanings/properties/title](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/title) |
| `support_url` | string | 0..1 | The support field is the URL provideded by Microsoft related to this update ID | [/$defs/meanings/properties/support_url](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/support_url) |
| `is_installed` | boolean | 0..1 | Whether the update is installed. | [/$defs/meanings/properties/is_installed](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_installed) |
| `is_hidden` | boolean | 0..1 | Whether the update is hidden. | [/$defs/meanings/properties/is_hidden](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/is_hidden) |
| `msrc_severity` | string | 0..1 | Microsoft Security Response Center severity rating. | [/$defs/meanings/properties/msrc_severity](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/msrc_severity) |
| `last_deployment_change_time` | string | 0..1 | The last published date of the update, provided by Microsoft related to this update ID | [/$defs/meanings/properties/last_deployment_change_time](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/last_deployment_change_time) |
| `source` | string | 0..1 | Where the update information was obtained. | [/$defs/meanings/properties/source](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/source) |
| `days_since_source_modified` | integer | 0..1 | Age of the update-search source file in days. | [/$defs/meanings/properties/days_since_source_modified](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json#/$defs/meanings/properties/days_since_source_modified) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the search criteria and updated id.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.wuaupdatesearcher.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`include_superseded_updates` | {"required": true, "type": "boolean"} | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.wuaupdatesearcher.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
