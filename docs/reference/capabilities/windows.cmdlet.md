# windows.cmdlet

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/filters) |
| `module_name` | See schema | 0..1 | PowerShell module name. | [/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_name) |
| `module_id` | See schema | 0..1 | PowerShell module GUID. | [/$defs/object/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_id) |
| `module_version` | See schema | 0..1 | Quoted lexical version value. | [/$defs/object/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_version) |
| `verb` | See schema | 0..1 | PowerShell cmdlet verb. | [/$defs/object/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/verb) |
| `noun` | See schema | 0..1 | PowerShell cmdlet noun. | [/$defs/object/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/noun) |
| `parameters` | See schema | 0..1 | Named parameters supplied to the cmdlet. | [/$defs/object/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/parameters) |
| `select` | See schema | 0..1 | Output properties selected from the cmdlet result. | [/$defs/object/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/select) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `module_name` | array, object | 0..1 | The name of the module that contains the cmdlet. | [/$defs/meanings/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_name) |
| `module_id` | array, object | 0..1 | The globally unique identifier for the module. | [/$defs/meanings/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_id) |
| `module_version` | array, object | 0..1 | The version of the module that contains the cmdlet in the form of MAJOR.MINOR. | [/$defs/meanings/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_version) |
| `verb` | array, object | 0..1 | The cmdlet verb. | [/$defs/meanings/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/verb) |
| `noun` | array, object | 0..1 | The cmdlet noun. | [/$defs/meanings/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/noun) |
| `parameters` | array, object | 0..1 | Named parameters supplied to the cmdlet. | [/$defs/meanings/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/parameters) |
| `select` | array, object | 0..1 | Output properties selected from the cmdlet result. | [/$defs/meanings/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/select) |
| `value` | array, object | 0..1 | Output fields returned by the cmdlet. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/value) |

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

[Local schema constraints](../advanced/windows.cmdlet.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`module_name` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`module_id` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`module_version` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`verb` | {"allow_variable": true, "enum": ["Approve", "Assert", "Compare", "Confirm", "Find", "Get", "Import", "Measure", "Read", "Request", "Resolve", "Search", "Select", "Show", "Test", "Trace", "Watch"], "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`noun` | {"allow_variable": true, "required": true, "type": "string"} | native-mapping-reviewed |
| Object.`parameters` | {"required": true} | source-meaning-reviewed |
| Object.`select` | {"required": true} | source-meaning-reviewed |
| Item.`module_name` | string | source-derived |
| Item.`module_id` | string | source-derived |
| Item.`module_version` | version | source-derived |
| Item.`verb` | string | source-derived |
| Item.`noun` | string | source-derived |
| Item.`parameters` | record | source-meaning-reviewed |
| Item.`select` | record | source-meaning-reviewed |
| Item.`value` | record | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
