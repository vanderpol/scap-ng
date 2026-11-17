# unix.shadow

Proposed documentation; frozen 0.4.1 validation is unchanged.

The shadow test is used to check information from the /etc/shadow file for a specific user.

This file contains a user's password, but also their password aging and lockout information.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.shadow.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a shadow test to define the shadow file to be evaluated.

A shdow object consists of a single user field that identifies the username associted with the shadow file.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/set) |
| `username` | string | 0..1 | UNIX account name. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/object/properties/username) |

Validation shape: [/$defs/unix_shadow_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_shadow_object/oneOf/1).

## Item

/etc/shadow.

See shadow(4).

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | string | 0..1 | UNIX account name. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/username) |
| `password` | string | 0..1 | The encrypted version of the user's password. | [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/password) |
| `chg_lst` | integer, string | 0..1 | Date of the last password change. | [/$defs/meanings/properties/chg_lst](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_lst) |
| `chg_allow` | integer, string | 0..1 | Minimum interval between password changes. | [/$defs/meanings/properties/chg_allow](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_allow) |
| `chg_req` | integer, string | 0..1 | Maximum password age. | [/$defs/meanings/properties/chg_req](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/chg_req) |
| `exp_warn` | integer, string | 0..1 | Warning interval before password expiration. | [/$defs/meanings/properties/exp_warn](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_warn) |
| `exp_inact` | integer, string | 0..1 | Inactivity interval after password expiration. | [/$defs/meanings/properties/exp_inact](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_inact) |
| `exp_date` | integer, string | 0..1 | Password expiration date. | [/$defs/meanings/properties/exp_date](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/exp_date) |
| `flag` | integer, string | 0..1 | A numeric reserved field that the shadow file may use in the future. | [/$defs/meanings/properties/flag](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/flag) |
| `encrypt_method` | string | 0..1 | Method that is used for hashing passwords. | [/$defs/meanings/properties/encrypt_method](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json#/$defs/meanings/properties/encrypt_method) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.shadow.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.shadow.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
