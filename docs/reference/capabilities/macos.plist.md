# macos.plist

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `macos.plist` is used to check the value(s) associated with property list preference keys.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.plist.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `macos.plist` to define the preference keys to collect and where to look for them.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/filters) |
| `app_id` | string | 0..1 | The unique application identifier that specifies the application to use when looking up the preference key (e.g. com.apple.Safari). | [/$defs/object/properties/app_id](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/app_id) |
| `filepath` | string | 0..1 | The absolute path to a plist file (e.g. /Library/Preferences/com.apple.TimeMachine.plist). | [/$defs/object/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/filepath) |
| `xpath` | string | 0..1 | An XPath 1.0 expression to evaluate against the XML representation of the plist file specified by the filename or app_id field. | [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/object/properties/xpath) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item stores results from checking the contents of the XML representation of a plist file.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `app_id` | string | 0..1 | The unique application identifier that specifies the application to use when looking up the preference key (e.g. com.apple.Safari). | [/$defs/meanings/properties/app_id](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/app_id) |
| `filepath` | string | 0..1 | The absolute path to a plist file (e.g. ~/Library/Preferences/com.apple.Safari.plist). | [/$defs/meanings/properties/filepath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/filepath) |
| `xpath` | string | 0..1 | An XPath expression describing the text node(s) or attribute(s) to look at. | [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/xpath) |
| `value_of` | 12 declared types; see details | 0..1 | The value of the preference key. | [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json#/$defs/meanings/properties/value_of) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

This includes the preference key, application identifier, filepath, type, as well as the preference key's value.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.plist.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value_of` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.plist.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
