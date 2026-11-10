# windows.cmdlet

Proposed documentation; frozen 0.4.0 validation is unchanged.

The `windows.cmdlet` is used to leverage a PowerShell cmdlet to check a Windows system.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Value datatypes are declarations; [advanced constraints](../advanced/windows.cmdlet.md) retain the validated encodings and any broader schema acceptance.

## Object

The Object is used by `windows.cmdlet` to identify the set of cmdlets to use and the parameters to provide to them for checking the state of a system.

The NoLanguage mode ensures that scripts that need to be evaluated are not allowed in the runspace.

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/filters) |
| `module_name` | string | 0..1 | PowerShell module name. | [/$defs/object/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_name) |
| `module_id` | string | 0..1 | PowerShell module GUID. | [/$defs/object/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_id) |
| `module_version` | string | 0..1 | Quoted lexical version value. | [/$defs/object/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/module_version) |
| `verb` | string | 0..1 | PowerShell cmdlet verb. | [/$defs/object/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/verb) |
| `noun` | string | 0..1 | PowerShell cmdlet noun. | [/$defs/object/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/noun) |
| `parameters` | record | 0..1 | Named parameters supplied to the cmdlet. | [/$defs/object/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/parameters) |
| `select` | record | 0..1 | Output properties selected from the cmdlet result. | [/$defs/object/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/object/properties/select) |

Validation shape: [/$defs/inline_object](../../../proposed-schema/documentation/capability-common.schema.json#/$defs/inline_object).

## Item

| Field | Value datatype | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `module_name` | string | 0..1 | The name of the module that contains the cmdlet. | [/$defs/meanings/properties/module_name](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_name) |
| `module_id` | string | 0..1 | The globally unique identifier for the module. | [/$defs/meanings/properties/module_id](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_id) |
| `module_version` | version | 0..1 | The version of the module that contains the cmdlet in the form of MAJOR.MINOR. | [/$defs/meanings/properties/module_version](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/module_version) |
| `verb` | string | 0..1 | The cmdlet verb. | [/$defs/meanings/properties/verb](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/verb) |
| `noun` | string | 0..1 | The cmdlet noun. | [/$defs/meanings/properties/noun](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/noun) |
| `parameters` | record | 0..1 | Named parameters supplied to the cmdlet. | [/$defs/meanings/properties/parameters](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/parameters) |
| `select` | record | 0..1 | Output properties selected from the cmdlet result. | [/$defs/meanings/properties/select](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/select) |
| `value` | record | 0..1 | Output fields returned by the cmdlet. | [/$defs/meanings/properties/value](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json#/$defs/meanings/properties/value) |

Validation shape: [schema](../../../proposed-schema/documentation/collected-item.schema.json#).

## Require

The comparison fields allows for assertions about the presence of PowerShell cmdlet related properties and values obtained from a cmdlet.

Use the Item fields above with the [shared Require forms and count policies](../shared/assessment-language.md). Capability-specific comparison-domain declarations, where different, are listed below.


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

See the [schema](../../../proposed-schema/documentation/capabilities/windows.cmdlet.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `windows-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
