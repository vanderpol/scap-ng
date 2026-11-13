# macos.pwpolicy

Proposed documentation; frozen 0.4.1 validation is unchanged.

This test retrieves password policy data from the 'pwpolicy -getaccountpolicies -u username [-a authenticator] [-p authenticator_password] [-n directory_node]' output where authenticator, authenticator_password, and directory_node are optional.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.pwpolicy.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/filters) |
| `username` | string | 0..1 | User whose password policy is queried. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/username) |
| `authenticator` | string | 0..1 | Username of the authenticator. | [/$defs/object/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator) |
| `authenticator_password` | string | 0..1 | Password of the authenticator as specified by the username field. | [/$defs/object/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/authenticator_password) |
| `directory_node` | string | 0..1 | Directory-service node queried for password policy. | [/$defs/object/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/directory_node) |
| `xpath` | string | 0..1 | An XPath 1.0 expression to evaluate against the XML representation of the output generated from the pwpolicy -getaccountinfo command. | [/$defs/object/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/object/properties/xpath) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

The Item holds the password policy information for a particular user specified by the target_user element.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | string | 0..1 | User whose password policy is queried. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/username) |
| `authenticator` | string | 0..1 | Username of the authenticator. | [/$defs/meanings/properties/authenticator](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator) |
| `authenticator_password` | string | 0..1 | Password of the authenticator as specified by the authenticator field. | [/$defs/meanings/properties/authenticator_password](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/authenticator_password) |
| `directory_node` | string | 0..1 | Directory-service node queried for password policy. | [/$defs/meanings/properties/directory_node](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/directory_node) |
| `xpath` | string | 0..1 | An XPath expression describing the text node(s) or attribute(s) to look at. | [/$defs/meanings/properties/xpath](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/xpath) |
| `value_of` | 12 declared types; see details | 0..1 | The value of the preference key. | [/$defs/meanings/properties/value_of](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json#/$defs/meanings/properties/value_of) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.pwpolicy.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Item.`value_of` | string, boolean, integer, float, binary, version, ipv4, ipv6, rpm_evr, debian_evr, fileset_revision, ios_version | source-derived |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.pwpolicy.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
