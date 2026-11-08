# windows.regkeyeffectiverights

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/set) |
| `hive` | object | 0..1 | The hive that the registry key belongs to. | [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/hive) |
| `key` | null, object | 0..1 | Registry key to be collected. | [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/key) |
| `trustee_sid` | object | 0..1 | Unique SID associated with a user, group, system, or program (such as a Windows service). | [/$defs/object/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/trustee_sid) |
| `traversal` | not accepted | 0..1 | **Not accepted in this inline form.** Controls downward traversal from the selected hierarchy entry. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/object/properties/traversal) |

### traversal

**Semantic hold inherited from the parent field; these children do not make the parent accepted.**

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means the starting key only, and unlimited removes the depth limit. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

Validation shape: [/$defs/windows_regkeyeffectiverights_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_regkeyeffectiverights_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `hive` | array, object | 0..1 | The hive of a registry key on the machine from which to retrieve the SACL. | [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/hive) |
| `key` | array, object | 0..1 | A registry key on the machine from which to retrieve the SACL. | [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key) |
| `trustee_sid` | array, object | 0..1 | Unique SID that associated a user, group, system, or program (such as a Windows service). | [/$defs/meanings/properties/trustee_sid](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_sid) |
| `trustee_name` | array, object | 0..1 | The trustee name associated with this particular DACL. | [/$defs/meanings/properties/trustee_name](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/trustee_name) |
| `standard_delete` | array, object | 0..1 | The right to delete the object. | [/$defs/meanings/properties/standard_delete](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_delete) |
| `standard_read_control` | array, object | 0..1 | The right to read the information in the object's Security Descriptor, not including the information in the SACL. | [/$defs/meanings/properties/standard_read_control](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_read_control) |
| `standard_write_dac` | array, object | 0..1 | The right to modify the DACL in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_dac](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_dac) |
| `standard_write_owner` | array, object | 0..1 | The right to change the owner in the object's Security Descriptor. | [/$defs/meanings/properties/standard_write_owner](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/standard_write_owner) |
| `access_system_security` | array, object | 0..1 | Indicates access to a system access control list (SACL). | [/$defs/meanings/properties/access_system_security](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/access_system_security) |
| `generic_read` | array, object | 0..1 | Read access. | [/$defs/meanings/properties/generic_read](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_read) |
| `generic_write` | array, object | 0..1 | Write access. | [/$defs/meanings/properties/generic_write](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_write) |
| `generic_execute` | array, object | 0..1 | Execute access. | [/$defs/meanings/properties/generic_execute](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_execute) |
| `generic_all` | array, object | 0..1 | Read, write, and execute access. | [/$defs/meanings/properties/generic_all](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/generic_all) |
| `key_query_value` | array, object | 0..1 | Effective right to query registry values. | [/$defs/meanings/properties/key_query_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_query_value) |
| `key_set_value` | array, object | 0..1 | Effective right to set registry values. | [/$defs/meanings/properties/key_set_value](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_set_value) |
| `key_create_sub_key` | array, object | 0..1 | Effective right to create a registry subkey. | [/$defs/meanings/properties/key_create_sub_key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_sub_key) |
| `key_enumerate_sub_keys` | array, object | 0..1 | Effective right to enumerate registry subkeys. | [/$defs/meanings/properties/key_enumerate_sub_keys](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_enumerate_sub_keys) |
| `key_notify` | array, object | 0..1 | Effective right to request notifications of registry changes. | [/$defs/meanings/properties/key_notify](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_notify) |
| `key_create_link` | array, object | 0..1 | Effective right to create a registry symbolic link. | [/$defs/meanings/properties/key_create_link](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_create_link) |
| `key_wow64_64key` | array, object | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_64key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_64key) |
| `key_wow64_32key` | array, object | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_32key](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_32key) |
| `key_wow64_res` | array, object | 0..1 | **Unresolved description** | [/$defs/meanings/properties/key_wow64_res](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json#/$defs/meanings/properties/key_wow64_res) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

### Condition logic

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |

### Item existence requirement

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Existence only; there is no satisfaction operation without a comparison. | [/$defs/item_presence_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/item_presence_requirement/properties/item_requirement) |


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.regkeyeffectiverights.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`hive` | string | source-derived |
| Object.`key` | string | source-derived |
| Object.`trustee_sid` | string | source-derived |
| Item.`hive` | string | source-derived |
| Item.`key` | string | source-derived |
| Item.`trustee_sid` | string | source-derived |
| Item.`trustee_name` | string | source-derived |
| Item.`standard_delete` | boolean | source-derived |
| Item.`standard_read_control` | boolean | source-derived |
| Item.`standard_write_dac` | boolean | source-derived |
| Item.`standard_write_owner` | boolean | source-derived |
| Item.`access_system_security` | boolean | source-derived |
| Item.`generic_read` | boolean | source-derived |
| Item.`generic_write` | boolean | source-derived |
| Item.`generic_execute` | boolean | source-derived |
| Item.`generic_all` | boolean | source-derived |
| Item.`key_query_value` | boolean | native-name-proposal |
| Item.`key_set_value` | boolean | native-name-proposal |
| Item.`key_create_sub_key` | boolean | native-name-proposal |
| Item.`key_enumerate_sub_keys` | boolean | native-name-proposal |
| Item.`key_notify` | boolean | native-name-proposal |
| Item.`key_create_link` | boolean | native-name-proposal |
| Item.`key_wow64_64key` | boolean | unresolved |
| Item.`key_wow64_32key` | boolean | unresolved |
| Item.`key_wow64_res` | boolean | unresolved |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.regkeyeffectiverights.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
