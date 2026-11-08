# windows.registry

Proposed documentation; frozen 0.4.0 validation is unchanged.

The registry test is used to check metadata associated with Windows registry key.

**Contract status: unresolved.** Registry-view selection, traversal contract differences, inaccessible keys, value conversion and collection-error aggregation remain unresolved. See issue #29 and the existing semantic research.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.registry.md) retain the validated encodings and any broader schema acceptance.

## Object

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/set) |
| `hive` | string | 0..1 | Registry hive containing the key. | [/$defs/object/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/hive) |
| `key` | string | 0..1 | Key path relative to the hive. | [/$defs/object/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/key) |
| `name` | string | 0..1 | Registry value name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/name) |
| `traversal` | not accepted | 0..1 | **Not accepted in this inline form.** Controls downward traversal from the selected hierarchy entry. | [/$defs/object/properties/traversal](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/object/properties/traversal) |

### traversal

**Semantic hold inherited from the parent field; these children do not make the parent accepted.**

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `max_depth` | integer, string | 1..1 (required) | Maximum downward hierarchy recursion depth; 0 means the starting key only, and unlimited removes the depth limit. | [/$defs/hierarchy_traversal/properties/max_depth](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/hierarchy_traversal/properties/max_depth) |

Validation shape: [/$defs/windows_registry_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/windows_registry_object/oneOf/1).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `hive` | string | 0..1 | Registry hive containing the key. | [/$defs/meanings/properties/hive](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/hive) |
| `key` | string | 0..1 | Key path relative to the hive. | [/$defs/meanings/properties/key](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/key) |
| `name` | string | 0..1 | Registry value name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/name) |
| `last_write_time` | integer | 0..1 | Last recorded write time for the key. | [/$defs/meanings/properties/last_write_time](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/last_write_time) |
| `type` | string | 0..1 | Native registry value kind. | [/$defs/meanings/properties/type](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/type) |
| `value` | binary, integer, string, version | 0..1 | Data stored in the registry value. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/value) |
| `expanded_value` | string | 0..1 | Registry string after environment-variable expansion. | [/$defs/meanings/properties/expanded_value](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json#/$defs/meanings/properties/expanded_value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields define the different metadata associated with a Windows registry key.

This includes the hive, key, name, type, and value.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


Validation shape: [/$defs/test/properties/require](../../../proposed-schema/documentation/assessment-language.schema.json#/$defs/test/properties/require).

## Advanced constraints and evidence

[Local schema constraints](../advanced/windows.registry.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.registry.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
