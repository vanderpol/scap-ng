# linux.dpkginfo

Proposed documentation; frozen 0.4.0 validation is unchanged.

**Contract status: unresolved.** Native collection boundaries, field multiplicity, missing values and error propagation are not established by field descriptions. Legacy source documentation is not a native execution contract.

Field meanings below are documentation proposals derived from the pinned sources. Reviewed wording and unresolved entries are identified in the [coverage ledger](../coverage.json) and schema annotations.

Occurrences indicate how many times a field may appear within its parent object; a field may separately contain multiple values. Object tables describe inline forms; named Object references and Set composition use the [shared collection grammar](../shared/capability-common.md). Item fields use the shared [typed-value wrapper](../shared/result-types.md); a field may contain one wrapper or an array. Capability-specific units, multiplicity and error behavior require evidence.

## Object

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `capability` | string | 0..1 | Optional for inline Objects only, whose capability is inherited from the enclosing Test; when supplied it must agree with the Test capability. | [/$defs/object/properties/capability](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object/properties/capability) |
| `filters` | array | 0..1 | Leaf Object post-collection Filters; observed Items, not selectors or compliance States. | [/$defs/object/properties/filters](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object/properties/filters) |
| `set` | object | 0..1 | Combines Object collections using union, intersection, or difference. | [/$defs/object/properties/set](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object/properties/set) |
| `name` | object | 0..1 | Installed package name. | [/$defs/object/properties/name](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/object/properties/name) |

Validation shape: [/$defs/linux_dpkginfo_object/oneOf/1](../../../proposed-schema/documentation/native-selector.schema.json#/$defs/linux_dpkginfo_object/oneOf/1).

## Item

| Field | Schema type | Occurrences | Description | Details |
| --- | --- | --- | --- | --- |
| `name` | array, object | 0..1 | Installed package name. | [/$defs/meanings/properties/name](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/name) |
| `arch` | array, object | 0..1 | Package architecture. | [/$defs/meanings/properties/arch](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/arch) |
| `epoch` | array, object | 0..1 | Package epoch. | [/$defs/meanings/properties/epoch](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/epoch) |
| `release` | array, object | 0..1 | Package revision component. | [/$defs/meanings/properties/release](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/release) |
| `version` | array, object | 0..1 | Package version component. | [/$defs/meanings/properties/version](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/version) |
| `evr` | array, object | 0..1 | Combined epoch, upstream version, and Debian revision. | [/$defs/meanings/properties/evr](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json#/$defs/meanings/properties/evr) |

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

[Local schema constraints](../advanced/linux.dpkginfo.md) retain allowed literals, defaults and bounds outside the basic field tables.

| Role / field | Declared datatype or collection shape | Annotation status |
| --- | --- | --- |
| Object.`name` | string | source-meaning-reviewed |
| Item.`name` | string | source-meaning-reviewed |
| Item.`arch` | string | source-meaning-reviewed |
| Item.`epoch` | string, integer | source-meaning-reviewed |
| Item.`release` | string, version | source-meaning-reviewed |
| Item.`version` | string, version | source-meaning-reviewed |
| Item.`evr` | rpm_evr, debian_evr | source-meaning-reviewed |

See the [schema](../../../proposed-schema/documentation/capabilities/linux.dpkginfo.schema.json) for exact description owners, native datatype declarations and collection-parameter declarations. Declarations are documentation annotations; they add no datatype or required-field restriction. Read [shared collection and evaluation schemas](../shared/assessment-language.md) for syntax; compilation and schema acceptance do not establish scanner equivalence.

Historical source: OVAL 5.12.3, commit `2f140ee5c5dd1ed9606fcd5afc301f6baeb48706`, `linux-definitions-schema.xsd`; native field mapping and source pointers are recorded in the schema. Legacy runtime behavior is not adopted. Support classification: **supported**.
