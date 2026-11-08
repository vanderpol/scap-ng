# windows.regkeyeffectiverights

Proposed documentation; frozen 0.4.0 validation is unchanged.

Inspects effective access-right fields for a Windows registry key and trustee.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.regkeyeffectiverights.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by a registry key effective rights test to define the objects used to evalutate against the specified state.

An Object is defined as a combination of a Windows registry and trustee SID.

The key field represents the registry key to be evaluated while the trustee SID represents the account (SID) to check effective rights of.

In addition, a number of behaviors may be provided that help guide the collection of objects.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/set) |
| `hive` | string | 0..1 | The hive that the registry key belongs to. | [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/hive) |
| `key` | string | 0..1 | Registry key to be collected. | [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/key) |
| `trustee_sid` | string | 0..1 | Unique SID associated with a user, group, system, or program (such as a Windows service). | [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/trustee_sid) |
| `traversal` | not accepted | 0..1 | **Not accepted in this inline form.** Controls downward traversal from the selected hierarchy entry. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/traversal) |

### traversal

**Semantic hold inherited from the parent field; these children do not make the parent accepted.**

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means the starting key only, and unlimited removes the depth limit. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

Validation shape: [/$defs/windows_regkeyeffectiverights_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1).

## Item

This item stores the effective rights of a registry key that a discretionary access control list (DACL) structure grants to a specified trustee.

The trustee's effective rights are determined checking all access-allowed and access-denied access control entries (ACEs) in the DACL.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `hive` | string | 0..1 | The hive of a registry key on the machine from which to retrieve the SACL. | [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/hive) |
| `key` | string | 0..1 | A registry key on the machine from which to retrieve the SACL. | [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key) |
| `trustee_sid` | string | 0..1 | Unique SID that associated a user, group, system, or program (such as a Windows service). | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) |
| `trustee_name` | string | 0..1 | The trustee name associated with this particular DACL. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) |
| `standard_delete` | boolean | 0..1 | The right to delete the object. | [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) |
| `standard_read_control` | boolean | 0..1 | The right to read the information in the object's Security Descriptor, not including the information in the SACL. | [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) |
| `standard_write_dac` | boolean | 0..1 | The right to modify the DACL in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) |
| `standard_write_owner` | boolean | 0..1 | The right to change the owner in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) |
| `access_system_security` | boolean | 0..1 | Indicates access to a system access control list (SACL). | [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) |
| `generic_read` | boolean | 0..1 | Read access. | [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_read) |
| `generic_write` | boolean | 0..1 | Write access. | [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_write) |
| `generic_execute` | boolean | 0..1 | Execute access. | [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) |
| `generic_all` | boolean | 0..1 | Read, write, and execute access. | [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_all) |
| `key_query_value` | boolean | 0..1 | Effective right to query registry values. | [/$defs/meanings/properties/key_query_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_query_value) |
| `key_set_value` | boolean | 0..1 | Effective right to set registry values. | [/$defs/meanings/properties/key_set_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_set_value) |
| `key_create_sub_key` | boolean | 0..1 | Effective right to create a registry subkey. | [/$defs/meanings/properties/key_create_sub_key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_sub_key) |
| `key_enumerate_sub_keys` | boolean | 0..1 | Effective right to enumerate registry subkeys. | [/$defs/meanings/properties/key_enumerate_sub_keys](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_enumerate_sub_keys) |
| `key_notify` | boolean | 0..1 | Effective right to request notifications of registry changes. | [/$defs/meanings/properties/key_notify](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_notify) |
| `key_create_link` | boolean | 0..1 | Effective right to create a registry symbolic link. | [/$defs/meanings/properties/key_create_link](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_link) |
| `key_wow64_64key` | boolean | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_64key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_64key) |
| `key_wow64_32key` | boolean | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_32key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_32key) |
| `key_wow64_res` | boolean | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_res](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_res) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.regkeyeffectiverights.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
