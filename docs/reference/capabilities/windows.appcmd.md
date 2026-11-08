# windows.appcmd

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.appcmd` is one of two tests used to gather Microsoft Internet Information Server (IIS) configuration settings.

It can gather Apppool, Site, and VDir settings.

Whereas certain website (Site) and virtual directory (VDir) data gathering are found in both or either test.

Meaning to be able capture larger sets of Site or VDir data both tests may be needed to gather all data.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.appcmd.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used to gather Apppool, Site, and VDir IIS settings.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/object/properties/filters) |
| `identifier_type` | string | 0..1 | The identifier_type defines the identifier type (Apppool, Site, or VDir). | [/$defs/object/properties/identifier_type](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/object/properties/identifier_type) |
| `identifier` | string | 0..1 | The identifier defines information about the location of the found result (apppool name, vdir name or site name). | [/$defs/object/properties/identifier](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/object/properties/identifier) |
| `parameter` | string | 0..1 | The parameter value defines the location of the setting. | [/$defs/object/properties/parameter](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/object/properties/parameter) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item is used to gather Apppool, Site, and VDir IIS settings.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `identifier_type` | string | 0..1 | The identifier_type defines the identifier type (Apppool, Site, or VDir). | [/$defs/meanings/properties/identifier_type](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/meanings/properties/identifier_type) |
| `identifier` | string | 0..1 | The identifier defines information about the location of the found result (such as apppool name or site name). | [/$defs/meanings/properties/identifier](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/meanings/properties/identifier) |
| `parameter` | string | 0..1 | The parameter value defines the location of the setting. | [/$defs/meanings/properties/parameter](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/meanings/properties/parameter) |
| `result` | 12 declared types; see details | 0..1 | The value of the collected setting. | [/$defs/meanings/properties/result](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json#/$defs/meanings/properties/result) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields is used to gather Apppool, Site, and VDir IIS settings.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.appcmd.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`result` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.appcmd.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
