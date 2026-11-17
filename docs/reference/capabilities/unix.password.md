# unix.password

Proposed documentation; frozen 0.4.1 validation is unchanged.

The password test is used to check metadata associated with the UNIX password file, of the sort returned by the passwd command.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/unix.password.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a password test to define the object to be evaluated.

A password object consists of a single username field that identifies the user(s) whose password is to be evaluated.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object/properties/set) |
| `username` | string | 0..1 | The user(s) account whose password is to be evaluated. | [/$defs/object/properties/username](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/object/properties/username) |

Validation shape: [/$defs/unix_password_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/unix_password_object/oneOf/1).

## Item

/etc/passwd.

See passwd(4).

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `username` | string | 0..1 | The UNIX account name. | [/$defs/meanings/properties/username](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/username) |
| `password` | string | 0..1 | The encrypted version of the user's password. | [/$defs/meanings/properties/password](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/password) |
| `user_id` | integer, string | 0..1 | The numeric user id, or uid, is the third column of each user's entry in /etc/passwd. | [/$defs/meanings/properties/user_id](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/user_id) |
| `group_id` | integer, string | 0..1 | The id of the primary UNIX group the user belongs to. | [/$defs/meanings/properties/group_id](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/group_id) |
| `gcos` | string | 0..1 | The GECOS (or GCOS) field from /etc/passwd; typically contains the user's full name. | [/$defs/meanings/properties/gcos](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/gcos) |
| `home_dir` | string | 0..1 | The user's home directory. | [/$defs/meanings/properties/home_dir](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/home_dir) |
| `login_shell` | string | 0..1 | The user's shell program. | [/$defs/meanings/properties/login_shell](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/login_shell) |
| `last_login` | integer | 0..1 | The date and time when the last login occurred. | [/$defs/meanings/properties/last_login](../../../proposed-schema/documentation/capabilities/unix.password.schema.json#/$defs/meanings/properties/last_login) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different information associated with the system passwords.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/unix.password.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/unix.password.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `unix-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
