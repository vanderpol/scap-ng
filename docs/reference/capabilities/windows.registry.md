# windows.registry

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Registry-view selection, traversal contract differences, inaccessible keys, value conversion and collection-error aggregation remain unresolved. See issue #29 and the existing semantic research.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/set) |
| `hive` | object | 0..1 | Registry hive containing the key. | [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/hive) |
| `key` | null, object | 0..1 | Key path relative to the hive. | [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/key) |
| `name` | null, object | 0..1 | Registry value name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/name) |
| `traversal` | not accepted | 0..1 | **Not accepted in this inline form.** Controls downward traversal from the selected hierarchy entry. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/traversal) |

### traversal

**Semantic hold inherited from the parent field; these children do not make the parent accepted.**

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means starting key only and unlimited maps OVAL -1. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

Validation shape: [/$defs/windows_registry_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `hive` | array, object | 0..1 | Registry hive containing the key. | [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/hive) |
| `key` | array, object | 0..1 | Key path relative to the hive. | [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/key) |
| `name` | array, object | 0..1 | Registry value name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/name) |
| `last_write_time` | array, object | 0..1 | Last recorded write time for the key. | [/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/last_write_time) |
| `type` | array, object | 0..1 | Native registry value kind. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/type) |
| `value` | array, object | 0..1 | Data stored in the registry value. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/value) |
| `expanded_value` | array, object | 0..1 | Registry string after environment-variable expansion. | [/$defs/meanings/properties/expanded_value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/expanded_value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

Field meanings are shared with Item; comparisons use the [native Require grammar](../shared/assessment-language.md). This is a field vocabulary, not a whitelist or a promise that every field is collected.

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `item_requirement` | object | 1..1 (required) | Sets how many Items must be found and how many must satisfy the comparison. | [/$defs/canonical_all_items_requirement/properties/item_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/item_requirement) |
| `field_requirement` | object | 1..1 (required) | Sets the shared value-count requirements for fields in this comparison. | [/$defs/canonical_all_items_requirement/properties/field_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/field_requirement) |
| `fields` | object | Conditional (at most 1) | Requires all listed field conditions to hold for an Item. | [/$defs/canonical_all_items_requirement/properties/fields](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/fields) |
| `and` | array | Conditional (at most 1) | Groups child conditions using logical AND. | [/$defs/canonical_all_items_requirement/properties/and](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/and) |
| `or` | array | Conditional (at most 1) | Groups child conditions using logical OR. | [/$defs/canonical_all_items_requirement/properties/or](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/or) |
| `one` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/one](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/one) |
| `xor` | array | Conditional (at most 1) | **Unresolved description** | [/$defs/canonical_all_items_requirement/properties/xor](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement/properties/xor) |


Validation shape: [/$defs/canonical_all_items_requirement](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/canonical_all_items_requirement).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.registry.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`hive` | string | native-mapping-reviewed |
| Object.`key` | string | native-mapping-reviewed |
| Object.`name` | string | native-mapping-reviewed |
| Item.`hive` | string | native-mapping-reviewed |
| Item.`key` | string | native-mapping-reviewed |
| Item.`name` | string | native-mapping-reviewed |
| Item.`last_write_time` | integer | native-mapping-reviewed |
| Item.`type` | string | native-mapping-reviewed |
| Item.`value` | string, integer, binary, version | native-mapping-reviewed |
| Item.`expanded_value` | string | native-mapping-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
