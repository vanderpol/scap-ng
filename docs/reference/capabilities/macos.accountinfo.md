# macos.accountinfo

Proposed documentation; frozen 0.4.1 validation is unchanged.

User account information (username, uid, gid, etc.) See netinfo(5) for field information, niutil(1) for retrieving it.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/macos.accountinfo.md) retain the validated encodings and any broader schema acceptance.

## Object

An Object consists of a single username that identifies the account from which to gather information.

The Object is used by `macos.accountinfo` to define the object(s) to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/object/properties/filters) |
| `username` | string | 0..1 | The user of the account to gather information from. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/object/properties/username) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

This item stores user account information (username, uid, gid, etc.).

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | string | 0..1 | The user of the account to gather information from. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/username) |
| `password` | string | 0..1 | Obfuscated (*****) or encrypted password for this user. | [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/password) |
| `uid` | integer | 0..1 | Numeric user identifier. | [/$defs/meanings/properties/uid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/uid) |
| `gid` | integer | 0..1 | Group ID of this account. | [/$defs/meanings/properties/gid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/gid) |
| `realname` | string | 0..1 | Real-name field of the user account. | [/$defs/meanings/properties/realname](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/realname) |
| `home_dir` | string | 0..1 | The home directory for this user account. | [/$defs/meanings/properties/home_dir](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/home_dir) |
| `login_shell` | string | 0..1 | The login shell for this user account. | [/$defs/meanings/properties/login_shell](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/login_shell) |
| `generated_uid` | string | 0..1 | The generated UID for this user account. | [/$defs/meanings/properties/generated_uid](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json#/$defs/meanings/properties/generated_uid) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/macos.accountinfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/macos.accountinfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `macos-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
